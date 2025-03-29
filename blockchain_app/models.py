from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import secrets
import hashlib

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Nhân viên phòng đào tạo'),
        ('teacher', 'Giảng viên'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='staff')
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    public_key = models.CharField(max_length=256, blank=True, null=True)
    
    # Lưu ý: Không lưu private key vào cơ sở dữ liệu
    
    def generate_keypair(self):
        """Tạo cặp khóa công khai/riêng tư và trả về khóa riêng tư (chỉ hiển thị một lần)"""
        # Tạo private key (chỉ hiển thị một lần cho người dùng)
        private_key = secrets.token_hex(32)  # 256-bit private key
        
        # Tạo public key từ private key
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        
        # Lưu public key
        self.public_key = public_key
        self.save()
        
        return private_key

    class Meta:
        # Sử dụng verbose_name để hiển thị tên thân thiện
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    credits = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
        ('expired', 'Hết hạn'), # Thêm trạng thái mới
    )
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_transactions')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transactions')
    approval_time = models.DateTimeField(null=True, blank=True)
    
    # Thêm trường mới để lưu danh sách staff đã vote
    approving_staff = models.ManyToManyField(User, related_name='approving_transactions', blank=True)
    
    # Thêm trường mới để lưu staff từ chối
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_transactions')
    rejection_reason = models.TextField(blank=True, null=True)
    rejection_time = models.DateTimeField(null=True, blank=True)
    
    is_mined = models.BooleanField(default=False)
    
    # Thêm trường deadline - mặc định là 3 ngày sau khi tạo
    deadline = models.DateTimeField(null=True, blank=True)
    
    # Thêm các trường liên quan đến chữ ký số
    creator_signature = models.CharField(max_length=512, blank=True, null=True)
    approver_signature = models.CharField(max_length=512, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Nếu là lần đầu tạo, thiết lập deadline
        if not self.pk and not self.deadline:
            self.deadline = timezone.now() + timedelta(days=3)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Kiểm tra xem giao dịch đã quá hạn chưa"""
        return timezone.now() > self.deadline if self.deadline else False

    def sign_transaction(self, private_key, role='creator', user=None):
        """
        Ký giao dịch bằng khóa riêng tư
        role: 'creator' hoặc 'approver'
        user: user cụ thể để ký (nếu không phải created_by hoặc approved_by)
        """
        # Tạo một chuỗi dữ liệu từ thông tin giao dịch
        transaction_data = f"{self.transaction_id}{self.student.student_id}{self.course.code}{self.score}"
        
        # Lấy người dùng dựa trên vai trò hoặc được truyền vào trực tiếp
        signing_user = user  # Ưu tiên user được truyền vào
        
        if not signing_user:
            if role == 'creator':
                signing_user = self.created_by
            elif role == 'approver' and hasattr(self, 'approved_by') and self.approved_by:
                signing_user = self.approved_by
        
        # Kiểm tra người dùng có tồn tại và có public key không - cung cấp thông tin chi tiết hơn
        if not signing_user:
            raise ValueError("Không tìm thấy người dùng hợp lệ để ký giao dịch")
        
        if not signing_user.public_key:
            raise ValueError(f"Người dùng {signing_user.username} chưa thiết lập khóa công khai. Vui lòng thiết lập khóa trước.")
        
        # Tạo public key từ private key
        generated_public_key = hashlib.sha256(private_key.encode()).hexdigest()
        
        # Xác minh khớp với public key đã lưu
        if generated_public_key != signing_user.public_key:
            raise ValueError("Khóa riêng tư không hợp lệ! Không khớp với khóa công khai của bạn.")
        
        # Tạo một "message" bằng cách kết hợp private_key và dữ liệu giao dịch
        message = hashlib.sha256(f"{private_key}{transaction_data}".encode()).hexdigest()
        
        # Tạo chữ ký
        signature = hashlib.sha256(f"{message}{private_key}".encode()).hexdigest()
        
        # Lưu chữ ký vào trường thích hợp
        if role == 'creator':
            self.creator_signature = signature
        elif role == 'approver':
            self.approver_signature = signature
        
        self.save()
        return signature
    
    def verify_signature(self, public_key, role='creator'):
        """
        Xác minh chữ ký bằng khóa công khai
        role: 'creator' hoặc 'approver'
        """
        # Lấy chữ ký cần xác minh
        signature = self.creator_signature if role == 'creator' else self.approver_signature
        
        if not signature:
            return False
        
        # Tạo lại dữ liệu giao dịch
        transaction_data = f"{self.transaction_id}{self.student.student_id}{self.course.code}{self.score}"
        
        # Trong hệ thống thực tế, đây là nơi xác minh chữ ký bằng khóa công khai
        # Sử dụng transaction_data trong quá trình xác minh
        expected_message = hashlib.sha256(f"{public_key}{transaction_data}".encode()).hexdigest()
        expected_signature = hashlib.sha256(f"{expected_message}{public_key}".encode()).hexdigest()
        
        # So sánh chữ ký được cung cấp với chữ ký được tính toán
        return signature == expected_signature

    def __str__(self):
        return f"{self.student.student_id} - {self.course.code} - {self.score} ({self.get_status_display()})"

class Block(models.Model):
    index = models.IntegerField(unique=True)
    hash = models.CharField(max_length=64)
    previous_hash = models.CharField(max_length=64)
    merkle_root = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)
    nonce = models.IntegerField()
    transactions = models.ManyToManyField(Transaction)
    difficulty = models.IntegerField(default=4)

    class Meta:
        ordering = ['-index']

    def __str__(self):
        return f"Block #{self.index} - {self.hash[:10]}..."
