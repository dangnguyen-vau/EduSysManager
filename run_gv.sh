#!/bin/bash
# Script chạy server Giảng Viên trên port 8001

set -e  # Dừng script nếu có lỗi

export NODE_TYPE=gv
echo "===== Khởi động Server Giảng Viên trên port 8001 ====="
cd "$(dirname "$0")"

# Kiểm tra xem database đã tồn tại chưa và tạo migrations nếu cần
if [ ! -f "db.sqlite3" ]; then
    echo ">> Tạo database và migrations mới..."
    python manage.py makemigrations
    python manage.py migrate
    
    echo ">> Tạo tài khoản ..."
    python create_superuser.py
fi

echo ">> Khởi động server trên port 8001..."
echo ">> Truy cập: http://localhost:8001/"
echo ">> Đăng nhập với tài khoản:"
echo "   - Tên đăng nhập: teacher1"
echo "   - Mật khẩu: teacher123"
echo "=============================================="

python manage.py runserver 0.0.0.0:8001 