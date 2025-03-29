@echo off
echo === KHỞI ĐỘNG NODE SINH VIÊN ===
echo.

REM Kiểm tra cơ sở dữ liệu
if not exist db.sqlite3 (
    echo Đang tạo cơ sở dữ liệu...
    python manage.py makemigrations
    python manage.py migrate
)

REM Thiết lập biến môi trường
echo Đang thiết lập môi trường...
set NODE_TYPE=sv

REM Thực hiện migrations nếu cần
echo Kiểm tra và cập nhật cơ sở dữ liệu...
python manage.py makemigrations
python manage.py migrate

REM Khởi động server
echo.
echo === SERVER SINH VIÊN ĐANG KHỞI ĐỘNG ===
echo Truy cập: http://localhost:8002
echo Tài khoản sinh viên: Đăng ký thông qua giao diện
echo Nhấn Ctrl+C để dừng server
echo.

python manage.py runserver 0.0.0.0:8002 