# 📊 DATA EXPORT SCRIPTS GUIDE

## 🎯 TỔNG QUAN

Tài liệu này hướng dẫn sử dụng các scripts xuất dữ liệu từ SSI API, đặc biệt là script `export_ssi_automation_style.py` được tạo để xuất dữ liệu OHLCV đầy đủ cho các mã cổ phiếu.

## 📋 DANH SÁCH SCRIPTS

### **📁 `scripts/export_ssi_automation_style.py`**
- **Mục đích**: Xuất dữ liệu OHLCV đầy đủ từ SSI API với pagination logic tương tự automation
- **Đầu vào**: Mã cổ phiếu, khoảng thời gian
- **Đầu ra**: File CSV với format pandas-friendly
- **Tính năng**: 
  - Sử dụng cùng logic pagination như `automation_vn100_direct.py`
  - Xử lý đầy đủ dữ liệu từ SSI API
  - Deduplicate và sort theo ngày
  - Format CSV chuẩn cho pandas

### **📁 `scripts/fetch_ssi_ohlcv.py`**
- **Mục đích**: Script cũ để xuất dữ liệu OHLCV (được thay thế bởi automation_style)
- **Trạng thái**: Legacy - không khuyến khích sử dụng

## 🚀 HƯỚNG DẪN SỬ DỤNG

### **📊 Export Single Symbol**

```bash
# Xuất dữ liệu DIG từ 2020-01-01 đến hôm nay
python3 scripts/export_ssi_automation_style.py --symbol DIG --start 2020-01-01 --end $(date +%F)

# Xuất dữ liệu PDR từ 2020-01-01 đến hôm nay
python3 scripts/export_ssi_automation_style.py --symbol PDR --start 2020-01-01 --end $(date +%F)

# Xuất dữ liệu CII từ 2020-01-01 đến hôm nay
python3 scripts/export_ssi_automation_style.py --symbol CII --start 2020-01-01 --end $(date +%F)
```

### **📊 Export với Custom Date Range**

```bash
# Xuất dữ liệu từ 2023-01-01 đến 2023-12-31
python3 scripts/export_ssi_automation_style.py --symbol ACB --start 2023-01-01 --end 2023-12-31

# Xuất dữ liệu từ 2024-01-01 đến hôm nay
python3 scripts/export_ssi_automation_style.py --symbol VIC --start 2024-01-01 --end $(date +%F)
```

### **📊 Export với Custom Output Directory**

```bash
# Xuất vào thư mục custom
python3 scripts/export_ssi_automation_style.py --symbol DIG --start 2020-01-01 --end $(date +%F) --output-dir /path/to/custom/directory
```

## 📋 THAM SỐ COMMAND LINE

| Parameter | Mô tả | Mặc định | Ví dụ |
|-----------|-------|----------|-------|
| `--symbol` | Mã cổ phiếu cần xuất | `DIG` | `--symbol ACB` |
| `--start` | Ngày bắt đầu (YYYY-MM-DD) | `2020-01-01` | `--start 2023-01-01` |
| `--end` | Ngày kết thúc (YYYY-MM-DD) | Hôm nay | `--end 2023-12-31` |
| `--output-dir` | Thư mục lưu file | `/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output` | `--output-dir /custom/path` |

## 📁 FORMAT OUTPUT

### **📊 CSV Structure**
```csv
date,open,high,low,close,volume
2020-01-02,10000.0,10500.0,9800.0,10200.0,1500000
2020-01-03,10200.0,10300.0,9900.0,10100.0,1200000
...
```

### **📊 Field Descriptions**
| Field | Mô tả | Data Type | Example |
|-------|-------|-----------|---------|
| `date` | Ngày giao dịch | String (YYYY-MM-DD) | `2020-01-02` |
| `open` | Giá mở cửa | Float | `10000.0` |
| `high` | Giá cao nhất | Float | `10500.0` |
| `low` | Giá thấp nhất | Float | `9800.0` |
| `close` | Giá đóng cửa | Float | `10200.0` |
| `volume` | Khối lượng giao dịch | Integer | `1500000` |

