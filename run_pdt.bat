@echo off
echo === KHỞI ĐỘNG NODE PHÒNG ĐÀO TẠO ===
echo.

REM Kiểm tra cơ sở dữ liệu
if not exist db.sqlite3 (
    echo Đang tạo cơ sở dữ liệu...
    python manage.py makemigrations
    python manage.py migrate
    
    echo Đang tạo tài khoản admin...
    python create_superuser.py
)

REM Thiết lập biến môi trường
echo Đang thiết lập môi trường...
set NODE_TYPE=pdt

REM Thực hiện migrations nếu cần
echo Kiểm tra và cập nhật cơ sở dữ liệu...
python manage.py makemigrations
python manage.py migrate

REM Khởi động server
echo.
echo === SERVER PHÒNG ĐÀO TẠO ĐANG KHỞI ĐỘNG ===
echo Truy cập: http://localhost:8000
echo Tài khoản admin: admin / admin123
echo Tài khoản nhân viên: staff1 / staff123
echo Nhấn Ctrl+C để dừng server
echo.

python manage.py runserver 0.0.0.0:8000 