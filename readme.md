# Hệ thống giám sát mưa & độ ẩm realtime từ Pi Pico

Dự án sử dụng:
- Flask + Flask-SocketIO (WebSocket realtime)
- SQLite (có thể đổi sang PostgreSQL sau)
- Pi Pico (MicroPython) gửi dữ liệu qua WebSocket

## Cấu trúc dữ liệu
- `devices`: thông tin trạm (id, tên, tọa độ, độ che phủ rừng, độ dốc, trạng thái online)
- `measurements`: dữ liệu thô (lượng mưa, độ ẩm, nhiệt độ, timestamp)
- `analysis`: dữ liệu sau phân tích (cảnh báo lũ, cháy rừng…)

---

## Hướng dẫn chạy dự án (cho lần đầu)

### 1. Clone và vào thư mục dự án
```bash
git clone <link-repo-của-bạn>
cd pico_monitor
```
### 2. Tạo virtual environment

```bash
python -m venv venv
```

### 3. Kích hoạt venv
#### Linux / macOS:
```bash 
source venv/bin/activate
```

#### Windows:
```cmd
venv\Scripts\activate
```
### 4. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 5. Tạo thư mục instance (nếu chưa có)
```bash
mkdir instance
```

___Quan trọng: SQLite sẽ lưu database vào đây. Nếu thiếu thư mục này sẽ bị lỗi!___

### 6. Khởi tạo database + dữ liệu mẫu
```bash
python app/database_init.py
```

→ Lần đầu chạy sẽ tạo bảng + 3 thiết bị mẫu + dữ liệu đo mẫu.

### 7. Chạy server
```bash
python run.py
```

Server sẽ chạy tại:
http://127.0.0.1:5000
http://[IP-máy-bạn]:5000 (để Pi Pico kết nối từ xa)


### 8. Kiểm tra API (mẫu)
```bash
# Xem tất cả thiết bị
curl http://127.0.0.1:5000/api/devices

# Xem dữ liệu đo (có phân trang)
curl "http://127.0.0.1:5000/api/measurements?client_id=pico_001&per_page=20"
```


### 9. Kết nối từ Pi Pico (MicroPython)
```python
import usocketio
client = usocketio.client("http://192.168.1.100:5000/pico")  # thay IP máy bạn
client.emit('pico_data', {
    'id': 'pico_001',
    'rain': 25.5,
    'hum': 88.2,
    'temp': 26.1
})
```

## Các lệnh hữu ích khác
```bash 
# Xóa database và tạo lại từ đầu
rm instance/app.db
python app/database_init.py

# Chạy lại server (khi sửa code)
python run.py
```

