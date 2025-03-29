from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Avg
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Student, Course, Transaction, Block, User
from .forms import (
    StudentForm, CourseForm, TransactionForm, CustomAuthenticationForm, UserRegistrationForm, TransactionApprovalForm
)
from .blockchain_logic import BlockchainManager
from django.contrib.auth import get_user_model
import math

# Hàm kiểm tra quyền Admin
def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

def is_pdt_staff(user):
    return user.is_authenticated and user.user_type in ['admin', 'staff']

# Các view xác thực
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Kiểm tra xem người dùng có phải nhân viên phòng đào tạo hoặc admin không
            if not is_pdt_staff(user):
                messages.error(request, 'Bạn không có quyền truy cập hệ thống phòng đào tạo!')
                return redirect('login')
                
            login(request, user)
            messages.success(request, f'Xin chào, {user.username}!')
            return redirect('home')
        else:
            # Thêm thông báo lỗi cụ thể
            if 'username' in form.errors:
                messages.error(request, 'Tài khoản không tồn tại trong hệ thống!')
            elif 'password' in form.errors:
                messages.error(request, 'Mật khẩu không chính xác!')
            else:
                messages.error(request, 'Đăng nhập không thành công. Vui lòng kiểm tra lại thông tin đăng nhập!')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'blockchain_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')

