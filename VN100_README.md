# VN100 Data Fetcher

## 📊 Tổng quan

Script này giúp bạn lấy dữ liệu lịch sử của tất cả 100 mã cổ phiếu VN100 từ 2010-01-01 đến hiện tại từ SSI API với xử lý đầy đủ các ngày không có dữ liệu.

## 🚀 Cách sử dụng

### Cách 1: Script đơn giản (Khuyến nghị)
```bash
python fetch_vn100.py
```

### Cách 2: Script đầy đủ với tùy chọn
```bash
python scripts/fetch_vn100_complete.py --start 2010-01-01 --end 2025-10-20
```

### Cách 3: Test với số lượng mã giới hạn
```bash
python scripts/fetch_vn100_complete.py --start 2010-01-01 --max-symbols 10
```

### Cách 4: Theo dõi tiến trình
```bash
python monitor_vn100.py
```

## 📁 Kết quả

Dữ liệu sẽ được lưu vào file CSV trong thư mục `output/YYYY-MM-DD/` với tên:
- `{SYMBOL}_daily_2010-01-01_2025-10-20_full.csv` (cho mỗi mã VN100)

## 📋 Dữ liệu bao gồm

- **Date**: Ngày giao dịch
- **Open**: Giá mở cửa
- **High**: Giá cao nhất
- **Low**: Giá thấp nhất  
- **Close**: Giá đóng cửa
- **Volume**: Khối lượng giao dịch

## 📊 Thống kê dữ liệu VN100

### Mã có dữ liệu đầy đủ từ 2010:
- **ACB**: 3,936 records (2010-01-04 đến 2025-10-17)
- **ANV**: 3,931 records (2010-01-04 đến 2025-10-17)
- **BID**: 2,926 records (2010-01-04 đến 2025-10-17)
- **BMP**: 3,923 records (2010-01-04 đến 2025-10-17)
- **BSI**: 3,543 records (2010-01-04 đến 2025-10-17)
- **BVH**: 3,936 records (2010-01-04 đến 2025-10-17)
- **BWE**: 3,936 records (2010-01-04 đến 2025-10-17)
- **CII**: 3,936 records (2010-01-04 đến 2025-10-17)
- **CMG**: 3,936 records (2010-01-04 đến 2025-10-17)
- **CTD**: 3,936 records (2010-01-04 đến 2025-10-17)

### Mã có dữ liệu từ năm sau:
- **BCM**: 1,892 records (2018-02-21 đến 2025-10-17)

## 🔧 Xử lý dữ liệu thiếu

Script tự động xử lý các ngày không có dữ liệu:
- **Ngày nghỉ cuối tuần**: Tự động bỏ qua
- **Ngày lễ**: Được xác định và bỏ qua
- **Nghỉ Tết**: Được xử lý đúng cách
- **Ngày nghỉ khác**: Được phân tích và báo cáo

## 🔧 Yêu cầu hệ thống

- Python 3.7+
- Thư viện: `requests`
- Kết nối internet để truy cập SSI API

## 📝 Ghi chú

- Dữ liệu được lấy từ SSI Charts History API (cùng API với VN-Index)
- Script có xử lý lỗi và retry logic
- Dữ liệu được validate trước khi lưu
- Format CSV tương thích với hệ thống hiện tại
- Tự động phân tích độ hoàn thiện dữ liệu
- Rate limiting để tránh bị chặn API
- Thời gian hoàn thành: khoảng 10-15 phút cho 100 mã

## 🎯 Tính năng nổi bật

- **API tối ưu**: Sử dụng Charts History API cho dữ liệu đầy đủ
- **Xử lý lỗi**: Retry logic và error handling
- **Theo dõi tiến trình**: Script monitor để theo dõi
- **Rate limiting**: Tránh bị chặn API
- **Dữ liệu đầy đủ**: Từ 2010 đến hiện tại
- **Format chuẩn**: CSV tương thích với pandas
