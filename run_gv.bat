@echo off
echo === KHỞI ĐỘNG NODE GIẢNG VIÊN ===
echo.

REM Kiểm tra cơ sở dữ liệu
if not exist db.sqlite3 (
    echo Đang tạo cơ sở dữ liệu...
    python manage.py makemigrations
    python manage.py migrate
)

REM Thiết lập biến môi trường
echo Đang thiết lập môi trường...
set NODE_TYPE=gv

REM Thực hiện migrations nếu cần
echo Kiểm tra và cập nhật cơ sở dữ liệu...
python manage.py makemigrations
python manage.py migrate

REM Khởi động server
echo.
echo === SERVER GIẢNG VIÊN ĐANG KHỞI ĐỘNG ===
echo Truy cập: http://localhost:8001
echo Tài khoản giảng viên: teacher1 / teacher123
echo Nhấn Ctrl+C để dừng server
echo.

python manage.py runserver 0.0.0.0:8001 