## 🔧 TECHNICAL DETAILS

### **📊 SSI API Integration**
- **URL**: `https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info`
- **Method**: GET với pagination
- **Headers**: 
  - `User-Agent`: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
  - `Referer`: https://iboard.ssi.com.vn/
  - `Origin`: https://iboard.ssi.com.vn

### **📊 Pagination Logic**
- **Page Size**: 100 records per page
- **Max Pages**: 10,000 (safety limit)
- **Continue Logic**: Dựa trên `paging.total` và `pageSize`
- **Rate Limiting**: 0.1s delay giữa các requests

### **📊 Data Processing**
- **Date Parsing**: `%d/%m/%Y` format từ SSI API
- **Date Filtering**: Chỉ lấy dữ liệu trong khoảng `start_date` đến `end_date`
- **Deduplication**: Theo `date` field (giữ record cuối cùng)
- **Sorting**: Theo `date` ascending

## 📊 USAGE EXAMPLES

### **📊 Python Integration**

```python
import pandas as pd

# Đọc file CSV đã xuất
df = pd.read_csv('/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output/DIG_daily_2020-01-01_2025-10-07_full.csv')

# Chuyển đổi date column
df['date'] = pd.to_datetime(df['date'])

# Set date làm index
df.set_index('date', inplace=True)

# Tính toán technical indicators
df['sma_20'] = df['close'].rolling(window=20).mean()
df['rsi'] = calculate_rsi(df['close'])

print(df.head())
```

### **📊 Batch Export Script**

```bash
#!/bin/bash
# Script để xuất nhiều mã cùng lúc

symbols=("DIG" "PDR" "CII" "ACB" "VIC" "VCB" "HPG" "MSN" "VHM" "GAS")
start_date="2020-01-01"
end_date=$(date +%F)

for symbol in "${symbols[@]}"; do
    echo "Exporting $symbol..."
    python3 scripts/export_ssi_automation_style.py --symbol $symbol --start $start_date --end $end_date
    sleep 2  # Delay giữa các requests
done

echo "All exports completed!"
```

## 🚨 TROUBLESHOOTING

### **📊 Common Issues**

#### **403 Forbidden Error**
```bash
# Lỗi: 403 Client Error: Forbidden
# Nguyên nhân: SSI API bị chặn hoặc rate limiting
# Giải pháp: 
# 1. Kiểm tra proxy settings
# 2. Tăng delay giữa requests
# 3. Thử lại sau vài phút
```

#### **Empty Data**
```bash
# Lỗi: Không có dữ liệu trong file CSV
# Nguyên nhân: 
# 1. Mã cổ phiếu không tồn tại
# 2. Không có dữ liệu trong khoảng thời gian
# 3. SSI API trả về empty response
# Giải pháp:
# 1. Kiểm tra mã cổ phiếu có đúng không
# 2. Thử với khoảng thời gian khác
# 3. Kiểm tra logs để debug
```

#### **Partial Data**
```bash
# Lỗi: Chỉ có một phần dữ liệu
# Nguyên nhân: 
# 1. SSI API pagination không hoạt động đúng
# 2. Rate limiting cắt ngang quá trình
# 3. Network timeout
# Giải pháp:
# 1. Chạy lại script
# 2. Kiểm tra network connection
# 3. Tăng timeout settings
```

### **📊 Debug Commands**

```bash
# Kiểm tra file output
ls -la /Users/macintoshhd/Project/Project/stock_playing/tracking_data/output/

# Kiểm tra nội dung file
head -5 /Users/macintoshhd/Project/Project/stock_playing/tracking_data/output/DIG_daily_2020-01-01_2025-10-07_full.csv

# Kiểm tra số dòng
wc -l /Users/macintoshhd/Project/Project/stock_playing/tracking_data/output/DIG_daily_2020-01-01_2025-10-07_full.csv

# Kiểm tra ngày cuối cùng
tail -5 /Users/macintoshhd/Project/Project/stock_playing/tracking_data/output/DIG_daily_2020-01-01_2025-10-07_full.csv
```

