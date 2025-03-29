from django.contrib import admin
from .models import User, Student, Course, Transaction, Block

# Đăng ký model User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'department')
    list_filter = ('user_type', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'department')
    fieldsets = (
        ('Thông tin cá nhân', {'fields': ('username', 'password', 'first_name', 'last_name', 'email')}),
        ('Quyền hạn', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Thông tin chức vụ', {'fields': ('user_type', 'department', 'phone')}),
        ('Ngày quan trọng', {'fields': ('last_login', 'date_joined')}),
    )

# Đăng ký model Student
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'created_at')
    search_fields = ('student_id', 'name', 'email')
    ordering = ('student_id',)

# Đăng ký model Course
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits', 'created_at')
    search_fields = ('code', 'name')
    ordering = ('code',)

# Đăng ký model Transaction với các tùy chọn nâng cao
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'student', 'course', 'score', 'status', 
                   'timestamp', 'created_by', 'approved_by', 'is_mined')
    list_filter = ('status', 'is_mined', 'course', 'timestamp')
    search_fields = ('student__student_id', 'student__name', 'course__code', 'course__name')
    readonly_fields = ('transaction_id', 'timestamp', 'is_mined')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Thông tin điểm', {
            'fields': ('transaction_id', 'student', 'course', 'score')
        }),
        ('Trạng thái', {
            'fields': ('status', 'is_mined')
        }),
        ('Thông tin phê duyệt', {
            'fields': ('created_by', 'approved_by', 'approval_time', 'rejection_reason')
        }),
        ('Thời gian', {
            'fields': ('timestamp',)
        }),
    )

# Đăng ký model Block
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('index', 'hash', 'timestamp', 'nonce', 'difficulty')
    list_filter = ('difficulty', 'timestamp')
    search_fields = ('hash', 'previous_hash')
    readonly_fields = ('hash', 'previous_hash', 'merkle_root', 'timestamp')
    filter_horizontal = ('transactions',)
