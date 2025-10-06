# 🚨 TROUBLESHOOTING GUIDE & FAQ

## 🎯 TỔNG QUAN

Tài liệu này cung cấp hướng dẫn chi tiết để xử lý các vấn đề thường gặp trong hệ thống Stock Tracking Data và trả lời các câu hỏi thường gặp.

## 🔧 SYSTEM STARTUP ISSUES

### **❌ Lỗi: Port đã được sử dụng**

**Triệu chứng:**
```
ERROR: for tracking_data_api  Cannot start service api: driver failed programming external connectivity on endpoint tracking_data_api: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Nguyên nhân:** Port 8000, 8001, 5434, hoặc 6379 đã được sử dụng bởi process khác.

**Giải pháp:**
```bash
# Kiểm tra process đang sử dụng port
lsof -i :8000
lsof -i :8001
lsof -i :5434
lsof -i :6379

# Kill process nếu cần
sudo kill -9 <PID>

# Hoặc thay đổi port trong docker-compose.yml
```

### **❌ Lỗi: Docker container không start**

**Triệu chứng:**
```
ERROR: Container tracking_data_db exited with code 1
```

**Nguyên nhân:** Database initialization failed hoặc volume permissions.

**Giải pháp:**
```bash
# Kiểm tra logs
docker logs tracking_data_db

# Clean up và restart
docker-compose down -v
docker-compose up -d

# Kiểm tra permissions
ls -la database/data/
```

### **❌ Lỗi: Database connection failed**

**Triệu chứng:**
```
psycopg2.OperationalError: could not connect to server
```

**Giải pháp:**
```bash
# Kiểm tra container status
docker ps | grep tracking_data

# Restart database container
docker restart tracking_data_db

# Kiểm tra database logs
docker logs tracking_data_db
```

## 🔌 API CONNECTION ISSUES

### **❌ Lỗi: SSI API không accessible**

**Triệu chứng:**
```
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='iboard-api.ssi.com.vn', port=443)
```

**Nguyên nhân:** SSI API bị block hoặc rate limit.

**Giải pháp:**
```bash
# Test SSI API trực tiếp
curl -H "User-Agent: Mozilla/5.0" "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info?symbol=ACB&page=1&pageSize=10"

# Kiểm tra network connectivity
ping iboard-api.ssi.com.vn

# Sử dụng SSI Proxy API thay thế
curl "http://localhost:8001/ssi/stock-info?symbol=ACB&page=1&pageSize=10"
```

### **❌ Lỗi: API response timeout**

**Triệu chứng:**
```
requests.exceptions.Timeout: HTTPSConnectionPool timeout
```

**Giải pháp:**
```bash
# Tăng timeout trong automation
python automation/automation_vn100_direct.py --request-timeout 60

# Kiểm tra network latency
ping -c 5 iboard-api.ssi.com.vn
```

### **❌ Lỗi: Cloudflare protection**

**Triệu chứng:**
```
403 Forbidden - Cloudflare protection
```

**Giải pháp:**
```bash
# Sử dụng headers phù hợp
curl -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
     -H "Accept: application/json" \
     "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info?symbol=ACB"
```

## 🗄️ DATABASE ISSUES

### **❌ Lỗi: Database schema không tồn tại**

**Triệu chứng:**
```
psycopg2.ProgrammingError: relation "stock_statistics" does not exist
```

**Giải pháp:**
```bash
# Recreate database schema
docker exec -it tracking_data_db psql -U postgres -d tracking_data -f /docker-entrypoint-initdb.d/init.sql

# Hoặc restart với fresh database
docker-compose down -v
docker-compose up -d
```

### **❌ Lỗi: Database connection pool exhausted**

**Triệu chứng:**
```
psycopg2.pool.PoolError: connection pool is closed
```

**Giải pháp:**
```bash
# Restart API container
docker restart tracking_data_api

# Kiểm tra database connections
docker exec tracking_data_db psql -U postgres -d tracking_data -c "SELECT count(*) FROM pg_stat_activity;"
```

### **❌ Lỗi: Database disk space full**

**Triệu chứng:**
```
psycopg2.OperationalError: could not write to hash-join temporary file: No space left on device
```

**Giải pháp:**
```bash
# Kiểm tra disk space
df -h

# Clean up old data
docker exec tracking_data_db psql -U postgres -d tracking_data -c "DELETE FROM stock_statistics WHERE date < '2020-01-01';"

