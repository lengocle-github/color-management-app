# PoC: Colorful iGame RTX 5070 RGB LED Test

## Mục đích
Test xem có thể giao tiếp và điều khiển RGB LED trên card Colorful iGame RTX 5070 Ultra W OC 12GB qua I2C hay không.

## Yêu cầu
- Windows 11
- Python 3.10+ (cài từ python.org)
- NVIDIA driver đã cài (GeForce Experience hoặc driver standalone)
- Card Colorful iGame RTX 5070 Ultra W OC 12GB

## Cách chạy

### Bước 1: Cài Python dependencies
```
pip install -r requirements.txt
```

### Bước 2: Chạy script scan I2C (tìm LED controller)
```
python scan_i2c.py
```
Script sẽ scan tất cả I2C addresses trên GPU và báo cáo device nào phản hồi.

### Bước 3: Chạy script set màu xanh dương
```
python set_blue.py
```
Script sẽ thử set LED thành màu xanh dương (#0066FF).

## Cảnh báo
- Script CHỈ giao tiếp qua NvAPI I2C — KHÔNG thay đổi GPU settings (clock, voltage, etc.)
- Nếu LED không phản hồi, không có hại gì cho card
- Cần chạy với quyền Administrator

## Troubleshooting
- Nếu "NvAPI DLL not found" → Kiểm tra NVIDIA driver đã cài chưa
- Nếu "No GPU detected" → Kiểm tra card có được nhận trong Device Manager không
- Nếu scan không tìm thấy device → LED controller có thể dùng protocol khác (không phải I2C chuẩn)
