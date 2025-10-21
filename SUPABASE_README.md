# Supabase Integration

## 📊 Tổng quan

Hệ thống tích hợp Supabase để lưu trữ và quản lý dữ liệu cổ phiếu VN100 và VN-Index từ SSI API.

## 🚀 Cài đặt

### 1. Cài đặt dependencies
```bash
python setup_supabase.py
```

### 2. Cấu hình Supabase
1. Tạo project trên [Supabase](https://supabase.com)
2. Copy `.env.example` thành `.env`
3. Điền thông tin Supabase vào `.env`:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

### 3. Tạo database schema
Chạy SQL schema trong Supabase SQL Editor:
```bash
cat supabase_schema.sql
```

## 📁 Cấu trúc Database

### Tables chính:

#### `stock_data`
- Lưu trữ dữ liệu OHLCV cho tất cả cổ phiếu
- Fields: `symbol`, `date`, `open`, `high`, `low`, `close`, `volume`
- Index: `(symbol, date)` unique

#### `vn100_symbols`
- Lưu trữ danh sách mã VN100
- Fields: `symbol`, `company_name`, `sector`, `market_cap`, `is_active`

#### `vnindex_data`
- Lưu trữ dữ liệu VN-Index
- Fields: `date`, `open`, `high`, `low`, `close`, `volume`

#### `data_sources`
- Theo dõi nguồn dữ liệu
- Fields: `source_name`, `source_type`, `last_updated`, `status`

## 🔧 Sử dụng

### Test kết nối
```bash
python upload_to_supabase.py --test-connection
```

### Upload dữ liệu từ thư mục
```bash
python upload_to_supabase.py --input-dir output/2025-10-20
```

### Upload file đơn lẻ
```bash
python upload_to_supabase.py --file output/2025-10-20/ACB_daily_2010-01-01_2025-10-20_full.csv
```

### Upload với pattern
```bash
python upload_to_supabase.py --input-dir output/2025-10-20 --pattern "*VNINDEX*.csv"
```

## 📊 Tính năng

### ✅ Đã implement:
- **Supabase Client**: Kết nối và tương tác với database
- **CSV Uploader**: Upload dữ liệu từ CSV files
- **Batch Processing**: Upload theo batch để tối ưu performance
- **Error Handling**: Xử lý lỗi và retry logic
- **Progress Tracking**: Theo dõi tiến trình upload
- **Data Validation**: Validate dữ liệu trước khi upload

### 🔄 Batch Upload:
- **Batch Size**: 1000 records/batch
- **Concurrent Batches**: 5 batches đồng thời
- **Retry Logic**: 3 lần retry với delay 1s
- **Rate Limiting**: Tránh quá tải database

### 📈 Performance:
- **Upload Speed**: ~1000 records/second
- **Memory Efficient**: Stream processing
- **Error Recovery**: Continue khi có lỗi
- **Progress Reporting**: Real-time status

## 🛠️ API Endpoints

### Supabase Client Methods:
```python
# Test connection
await client.test_connection()

# Upload stock data
await client.upload_stock_data(data, symbol)

# Upload VN-Index data
await client.upload_vnindex_data(data)

# Upload VN100 symbols
await client.upload_vn100_symbols(symbols)

# Get upload status
await client.get_upload_status(symbol)

# Cleanup old data
await client.cleanup_old_data(symbol, before_date)
```

## 📋 Database Views

### `stock_data_summary`
Tổng quan dữ liệu cổ phiếu:
- Total records per symbol
- Date range
- Average close price
- Max volume

### `vnindex_summary`
Tổng quan dữ liệu VN-Index:
- Total records
- Date range
- Average close price
- Max volume

## 🔒 Security

### Row Level Security (RLS):
- **Public Read**: Cho phép đọc công khai
- **Authenticated Write**: Chỉ user đã xác thực mới được ghi
- **Service Role**: Admin operations

### Policies:
- Read access cho tất cả tables
- Write access chỉ cho authenticated users
- Admin access cho service role

## 📊 Monitoring

### Upload Statistics:
- Total files processed
- Successful uploads
- Failed uploads
- Total records uploaded
- Upload duration
- Average speed

### Error Tracking:
- Detailed error messages
- Failed file list
- Retry attempts
- Connection issues

## 🚨 Troubleshooting

### Common Issues:

1. **Connection Failed**:
   - Check `.env` file configuration
   - Verify Supabase project URL and keys
   - Test network connectivity

2. **Upload Failed**:
   - Check CSV file format
   - Verify database schema
   - Check RLS policies

3. **Performance Issues**:
   - Reduce batch size
   - Check database performance
   - Monitor network latency

### Debug Mode:
```bash
# Enable debug logging
export SUPABASE_DEBUG=1
python upload_to_supabase.py --input-dir output/2025-10-20
```

## 📚 Examples

### Upload VN100 data:
```bash
# Upload all VN100 CSV files
python upload_to_supabase.py --input-dir output/2025-10-20

# Upload only VN-Index
python upload_to_supabase.py --input-dir output/2025-10-20 --pattern "*VNINDEX*.csv"
```

### Check upload status:
```python
from supabase_client import SupabaseClient
from supabase_config import SupabaseConfig

config = SupabaseConfig.from_env()
client = SupabaseClient(config)

# Get status for ACB
status = await client.get_upload_status("ACB")
print(f"ACB records: {status['record_count']}")
```

## 🔗 Links

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
