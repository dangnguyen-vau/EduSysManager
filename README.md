# Hệ thống Quản lý Điểm Blockchain cho Phòng Đào Tạo

Đây là ứng dụng quản lý điểm số sử dụng công nghệ blockchain, cho phép phòng đào tạo duyệt và xác nhận điểm từ giảng viên, tạo bảng điểm an toàn và minh bạch.

## Kiến trúc hệ thống

Hệ thống được thiết kế với 3 node blockchain:

1. **Node Phòng Đào Tạo (chính)**: Duyệt điểm, tạo block, quản lý dữ liệu
2. **Node Giảng Viên**: Nhập điểm, gửi lên phòng đào tạo để duyệt
3. **Node Sinh Viên**: Xem điểm đã được xác thực trên blockchain

## Cài đặt và Chạy (Dành cho Windows)

### Cách 1: Sử dụng file .bat (Đơn giản nhất)

Hệ thống đã được cung cấp các file script (.bat) để chạy tự động. Bạn chỉ cần nhấp đúp chuột vào file tương ứng:

1. **run_pdt.bat** - Khởi động node Phòng Đào Tạo (cổng 8000)
2. **run_gv.bat** - Khởi động node Giảng Viên (cổng 8001)
3. **run_sv.bat** - Khởi động node Sinh Viên (cổng 8002)

> 💡 **Lưu ý**: Bạn cần mở mỗi file trong một cửa sổ Command Prompt riêng biệt.

### Cách 2: Thiết lập thủ công

Nếu bạn muốn thiết lập thủ công, hãy làm theo các bước sau:

### 1. Cài đặt môi trường

```powershell
# Bước 1: Tạo môi trường ảo
python -m venv .venv

# Bước 2: Kích hoạt môi trường ảo
# Nếu dùng CMD:
.venv\Scripts\activate.bat
# Hoặc nếu dùng PowerShell:
.venv\Scripts\Activate.ps1

# Bước 3: Cài đặt các gói phụ thuộc
pip install -r requirements.txt
```

> 💡 **Lưu ý**: Nếu bạn gặp lỗi "không thể chạy script", mở PowerShell với quyền Administrator và chạy lệnh: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2. Chuẩn bị cơ sở dữ liệu

```powershell
# Tạo migrations
python manage.py makemigrations

# Áp dụng migrations
python manage.py migrate
```

### 3. Chạy các node của hệ thống

> 💡 **Quan trọng**: Bạn cần mở một cửa sổ CMD hoặc PowerShell riêng cho mỗi node. Đảm bảo đã kích hoạt môi trường ảo trong mỗi cửa sổ trước khi chạy lệnh.

#### Node Phòng Đào Tạo (Port 8000):

```powershell
# Bước 1: Thiết lập biến môi trường NODE_TYPE
set NODE_TYPE=pdt

# Bước 2: Chạy server Django
python manage.py runserver 0.0.0.0:8000
```

#### Node Giảng Viên (Port 8001):

```powershell
# Bước 1: Thiết lập biến môi trường NODE_TYPE
set NODE_TYPE=gv

# Bước 2: Chạy server Django
python manage.py runserver 0.0.0.0:8001
```

#### Node Sinh Viên (Port 8002):

```powershell
# Bước 1: Thiết lập biến môi trường NODE_TYPE
set NODE_TYPE=sv

# Bước 2: Chạy server Django
python manage.py runserver 0.0.0.0:8002
```

### 4. Truy cập hệ thống

Sau khi chạy các server, bạn có thể truy cập các node thông qua trình duyệt:

- **Node Phòng Đào Tạo**: http://localhost:8000/
- **Node Giảng Viên**: http://localhost:8001/
- **Node Sinh Viên**: http://localhost:8002/

### 5. Tài khoản mặc định

Khi chạy node Phòng Đào Tạo lần đầu, các tài khoản mặc định sẽ được tạo:

