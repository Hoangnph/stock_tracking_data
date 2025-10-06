# 🕰️ DAILY AUTOMATION SERVICE SETUP

## 🎯 TỔNG QUAN

Hướng dẫn thiết lập automation service để chạy hàng ngày lúc 17:00, tự động cập nhật dữ liệu VN100.

## 📁 FILES ĐÃ TẠO

### **📋 Service Files:**
- **`scripts/daily_automation.sh`** - Script chính chạy automation
- **`scripts/automation_service_manager.sh`** - Manager để quản lý service
- **`scripts/vn100-automation.service`** - Systemd service file (Linux)
- **`scripts/vn100-automation.timer`** - Systemd timer file (Linux)

## 🚀 CÁCH SỬ DỤNG

### **📋 1. Cài đặt Service (macOS)**

```bash
# Cài đặt service
./scripts/automation_service_manager.sh install

# Kiểm tra trạng thái
./scripts/automation_service_manager.sh status

# Chạy thử ngay
./scripts/automation_service_manager.sh run-now
```

### **📋 2. Quản lý Service**

```bash
# Dừng service
./scripts/automation_service_manager.sh stop

# Khởi động lại service
./scripts/automation_service_manager.sh start

# Gỡ cài đặt service
./scripts/automation_service_manager.sh uninstall

# Xem logs
./scripts/automation_service_manager.sh logs
```

### **📋 3. Cài đặt Service (Linux với systemd)**

```bash
# Copy service files
sudo cp scripts/vn100-automation.service /etc/systemd/system/
sudo cp scripts/vn100-automation.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable và start timer
sudo systemctl enable vn100-automation.timer
sudo systemctl start vn100-automation.timer

# Kiểm tra trạng thái
sudo systemctl status vn100-automation.timer
```

## ⚙️ CẤU HÌNH SERVICE

### **📊 Schedule:**
- **Thời gian**: Hàng ngày lúc 17:00 (5:00 PM)
- **Timezone**: GMT+7 (Vietnam time)
- **Retry**: Không retry tự động (manual restart nếu fail)

### **📊 Automation Settings:**
- **Max Symbols**: 100 (tất cả VN100)
- **Mode**: Production
- **Log Level**: INFO
- **Log Files**: `logs/daily_automation_YYYYMMDD.log`

### **📊 System Checks:**
- Kiểm tra Docker containers
- Kiểm tra API health
- Tự động restart nếu cần
- Logging chi tiết

## 📊 MONITORING

### **📋 Log Files:**
```bash
# Logs hàng ngày
logs/daily_automation_20251006.log

# Service logs
logs/automation_service.log
logs/automation_service_error.log

# Automation logs
automation/automation_vn100_direct.log
```

### **📋 Kiểm tra Status:**
```bash
# Kiểm tra service status
./scripts/automation_service_manager.sh status

# Xem logs gần nhất
./scripts/automation_service_manager.sh logs

# Chạy manual để test
./scripts/automation_service_manager.sh run-now
```

## 🔧 TROUBLESHOOTING

### **❌ Service không chạy:**
```bash
# Kiểm tra service status
./scripts/automation_service_manager.sh status

# Kiểm tra logs
./scripts/automation_service_manager.sh logs

# Restart service
./scripts/automation_service_manager.sh stop
./scripts/automation_service_manager.sh start
```

### **❌ Automation fail:**
```bash
# Kiểm tra system status
./ssi_system_manager.sh status

# Restart system
./ssi_system_manager.sh restart

# Chạy manual để debug
./scripts/automation_service_manager.sh run-now
```

### **❌ Permission issues:**
```bash
# Fix permissions
chmod +x scripts/daily_automation.sh
chmod +x scripts/automation_service_manager.sh

# Check file ownership
ls -la scripts/
```

## 📋 DAILY WORKFLOW

### **🕰️ 17:00 Daily:**
1. **System Check**: Kiểm tra Docker và API
2. **Data Fetch**: Lấy dữ liệu mới từ SSI
3. **Database Update**: Cập nhật database
4. **Validation**: Kiểm tra dữ liệu
5. **Logging**: Ghi log chi tiết
6. **Notification**: Thông báo kết quả (optional)

### **📊 Expected Results:**
- **Data Coverage**: 100% VN100 symbols
- **Update Time**: ~30-60 minutes
- **Success Rate**: 99%+ (với retry logic)
- **Log Size**: ~1-5MB per day

## 🎯 BENEFITS

### **✅ Automated Updates:**
- Tự động cập nhật dữ liệu hàng ngày
- Không cần can thiệp thủ công
- Đảm bảo dữ liệu luôn mới nhất

### **✅ Production Ready:**
- Error handling và retry logic
- Comprehensive logging
- System health checks
- Easy monitoring

### **✅ Flexible Management:**
- Dễ dàng start/stop service
- Manual run khi cần
- Log monitoring
- Easy troubleshooting

---

## 🎉 KẾT LUẬN

**Service đã được thiết lập để chạy automation hàng ngày lúc 17:00, tự động cập nhật dữ liệu VN100 mà không cần can thiệp thủ công.**

**Sử dụng `./scripts/automation_service_manager.sh install` để bắt đầu!**
