#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blockchain_gui.settings")
django.setup()

from blockchain_app.models import User


def create_admin():
    """Tạo tài khoản admin nếu chưa tồn tại"""
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        admin.user_type = 'admin'
        admin.save()
        print("Tài khoản admin đã được tạo:")
        print("- Username: admin")
        print("- Password: admin123")
    else:
        print("Tài khoản admin đã tồn tại.")

def create_staff():
    """Tạo 3 tài khoản nhân viên phòng đào tạo"""
    staff_accounts = [
        {"username": "staff1", "email": "nguyenvan.a@example.com", "first_name": "Văn A", "last_name": "Nguyễn"},
        {"username": "staff2", "email": "tranthib@example.com", "first_name": "Thị B", "last_name": "Trần"},
        {"username": "staff3", "email": "lequoc.c@example.com", "first_name": "Quốc C", "last_name": "Lê"}
    ]
    
    for account in staff_accounts:
        if not User.objects.filter(username=account["username"]).exists():
            staff = User.objects.create_user(
                username=account["username"],
                email=account["email"],
                password="staff123",
                first_name=account["first_name"],
                last_name=account["last_name"]
            )
            staff.user_type = 'staff'
            staff.save()
            print(f"Tài khoản nhân viên PDT đã được tạo: {account['last_name']} {account['first_name']}")
            print(f"- Username: {account['username']}")
            print("- Password: staff123")
        else:
            print(f"Tài khoản {account['username']} đã tồn tại.")

def create_teacher():
    """Tạo 3 tài khoản giảng viên"""
    teacher_accounts = [
        {"username": "teacher1", "email": "phamtuan.d@example.com", "first_name": "Tuấn D", "last_name": "Phạm"},
        {"username": "teacher2", "email": "vuminh.e@example.com", "first_name": "Minh E", "last_name": "Vũ"},
        {"username": "teacher3", "email": "hoanglan.f@example.com", "first_name": "Lan F", "last_name": "Hoàng"}
    ]
    
    for account in teacher_accounts:
        if not User.objects.filter(username=account["username"]).exists():
            teacher = User.objects.create_user(
                username=account["username"],
                email=account["email"],
                password="teacher123",
                first_name=account["first_name"],
                last_name=account["last_name"]
            )
            teacher.user_type = 'teacher'
            teacher.save()
            print(f"Tài khoản giảng viên đã được tạo: {account['last_name']} {account['first_name']}")
            print(f"- Username: {account['username']}")
            print("- Password: teacher123")
        else:
            print(f"Tài khoản {account['username']} đã tồn tại.")

def create_student():
    """Tạo 3 tài khoản sinh viên"""
    student_accounts = [
        {"username": "student1", "email": "trannam.g@example.com", "first_name": "Nam G", "last_name": "Trần"},
        {"username": "student2", "email": "lehoa.h@example.com", "first_name": "Hoa H", "last_name": "Lê"},
        {"username": "student3", "email": "nguyenduc.i@example.com", "first_name": "Đức I", "last_name": "Nguyễn"}
    ]
    
    for account in student_accounts:
        if not User.objects.filter(username=account["username"]).exists():
            student = User.objects.create_user(
                username=account["username"],
                email=account["email"],
                password="student123",
                first_name=account["first_name"],
                last_name=account["last_name"]
            )
            student.user_type = 'student'
            student.save()
            print(f"Tài khoản sinh viên đã được tạo: {account['last_name']} {account['first_name']}")
            print(f"- Username: {account['username']}")
            print("- Password: student123")
        else:
            print(f"Tài khoản {account['username']} đã tồn tại.")

if __name__ == "__main__":
    create_admin()
    create_staff()
    create_teacher()
    create_student()
    print("Đã tạo xong các tài khoản mặc định.") 