# Vacuum database
docker exec tracking_data_db psql -U postgres -d tracking_data -c "VACUUM FULL;"
```

## 🤖 AUTOMATION ISSUES

### **❌ Lỗi: Automation không fetch được dữ liệu**

**Triệu chứng:**
```
No data fetched for symbol ACB
```

**Nguyên nhân:** SSI API không trả về dữ liệu hoặc symbol không tồn tại.

**Giải pháp:**
```bash
# Test symbol trực tiếp
curl "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info?symbol=ACB&page=1&pageSize=10"

# Kiểm tra VN100 list
curl "https://iboard-query.ssi.com.vn/stock/group/VN100"

# Debug automation
python automation/automation_vn100_direct.py --debug --max-symbols 1
```

### **❌ Lỗi: Automation bị stuck**

**Triệu chứng:**
```
Automation process không kết thúc sau nhiều giờ
```

**Giải pháp:**
```bash
# Kill automation process
pkill -f automation_vn100_direct.py

# Kiểm tra logs
tail -f automation/automation_vn100_direct.log

# Restart với debug mode
python automation/automation_vn100_direct.py --debug --max-symbols 5
```

### **❌ Lỗi: Duplicate data trong database**

**Triệu chứng:**
```
Database có duplicate records cho cùng symbol và date
```

**Giải pháp:**
```bash
# Kiểm tra duplicates
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
SELECT symbol, date, COUNT(*) 
FROM stock_statistics 
GROUP BY symbol, date 
HAVING COUNT(*) > 1;"

# Xóa duplicates
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
DELETE FROM stock_statistics 
WHERE id NOT IN (
    SELECT MIN(id) 
    FROM stock_statistics 
    GROUP BY symbol, date
);"
```

## 📊 DATA QUALITY ISSUES

### **❌ Lỗi: Dữ liệu OHLC bị thiếu**

**Triệu chứng:**
```
open_price, high_price, low_price, close_price = NULL
```

**Nguyên nhân:** URL2 (Charts History API) không được fetch hoặc lỗi mapping.

**Giải pháp:**
```bash
# Kiểm tra dữ liệu OHLC
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
SELECT COUNT(*) FROM stock_statistics WHERE open_price IS NULL;"

# Re-fetch dữ liệu OHLC
python automation/automation_vn100_direct.py --max-symbols 5 --force-refresh
```

### **❌ Lỗi: Dữ liệu date không đúng**

**Triệu chứng:**
```
Dữ liệu có date trong tương lai hoặc quá khứ xa
```

**Giải pháp:**
```bash
# Kiểm tra date range
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
SELECT MIN(date), MAX(date) FROM stock_statistics;"

# Fix date logic trong automation
# Kiểm tra timezone settings
```

## 🔍 PERFORMANCE ISSUES

### **❌ Lỗi: API response chậm**

**Triệu chứng:**
```
API response time > 5 seconds
```

**Giải pháp:**
```bash
# Kiểm tra database performance
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Optimize database
docker exec tracking_data_db psql -U postgres -d tracking_data -c "VACUUM ANALYZE;"
```

### **❌ Lỗi: Memory usage cao**

**Triệu chứng:**
```
Docker containers sử dụng > 4GB RAM
```

**Giải pháp:**
```bash
# Kiểm tra memory usage
docker stats

# Restart containers
docker-compose restart

# Kiểm tra memory leaks
docker exec tracking_data_api ps aux
```

## 🧪 TESTING ISSUES

### **❌ Lỗi: Tests không pass**

**Triệu chứng:**
```
FAILED test_api.py::test_get_stock_statistics
```

**Giải pháp:**
```bash
# Chạy tests với verbose output
cd test
python -m pytest -v

# Chạy specific test
python -m pytest test_api.py::test_get_stock_statistics -v

# Kiểm tra test data
python -m pytest --setup-show
```

### **❌ Lỗi: Test database không clean**

**Triệu chứng:**
```
Tests fail due to existing data
```

**Giải pháp:**
```bash
# Clean test database
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
TRUNCATE TABLE stock_statistics CASCADE;"

# Re-run tests
cd test && python run_all_tests.py
```

## 🔧 MAINTENANCE ISSUES

### **❌ Lỗi: Log files quá lớn**

**Triệu chứng:**
```
Disk space full due to large log files
```

**Giải pháp:**
```bash
# Clean up old logs
find . -name "*.log" -mtime +7 -delete

# Rotate logs
docker-compose logs --tail=1000 > recent_logs.txt
```

### **❌ Lỗi: Backup failed**

**Triệu chứng:**
```
pg_dump: error: could not write to output file
```

**Giải pháp:**
```bash
# Kiểm tra disk space
df -h

