#!/bin/bash
# Script chạy server Phòng Đào Tạo (node chính) trên port 8000

set -e  # Dừng script nếu có lỗi

export NODE_TYPE=pdt
echo "===== Khởi động Server Phòng Đào Tạo (node chính) ====="
cd "$(dirname "$0")"

# Hỏi người dùng có muốn reset database không
read -p "Bạn có muốn reset database không? (y/n): " reset_db

if [ "$reset_db" = "y" ] || [ "$reset_db" = "Y" ]; then
    echo ">> Đang reset database..."
    rm -f db.sqlite3
    python manage.py makemigrations
    python manage.py migrate
    
    echo ">> Tạo tài khoản admin..."
    python create_superuser.py
else
    # Kiểm tra xem database đã tồn tại chưa và tạo migrations nếu cần
    if [ ! -f "db.sqlite3" ]; then
        echo ">> Tạo database và migrations mới..."
        python manage.py makemigrations
        python manage.py migrate
        
        echo ">> Tạo tài khoản admin..."
        python create_superuser.py
    fi
fi

echo ">> Khởi động server trên port 8000..."
echo ">> Truy cập: http://localhost:8000/"
echo ">> Đăng nhập với tài khoản:"
echo "   - Tên đăng nhập: staff1"
echo "   - Mật khẩu: staff123"
echo "=============================================="

python manage.py runserver 0.0.0.0:8000