## 📊 PERFORMANCE CONSIDERATIONS

### **📊 Rate Limiting**
- **Delay**: 0.1s giữa các requests
- **Max Pages**: 10,000 per symbol
- **Timeout**: 30s per request
- **Concurrent**: Single-threaded để tránh rate limiting

### **📊 Memory Usage**
- **Processing**: Stream processing, không load toàn bộ vào memory
- **Output**: Ghi file trực tiếp, không cache trong memory
- **Deduplication**: Sử dụng dictionary để deduplicate

### **📊 Network Considerations**
- **Retry Logic**: Không có auto-retry (cần manual retry)
- **Error Handling**: Graceful error handling với logging
- **Connection Pooling**: Sử dụng requests.Session()

## 📊 BEST PRACTICES

### **📊 Data Export**
1. **Always specify date range**: Tránh export toàn bộ dữ liệu không cần thiết
2. **Use appropriate delay**: 0.1s delay giữa requests để tránh rate limiting
3. **Check output files**: Verify file size và content sau khi export
4. **Backup important data**: Lưu backup của các file quan trọng

### **📊 Script Usage**
1. **Test with small range**: Test với khoảng thời gian nhỏ trước
2. **Monitor logs**: Theo dõi logs để phát hiện issues
3. **Use batch scripts**: Sử dụng batch scripts cho nhiều symbols
4. **Validate output**: Kiểm tra output format và content

### **📊 Integration**
1. **Pandas compatibility**: Output format tương thích với pandas
2. **Date handling**: Sử dụng proper date parsing
3. **Error handling**: Implement proper error handling trong code
4. **Performance**: Optimize cho large datasets

## 📊 EXAMPLES & USE CASES

### **📊 Research & Analysis**
```python
# Xuất dữ liệu cho research
symbols = ["DIG", "PDR", "CII", "ACB", "VIC"]
for symbol in symbols:
    # Export data
    os.system(f"python3 scripts/export_ssi_automation_style.py --symbol {symbol} --start 2020-01-01 --end $(date +%F)")
    
    # Load và analyze
    df = pd.read_csv(f"output/{symbol}_daily_2020-01-01_{date.today().strftime('%Y-%m-%d')}_full.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    # Technical analysis
    df['sma_20'] = df['close'].rolling(20).mean()
    df['volatility'] = df['close'].pct_change().rolling(20).std()
    
    print(f"{symbol}: Latest close = {df['close'].iloc[-1]:.2f}")
```

### **📊 Portfolio Analysis**
```python
# Xuất dữ liệu cho portfolio analysis
portfolio_symbols = ["DIG", "PDR", "CII"]
all_data = {}

for symbol in portfolio_symbols:
    df = pd.read_csv(f"output/{symbol}_daily_2020-01-01_{date.today().strftime('%Y-%m-%d')}_full.csv")
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    all_data[symbol] = df['close']

# Tạo portfolio dataframe
portfolio_df = pd.DataFrame(all_data)
portfolio_df['portfolio_return'] = portfolio_df.pct_change().mean(axis=1)

print("Portfolio Analysis:")
print(portfolio_df.tail())
```

## 📊 CONCLUSION

Script `export_ssi_automation_style.py` cung cấp cách thức xuất dữ liệu OHLCV đầy đủ và đáng tin cậy từ SSI API. Với:

- ✅ **Robust pagination logic** từ automation system
- ✅ **Pandas-compatible output format**
- ✅ **Comprehensive error handling**
- ✅ **Flexible date range support**
- ✅ **Rate limiting protection**

Script này là công cụ lý tưởng cho:
- 📊 **Data analysis và research**
- 📊 **Portfolio analysis**
- 📊 **Technical analysis**
- 📊 **Backtesting và strategy development**

**Tất cả dữ liệu đã được test và verify với các mã DIG, PDR, CII từ 2020-01-01 đến hôm nay.**