# Backup với compression
docker exec tracking_data_db pg_dump -U postgres -d tracking_data | gzip > backup_$(date +%Y%m%d).sql.gz
```

## 📋 FAQ - FREQUENTLY ASKED QUESTIONS

### **Q1: Làm sao để thêm symbol mới vào VN100?**

**A:** VN100 list được fetch tự động từ SSI API. Để thêm symbol mới:
```bash
# Kiểm tra VN100 list hiện tại
curl "https://iboard-query.ssi.com.vn/stock/group/VN100"

# Re-run automation để sync
python automation/automation_vn100_direct.py --max-symbols 100
```

### **Q2: Làm sao để thay đổi date range cho data fetching?**

**A:** Sửa đổi trong `automation_vn100_direct.py`:
```python
# Trong calculate_date_range function
start_date = date(2010, 1, 1)  # Thay đổi start date
end_date = date.today()        # Thay đổi end date
```

### **Q3: Làm sao để monitor system performance?**

**A:** Sử dụng các tools sau:
```bash
# System monitoring
docker stats

# Database monitoring
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
SELECT * FROM pg_stat_activity;"

# API monitoring
curl "http://localhost:8000/health"
```

### **Q4: Làm sao để scale system cho nhiều symbols hơn?**

**A:** 
1. **Horizontal scaling**: Thêm API instances
2. **Database optimization**: Index optimization
3. **Caching**: Redis caching
4. **Load balancing**: Nginx load balancer

### **Q5: Làm sao để backup và restore data?**

**A:**
```bash
# Backup
docker exec tracking_data_db pg_dump -U postgres -d tracking_data > backup.sql

# Restore
docker exec -i tracking_data_db psql -U postgres -d tracking_data < backup.sql
```

### **Q6: Làm sao để debug API issues?**

**A:**
```bash
# Enable debug mode
export DEBUG=1

# Check API logs
docker logs tracking_data_api

# Test API endpoints
curl -v "http://localhost:8000/stock-statistics?symbol=ACB&limit=5"
```

### **Q7: Làm sao để thay đổi database configuration?**

**A:** Sửa đổi trong `docker-compose.yml`:
```yaml
environment:
  POSTGRES_DB: tracking_data
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres123
```

### **Q8: Làm sao để thêm authentication cho APIs?**

**A:** Implement JWT authentication:
```python
# Thêm vào main_unified.py
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer()
```

## 🚨 EMERGENCY PROCEDURES

### **System Down**
```bash
# 1. Check system status
./ssi_system_manager.sh status

# 2. Restart all services
./ssi_system_manager.sh restart

# 3. Check logs
./ssi_system_manager.sh logs

# 4. If still down, full reset
docker-compose down -v
docker-compose up -d
```

### **Data Corruption**
```bash
# 1. Stop all services
./ssi_system_manager.sh stop

# 2. Restore from backup
docker exec -i tracking_data_db psql -U postgres -d tracking_data < backup.sql

# 3. Restart services
./ssi_system_manager.sh start
```

### **Performance Degradation**
```bash
# 1. Check resource usage
docker stats

# 2. Optimize database
docker exec tracking_data_db psql -U postgres -d tracking_data -c "VACUUM ANALYZE;"

# 3. Restart services
docker-compose restart
```

## 📞 SUPPORT CONTACTS

### **Documentation Resources**
- **Main Documentation**: `docs/` directory
- **API Documentation**: http://localhost:8000/docs
- **Handover Guide**: `docs/Handover_Guide.md`
- **System Overview**: `docs/System_Overview.md`

### **Key Files for Troubleshooting**
- **Configuration**: `docker-compose.yml`
- **Scripts**: `ssi_system_manager.sh`
- **Logs**: `automation/automation_vn100_direct.log`
- **Tests**: `test/run_all_tests.py`

---

## 🎯 CONCLUSION

Tài liệu này cung cấp hướng dẫn chi tiết để xử lý các vấn đề thường gặp trong hệ thống Stock Tracking Data. Nếu gặp vấn đề không được đề cập trong tài liệu này, vui lòng tham khảo:

1. **System Logs**: Sử dụng management scripts để xem logs
2. **Documentation**: Thư mục `docs/` để tìm hiểu thêm
3. **Test Files**: Thư mục `test/` để validate system
4. **Emergency Procedures**: Sử dụng các procedure khẩn cấp khi cần

**Hệ thống đã được thiết kế để robust và có khả năng tự phục hồi, nhưng tài liệu này sẽ giúp xử lý các vấn đề phức tạp hơn.**
