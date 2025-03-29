from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg, Max, Min
from django.http import JsonResponse
from django.contrib import messages

from blockchain_app.models import Transaction, Student, Course
from teacher_app.forms import TeacherTransactionForm  # Chỉ giữ import của TeacherTransactionForm

# Thêm imports cho login
from django.contrib.auth import login, logout
from blockchain_app.forms import CustomAuthenticationForm

# Hàm kiểm tra người dùng là giảng viên hoặc admin
def is_teacher_or_admin(user):
    return user.user_type in ['teacher', 'admin']

# Login view riêng cho teacher_app
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Kiểm tra xem người dùng có phải giảng viên hoặc admin không
            if not is_teacher_or_admin(user):
                messages.error(request, 'Bạn không có quyền truy cập hệ thống giảng viên!')
                return redirect('login')
            
            login(request, user)
            messages.success(request, f'Xin chào, {user.username}!')
            return redirect('teacher_home')
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
    
    return render(request, 'teacher_app/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')

@login_required
@user_passes_test(is_teacher_or_admin, login_url='login')
def teacher_home(request):
    """Trang chủ cho giảng viên"""
    # Lấy thống kê điểm số
    total_scores = Transaction.objects.filter(created_by=request.user).count()
    pending_scores = Transaction.objects.filter(created_by=request.user, status='pending').count()
    approved_scores = Transaction.objects.filter(created_by=request.user, status='approved').count()
    rejected_scores = Transaction.objects.filter(created_by=request.user, status='rejected').count()
    
    # Lấy điểm đã nhập gần đây
    recent_scores = Transaction.objects.filter(created_by=request.user).order_by('-timestamp')[:10]
    
    context = {
        'total_scores': total_scores,
        'pending_scores': pending_scores,
        'approved_scores': approved_scores,
        'rejected_scores': rejected_scores,
        'recent_scores': recent_scores,
    }
    return render(request, 'teacher_app/home.html', context)

@login_required
@user_passes_test(is_teacher_or_admin, login_url='login')
def add_score(request):
    """Thêm điểm mới cho sinh viên"""
    # Xử lý form pre-selected nếu có từ url parameters
    initial_data = {}
    if 'student' in request.GET:
        try:
            student_id = int(request.GET.get('student'))
            initial_data['student'] = student_id
        except (ValueError, TypeError):
            pass
            
    if 'course' in request.GET:
        try:
            course_id = int(request.GET.get('course'))
            initial_data['course'] = course_id
        except (ValueError, TypeError):
            pass
    
    if request.method == 'POST':
        form = TeacherTransactionForm(request.POST)
        if form.is_valid():
            # Lấy private_key từ form nhưng không lưu vào database
            private_key = form.cleaned_data.pop('private_key')
            
            # Lưu form nhưng chưa commit để thêm thông tin người tạo
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            
            # Kiểm tra xem người dùng có khóa công khai không
            if not request.user.public_key:
                messages.error(request, "Bạn chưa thiết lập cặp khóa. Vui lòng thiết lập khóa trước khi nhập điểm.")
                return redirect('teacher_manage_keys')
            
            # Lưu transaction trước khi ký
            transaction.save()
            
            # Ký giao dịch bằng private_key của giảng viên
            try:
                transaction.sign_transaction(private_key, 'creator', user=request.user)
                messages.success(request, f"Đã nhập và ký điểm {transaction.score} cho sinh viên {transaction.student.name}, môn {transaction.course.name}!")
            except ValueError as e:
                # Xóa giao dịch nếu không thể ký
                transaction.delete()
                messages.error(request, f"Lỗi khi ký số: {str(e)}")
                return redirect('add_score')
            except Exception as e:
                # Xóa giao dịch nếu có lỗi khác
                transaction.delete()
                messages.error(request, f"Lỗi không xác định: {str(e)}")
                return redirect('add_score')
            
            # Chuyển hướng về trang thêm điểm mới nếu người dùng muốn nhập điểm khác
            if 'submit_add_another' in request.POST:
                return redirect('add_score')
            
            # Mặc định chuyển hướng về trang chủ
            return redirect('teacher_home')
    else:
        form = TeacherTransactionForm(initial=initial_data)
    
    # Lấy điểm đang chờ duyệt gần đây
    recent_pending_scores = Transaction.objects.filter(
        created_by=request.user,
        status='pending'
    ).order_by('-timestamp')[:5]
    
    context = {
        'form': form,
        'recent_pending_scores': recent_pending_scores,
    }
    return render(request, 'teacher_app/add_score.html', context)

@login_required
@user_passes_test(is_teacher_or_admin, login_url='login')
def score_history(request):
    """Xem lịch sử điểm đã nhập"""
    # Lấy tất cả điểm do người dùng hiện tại tạo
    scores = Transaction.objects.filter(created_by=request.user).order_by('-timestamp')
    
    # Lọc theo sinh viên
    student_id = request.GET.get('student')
    if student_id:
        scores = scores.filter(student_id=student_id)
    
    # Lọc theo môn học
    course_id = request.GET.get('course')
    if course_id:
        scores = scores.filter(course_id=course_id)
    
    # Lọc theo trạng thái
    status = request.GET.get('status')
    if status:
        scores = scores.filter(status=status)
    
    # Lọc theo đã xác nhận hay chưa
    mined = request.GET.get('mined')
    if mined == 'yes':
        scores = scores.filter(is_mined=True)
    elif mined == 'no':
        scores = scores.filter(is_mined=False)
    
    # Phân trang
    paginator = Paginator(scores, 10)  # 10 điểm mỗi trang
    page_number = request.GET.get('page')
    scores = paginator.get_page(page_number)
    
    # Lấy danh sách sinh viên và môn học cho bộ lọc
    students = Student.objects.all().order_by('student_id')
    courses = Course.objects.all().order_by('code')
    
    context = {
        'scores': scores,
        'students': students,
        'courses': courses,
    }
    return render(request, 'teacher_app/score_history.html', context)