#### Tài khoản Admin (dùng được ở cả ba node):
- **Tên đăng nhập**: admin
- **Mật khẩu**: admin123

#### Tài khoản giảng viên (chỉ dùng ở node giảng viên):
- **Tên đăng nhập**: teacher1
- **Mật khẩu**: teacher123

#### Tài khoản nhân viên phòng đào tạo (chỉ dùng ở node phòng đào tạo):
- **Tên đăng nhập**: staff1
- **Mật khẩu**: staff123

## Quy trình hoạt động chi tiết

### Bước 1: Giảng viên nhập điểm
1. Đăng nhập vào node giảng viên (http://localhost:8001/) với tài khoản giảng viên
2. Chọn "Nhập điểm mới" từ menu bên trái
3. Chọn sinh viên, môn học và nhập điểm
4. Nhấn "Lưu điểm" để gửi lên phòng đào tạo

### Bước 2: Phòng đào tạo duyệt điểm
1. Đăng nhập vào node phòng đào tạo (http://localhost:8000/) với tài khoản phòng đào tạo
2. Chọn "Duyệt điểm" từ menu bên trái
3. Xem danh sách điểm chờ duyệt và nhấn "Duyệt" trên từng điểm
4. Chọn "Chấp nhận" hoặc "Từ chối" điểm, kèm lý do nếu từ chối

### Bước 3: Phòng đào tạo xác nhận điểm chính thức
1. Sau khi duyệt điểm, chọn "Xác nhận điểm chính thức"
2. Kiểm tra danh sách điểm đã duyệt chờ xác nhận
3. Nhấn "Xác nhận và phát hành điểm chính thức" để tạo block mới trong blockchain

### Bước 4: Sinh viên xem điểm
1. Đăng nhập vào node sinh viên (http://localhost:8002/)
2. Xem điểm đã được xác thực trên blockchain

## Chức năng chi tiết của từng node

### Node Phòng Đào Tạo

1. **Quản lý tài khoản**:
   - Đăng nhập/đăng xuất
   - Tạo tài khoản nhân viên mới

2. **Quản lý sinh viên và môn học**:
   - Xem danh sách sinh viên/môn học
   - Thêm sinh viên/môn học mới
   - Tìm kiếm thông tin

3. **Duyệt điểm**:
   - Xem danh sách điểm chờ duyệt
   - Phê duyệt hoặc từ chối điểm
   - Ghi chú lý do từ chối

4. **Xác nhận điểm vào blockchain**:
   - Tạo block mới từ các điểm đã duyệt
   - Xem lịch sử các block
   - Kiểm tra tính toàn vẹn của blockchain

### Node Giảng Viên

1. **Quản lý điểm số**:
   - Nhập điểm cho sinh viên
   - Xem lịch sử nhập điểm
   - Theo dõi trạng thái duyệt

2. **Thống kê**:
   - Xem thống kê điểm số theo môn học
   - Xem thống kê điểm số theo sinh viên

### Node Sinh Viên

1. **Xem điểm số**:
   - Xem điểm đã được xác thực
   - Xem lịch sử các khối blockchain
   - Kiểm tra tính toàn vẹn điểm số

## Xử lý sự cố

### Lỗi "Address already in use"
Nếu gặp lỗi "Address already in use", có nghĩa là cổng đang được sử dụng:

```powershell
# Bước 1: Tìm tiến trình sử dụng cổng
netstat -ano | findstr 8000
# (Thay 8000 bằng số cổng đang bị sử dụng: 8001 hoặc 8002)

# Bước 2: Kết thúc tiến trình
# Sử dụng số PID hiển thị từ lệnh trên
taskkill /F /PID SỐ_PID
```

### Không thể chạy lệnh trong PowerShell
Nếu gặp lỗi về quyền thực thi script, hãy thử các bước sau:

1. Mở PowerShell với quyền Administrator
2. Chạy lệnh: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Khởi động lại PowerShell và thử lại 