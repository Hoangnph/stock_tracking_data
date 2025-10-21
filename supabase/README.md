# Supabase Integration

## 📊 Tổng quan

Package tích hợp Supabase để lưu trữ và quản lý dữ liệu cổ phiếu VN100 và VN-Index từ SSI API.

## 📁 Cấu trúc thư mục

```
supabase/
├── __init__.py              # Package initialization
├── config.py               # Supabase configuration
├── client.py               # Supabase client
├── upload_to_supabase.py  # CSV uploader
├── setup_supabase.py       # Setup script
├── requirements.txt        # Dependencies
├── schema.sql             # Database schema
└── README.md              # Documentation
```

## 🚀 Cài đặt

### 1. Cài đặt dependencies
```bash
python setup_supabase.py
```

### 2. Cấu hình Supabase
1. Tạo project trên [Supabase](https://supabase.com)
2. Copy `.env.example` thành `.env`
3. Điền thông tin Supabase vào `.env`

### 3. Tạo database schema
Chạy SQL schema trong Supabase SQL Editor:
```bash
cat supabase/schema.sql
```

## 🔧 Sử dụng

### Test kết nối
```bash
python upload_to_supabase.py --test-connection
```

### Upload dữ liệu
```bash
python upload_to_supabase.py --input-dir output/2025-10-20
```

## 📊 Tính năng

- **Async Support**: Hỗ trợ async/await
- **Batch Processing**: Upload theo batch
- **Error Handling**: Xử lý lỗi và retry
- **Progress Tracking**: Theo dõi tiến trình
- **Data Validation**: Validate dữ liệu
- **Security**: Row Level Security (RLS)

## 🔗 Links

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