@login_required
@user_passes_test(is_teacher_or_admin, login_url='login')
def teacher_student_list(request):
    """Xem danh sách sinh viên"""
    # Lọc sinh viên theo tìm kiếm
    query_student_id = request.GET.get('student_id', '')
    query_name = request.GET.get('name', '')
    
    students = Student.objects.all().order_by('student_id')
    
    if query_student_id:
        students = students.filter(student_id__icontains=query_student_id)
    if query_name:
        students = students.filter(name__icontains=query_name)
    
    # Phân trang
    paginator = Paginator(students, 10)  # 10 sinh viên mỗi trang
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    context = {
        'students': students,
    }
    return render(request, 'teacher_app/student_list.html', context)

@login_required
@user_passes_test(is_teacher_or_admin, login_url='login')
def teacher_course_list(request):
    """Xem danh sách môn học"""
    # Lọc môn học theo tìm kiếm
    query_code = request.GET.get('code', '')
    query_name = request.GET.get('name', '')
    
    courses = Course.objects.all().order_by('code')
    
    if query_code:
        courses = courses.filter(code__icontains=query_code)
    if query_name:
        courses = courses.filter(name__icontains=query_name)
    
    # Phân trang
    paginator = Paginator(courses, 10)  # 10 môn học mỗi trang
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)
    
    context = {
        'courses': courses,
    }
    return render(request, 'teacher_app/course_list.html', context)

@login_required
@user_passes_test(is_teacher_or_admin, login_url='login')
def api_student_scores(request, student_id):
    """API lấy điểm của một sinh viên"""
    student = get_object_or_404(Student, id=student_id)
    
    # Lấy điểm của sinh viên do người dùng hiện tại nhập
    scores = Transaction.objects.filter(
        student_id=student_id,
        created_by=request.user
    ).order_by('-timestamp')
    
    # Chuyển đổi sang format JSON
    scores_data = [{
        'id': score.id,
        'course_name': score.course.name,
        'score': score.score,
        'status': score.status,
        'status_display': score.get_status_display(),
        'is_mined': score.is_mined,
        'timestamp': score.timestamp.strftime('%d/%m/%Y %H:%M'),
    } for score in scores]
    
    return JsonResponse({
        'student': {
            'id': student.id,
            'student_id': student.student_id,
            'name': student.name,
        },
        'scores': scores_data
    })

@login_required
@user_passes_test(is_teacher_or_admin, login_url='login')
def api_course_scores(request, course_id):
    """API lấy thống kê điểm của một môn học"""
    course = get_object_or_404(Course, id=course_id)
    
    # Lấy điểm của môn học do người dùng hiện tại nhập
    scores = Transaction.objects.filter(
        course_id=course_id,
        created_by=request.user
    ).order_by('-timestamp')
    
    # Tính toán thống kê
    stats = scores.aggregate(
        average_score=Avg('score'),
        max_score=Max('score'),
        min_score=Min('score'),
    )
    
    # Tính tỷ lệ đạt (điểm >= 5)
    total_scores = scores.count()
    pass_scores = scores.filter(score__gte=5).count()
    pass_rate = round((pass_scores / total_scores) * 100) if total_scores > 0 else 0
    
    # Tính phân bố điểm
    distribution = [
        scores.filter(score__lt=4).count(),
        scores.filter(score__gte=4, score__lt=5).count(),
        scores.filter(score__gte=5, score__lt=6).count(),
        scores.filter(score__gte=6, score__lt=7).count(),
        scores.filter(score__gte=7, score__lt=8).count(),
        scores.filter(score__gte=8, score__lt=9).count(),
        scores.filter(score__gte=9).count(),
    ]
    
    # Chuyển đổi sang format JSON
    scores_data = [{
        'id': score.id,
        'student_id': score.student.student_id,
        'student_name': score.student.name,
        'score': score.score,
        'status': score.status,
        'status_display': score.get_status_display(),
        'is_mined': score.is_mined,
        'timestamp': score.timestamp.strftime('%d/%m/%Y %H:%M'),
    } for score in scores]
    
    return JsonResponse({
        'course': {
            'id': course.id,
            'code': course.code,
            'name': course.name,
        },
        'total_scores': total_scores,
        'average_score': stats['average_score'] or 0,
        'max_score': stats['max_score'] or 0,
        'min_score': stats['min_score'] or 0,
        'pass_rate': pass_rate,
        'distribution': distribution,
        'scores': scores_data
    })

@login_required
@user_passes_test(is_teacher_or_admin, login_url='login')
def manage_keys(request):
    """Trang quản lý khóa của giảng viên"""
    if request.method == 'POST' and 'generate_keys' in request.POST:
        # Tạo cặp khóa mới
        private_key = request.user.generate_keypair()
        
        # Hiển thị khóa riêng tư cho người dùng để lưu (chỉ hiển thị một lần)
        context = {
            'private_key': private_key,
            'public_key': request.user.public_key,
            'key_generated': True
        }
        return render(request, 'teacher_app/manage_keys.html', context)
    
    context = {
        'public_key': request.user.public_key,
        'has_keys': bool(request.user.public_key)
    }
    return render(request, 'teacher_app/manage_keys.html', context)