@user_passes_test(is_admin)
def register_staff(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tài khoản nhân viên mới đã được tạo thành công!')
            return redirect('staff_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'blockchain_app/register_staff.html', {'form': form})

@user_passes_test(is_admin)
def staff_list(request):
    staff = User.objects.all()
    return render(request, 'blockchain_app/staff_list.html', {'staff': staff})

# Các view chính
@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def home(request):
    blocks = Block.objects.all().order_by('-index')
    pending_transactions = BlockchainManager.get_pending_transactions()
    approved_transactions = BlockchainManager.get_approved_unmined_transactions()
    
    context = {
        'blocks': blocks,
        'pending_transactions': pending_transactions,
        'approved_transactions': approved_transactions,
        'total_blocks': blocks.count(),
        'total_transactions': Transaction.objects.count(),
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'average_score': Transaction.objects.aggregate(Avg('score'))['score__avg'],
        'blocks_by_difficulty': Block.objects.values('difficulty').annotate(count=Count('id')),
        'latest_blocks': Block.objects.order_by('-timestamp')[:5],
    }
    return render(request, 'blockchain_app/home.html', context)

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def transaction_list(request):
    # Kiểm tra và cập nhật các giao dịch quá hạn
    check_expired_transactions()
    
    pending_transactions = BlockchainManager.get_pending_transactions()
    approved_transactions = Transaction.objects.filter(status='approved')
    rejected_transactions = Transaction.objects.filter(status='rejected')
    expired_transactions = Transaction.objects.filter(status='expired')
    
    context = {
        'pending_transactions': pending_transactions,
        'approved_transactions': approved_transactions,
        'rejected_transactions': rejected_transactions,
        'expired_transactions': expired_transactions,
    }
    return render(request, 'blockchain_app/transaction_list.html', context)

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def approve_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    
    # Kiểm tra xem giao dịch đã quá hạn chưa
    if transaction.is_expired() and transaction.status == 'pending':
        transaction.status = 'expired'
        transaction.save()
        messages.error(request, 'Giao dịch này đã quá hạn phê duyệt (3 ngày). Vui lòng yêu cầu giảng viên gửi lại.')
        return redirect('transaction_list')
    
    User = get_user_model()
    
    # Chỉ lấy nhân viên staff, không bao gồm admin
    total_staff = User.objects.filter(user_type='staff').count()
    
    # Đổi ngưỡng đồng thuận thành 51%
    consensus_threshold = math.ceil(total_staff * 0.51)  # Làm tròn lên để đảm bảo đa số
    
    if request.method == 'POST':
        form = TransactionApprovalForm(request.POST, instance=transaction)
        if form.is_valid():
            # Lấy dữ liệu từ form
            new_status = form.cleaned_data.get('status')
            
            # Lấy private key từ form (nếu có)
            private_key = form.cleaned_data.get('private_key')
            
            # Xử lý từ chối điểm
            if new_status == 'rejected':
                tx = form.save(commit=False)
                tx.rejected_by = request.user
                tx.rejection_time = timezone.now()
                tx.status = 'rejected'
                tx.save()
                
                # Ký giao dịch từ chối nếu có private key
                if private_key:
                    try:
                        tx.sign_transaction(private_key, 'approver')
                    except Exception as e:
                        messages.warning(request, f"Đã từ chối điểm nhưng có lỗi khi ký: {str(e)}")
                
                tx = form.save(commit=False)
                tx.approved_by = request.user
                tx.approval_time = timezone.now()
                tx.status = 'approved'
                tx.save()
                messages.success(request, 'Với quyền admin, bạn đã phê duyệt trực tiếp điểm số này!')
                return redirect('transaction_list')
                
            # Kiểm tra xem đã đạt đồng thuận chưa (chỉ tính staff)
            approval_count = transaction.approving_staff.filter(user_type='staff').count()
            if approval_count >= consensus_threshold:
                tx = form.save(commit=False)
                tx.approved_by = request.user  # Người hoàn tất quá trình phê duyệt
                tx.approval_time = timezone.now()
                tx.status = 'approved'
                tx.save()
                messages.success(request, f'Đạt đồng thuận! {approval_count}/{total_staff} nhân viên đã phê duyệt (>51%). Điểm số được xác nhận!')
            else:
                messages.info(request, f'Đã ghi nhận phê duyệt của bạn. Hiện tại: {approval_count}/{total_staff} phê duyệt (cần ít nhất {consensus_threshold}).')
            
            return redirect('transaction_list')
    else:
        form = TransactionApprovalForm(instance=transaction)
    
    # Hiển thị thông tin về staff đã phê duyệt (chỉ hiển thị staff, không hiển thị admin)
    approving_staff = transaction.approving_staff.filter(user_type='staff')
    remaining_staff = User.objects.filter(user_type='staff').exclude(id__in=approving_staff.values_list('id', flat=True))
    
    # Kiểm tra xem người dùng hiện tại đã duyệt chưa
    user_has_approved = request.user in transaction.approving_staff.all()
    
    # Tính thời gian còn lại
    time_remaining = None
    if transaction.deadline:
        now = timezone.now()
        if now < transaction.deadline:
            time_delta = transaction.deadline - now
            days = time_delta.days
            hours, remainder = divmod(time_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            time_remaining = f"{days} ngày, {hours} giờ, {minutes} phút"
    
    context = {
        'form': form,
        'transaction': transaction,
        'approving_staff': approving_staff,
        'remaining_staff': remaining_staff,
        'approval_count': approving_staff.count(),
        'total_staff': total_staff,
        'consensus_threshold': consensus_threshold,
        'is_admin': request.user.user_type == 'admin',
        'time_remaining': time_remaining,
        'deadline': transaction.deadline,
        'user_has_approved': user_has_approved,  # Thêm biến này
    }
    return render(request, 'blockchain_app/approve_transaction.html', context)

# Thêm hàm kiểm tra giao dịch quá hạn
def check_expired_transactions():
    """Kiểm tra và cập nhật trạng thái các giao dịch quá hạn"""
    now = timezone.now()
    expired_transactions = Transaction.objects.filter(
        status='pending',
        deadline__lt=now  # Lấy các giao dịch có deadline đã qua
    )
    
    count = expired_transactions.count()
    if count > 0:
        expired_transactions.update(status='expired')
        return count
    return 0

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def mine_block(request):
    if request.method == 'POST':
        # Sử dụng độ khó cố định thay vì từ form
        difficulty = 4  # Mức độ khó vừa phải - cân bằng giữa bảo mật và hiệu suất
        approved_transactions = BlockchainManager.get_approved_unmined_transactions()
        
        if not approved_transactions:
            messages.warning(request, 'Không có điểm đã duyệt nào để xác nhận. Vui lòng duyệt điểm trước.')
            return redirect('mine_block')
        
        latest_block = Block.objects.order_by('-index').first()
        index = 1 if not latest_block else latest_block.index + 1
        previous_hash = '0' if not latest_block else latest_block.hash
        
        # Use _ to indicate we're intentionally not using the return value
        _ = BlockchainManager.mine_block(
            index=index,
            transactions=approved_transactions,
            previous_hash=previous_hash,
            difficulty=difficulty
        )
        
        # Mark transactions as mined
        approved_transactions.update(is_mined=True)
        
        messages.success(request, f'Đã xác nhận thành công {approved_transactions.count()} điểm. Điểm số đã được lưu trữ an toàn và không thể thay đổi.')
        return redirect('home')
    
    context = {
        'approved_transactions': BlockchainManager.get_approved_unmined_transactions(),
    }
    return render(request, 'blockchain_app/mine_block.html', context)

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def verify_chain(request):
    is_valid, message = BlockchainManager.verify_chain()
    if is_valid:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('home')

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def student_list(request):
    students = Student.objects.annotate(
        transaction_count=Count('transaction'),
        average_score=Avg('transaction__score')
    )
    context = {
        'students': students,
    }
    return render(request, 'blockchain_app/student_list.html', context)

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sinh viên đã được thêm thành công!')
            return redirect('student_list')
    else:
        form = StudentForm()
    
    context = {
        'form': form,
    }
    return render(request, 'blockchain_app/add_student.html', context)

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def course_list(request):
    courses = Course.objects.annotate(
        transaction_count=Count('transaction'),
        average_score=Avg('transaction__score')
    )
    context = {
        'courses': courses,
    }
    return render(request, 'blockchain_app/course_list.html', context)

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Môn học đã được thêm thành công!')
            return redirect('course_list')
    else:
        form = CourseForm()
    
    context = {
        'form': form,
    }
    return render(request, 'blockchain_app/add_course.html', context)

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def statistics(request):
    context = {
        'total_blocks': Block.objects.count(),
        'total_transactions': Transaction.objects.count(),
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'average_score': Transaction.objects.aggregate(Avg('score'))['score__avg'],
        'blocks_by_difficulty': Block.objects.values('difficulty').annotate(count=Count('id')),
        'latest_blocks': Block.objects.order_by('-timestamp')[:5],
    }
    return render(request, 'blockchain_app/statistics.html', context)

@login_required
@user_passes_test(is_pdt_staff, login_url='login')
def add_transaction(request):
    """Thêm điểm mới cho sinh viên"""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            # Lưu form nhưng chưa commit để thêm thông tin người tạo
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            
            messages.success(request, f"Đã nhập điểm {transaction.score} cho sinh viên {transaction.student.name}, môn {transaction.course.name}!")
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    
    # Lấy điểm đang chờ duyệt gần đây
    pending_transactions = Transaction.objects.filter(
        status='pending'
    ).order_by('-timestamp')[:5]
    
    context = {
        'form': form,
        'pending_transactions': pending_transactions,
    }
    return render(request, 'blockchain_app/add_transaction.html', context)

@login_required
def manage_keys(request):
    """Trang quản lý khóa của người dùng"""
    if request.method == 'POST' and 'generate_keys' in request.POST:
        # Tạo cặp khóa mới
        private_key = request.user.generate_keypair()
        
        # Hiển thị khóa riêng tư cho người dùng để lưu (chỉ hiển thị một lần)
        context = {
            'private_key': private_key,
            'public_key': request.user.public_key,
            'key_generated': True
        }
        return render(request, 'blockchain_app/manage_keys.html', context)
    
    context = {
        'public_key': request.user.public_key,
        'has_keys': bool(request.user.public_key)
    }
    return render(request, 'blockchain_app/manage_keys.html', context)
