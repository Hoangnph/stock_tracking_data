# VN-Index Data Fetcher

## 📊 Tổng quan

Script này giúp bạn lấy dữ liệu lịch sử của chỉ số VN-Index từ 2010-01-01 đến hiện tại từ SSI API với xử lý đầy đủ các ngày không có dữ liệu.

## 🚀 Cách sử dụng

### Cách 1: Script đơn giản cho dữ liệu từ 2010 đến hiện tại (Khuyến nghị)
```bash
python fetch_vnindex_complete.py
```

### Cách 2: Script đơn giản cho dữ liệu từ 2020 đến 2025
```bash
python fetch_vnindex.py
```

### Cách 3: Script đầy đủ với tùy chọn
```bash
python scripts/fetch_vnindex_2010_present.py --start 2010-01-01 --end 2025-10-20
```

### Cách 4: Script Charts API
```bash
python scripts/fetch_vnindex_charts.py --symbol VNINDEX --start 2010-01-01 --end 2025-10-20
```

## 📁 Kết quả

Dữ liệu sẽ được lưu vào file CSV trong thư mục `output/YYYY-MM-DD/` với tên:
- `VNINDEX_complete_2010-01-01_2025-10-20_full.csv` (dữ liệu từ 2010)
- `VNINDEX_daily_2020-01-01_2025-10-18_full.csv` (dữ liệu từ 2020)

## 📋 Dữ liệu bao gồm

- **Date**: Ngày giao dịch
- **Open**: Giá mở cửa
- **High**: Giá cao nhất
- **Low**: Giá thấp nhất  
- **Close**: Giá đóng cửa
- **Volume**: Khối lượng giao dịch

## 📊 Thống kê dữ liệu (2010-2025)

- **Tổng số records**: 3,918 ngày giao dịch
- **Khoảng thời gian**: 2010-01-04 đến 2025-10-17
- **Độ hoàn thiện dữ liệu**: 95.1%
- **Ngày thiếu**: 202 ngày (chủ yếu là ngày lễ và nghỉ Tết)
- **Giá đóng cửa đầu tiên**: 517.1 điểm (2010-01-04)
- **Giá đóng cửa cuối cùng**: 1,731.19 điểm (2025-10-17)
- **Giá thấp nhất**: 336.73 điểm
- **Giá cao nhất**: 1,766.85 điểm
- **Khối lượng trung bình**: 297,061,382
- **Tổng khối lượng**: 1,163,886,496,320

## 📊 Thống kê dữ liệu (2020-2025)

- **Tổng số records**: 1,447 ngày giao dịch
- **Khoảng thời gian**: 2020-01-02 đến 2025-10-17
- **Giá đóng cửa đầu tiên**: 966.67 điểm
- **Giá đóng cửa cuối cùng**: 1,731.19 điểm
- **Giá thấp nhất**: 659.21 điểm
- **Giá cao nhất**: 1,766.85 điểm
- **Khối lượng trung bình**: 637,012,389
- **Tổng khối lượng**: 921,756,927,540

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

- Dữ liệu được lấy từ SSI Charts History API
- Script có xử lý lỗi và retry logic
- Dữ liệu được validate trước khi lưu
- Format CSV tương thích với hệ thống hiện tại
- Tự động phân tích độ hoàn thiện dữ liệu
- Báo cáo chi tiết về các ngày thiếu dữ liệu

