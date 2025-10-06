# SSI Direct API Proxy Documentation

## 📊 Tổng quan

SSI Direct API Proxy cung cấp truy cập trực tiếp vào các SSI APIs mà không cần lưu trữ vào database. Điều này hữu ích cho:

- **Real-time data access** - Lấy dữ liệu thời gian thực
- **Testing và debugging** - Test APIs mà không ảnh hưởng database
- **Development** - Phát triển và tích hợp nhanh chóng
- **Monitoring** - Theo dõi trạng thái SSI APIs

## 🚀 Service Information

- **Service Name**: SSI Direct API Proxy
- **Version**: 2.1.0
- **Port**: 8001
- **Base URL**: http://localhost:8001
- **Documentation**: http://localhost:8001/docs

## 🔗 API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-05T03:52:02.777369",
  "database": "connected",
  "version": "2.1.0",
  "service": "SSI Direct API Proxy"
}
```

### 2. Service Information
```http
GET /
```

**Response:**
```json
{
  "message": "SSI Direct API Proxy v2.1 is running",
  "version": "2.1.0",
  "description": "Direct access to SSI APIs without database storage",
  "endpoints": {
    "stock_info": "/ssi-proxy/stock-info",
    "charts_history": "/ssi-proxy/charts-history", 
    "vn100_group": "/ssi-proxy/vn100-group",
    "docs": "/docs"
  }
}
```

### 3. SSI API Configuration
```http
GET /ssi-proxy/config
```

**Response:**
```json
{
  "apis": {
    "stock_info": {
      "base_url": "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info",
      "method": "GET",
      "description": "Stock Info API - Thông tin chi tiết cổ phiếu"
    },
    "charts_history": {
      "base_url": "https://iboard-api.ssi.com.vn/statistics/charts/history",
      "method": "GET",
      "description": "Charts History API - Dữ liệu lịch sử giá"
    },
    "vn100_group": {
      "base_url": "https://iboard-query.ssi.com.vn/stock/group/VN100",
      "method": "GET",
      "description": "VN100 Group API - Thông tin nhóm cổ phiếu VN100"
    }
  },
  "timestamp": "2025-10-05T03:52:07.665280",
  "version": "2.1.0"
}
```

## 📊 SSI Proxy Endpoints

### 1. Stock Info Proxy (URL 1)

```http
GET /ssi-proxy/stock-info
```

**Parameters:**
- `symbol` (required): Mã cổ phiếu (VD: ACB)
- `from_date` (required): Ngày bắt đầu (DD/MM/YYYY)
- `to_date` (required): Ngày kết thúc (DD/MM/YYYY)
- `page` (optional): Số trang (mặc định: 1)
- `page_size` (optional): Số lượng kết quả mỗi trang (mặc định: 10)

**Example:**
```bash
curl "http://localhost:8001/ssi-proxy/stock-info?symbol=ACB&from_date=01/10/2025&to_date=05/10/2025"
```

**Response:**
```json
{
  "success": true,
  "api_endpoint": "stock-info",
  "symbol": "ACB",
  "data": [
    {
      "symbol": "ACB",
      "trading_date": "04/10/2025",
      "open_price": 25.5,
      "high_price": 26.0,
      "low_price": 25.2,
      "close_price": 25.8,
      "volume": 1000000,
      "price_changed": 0.3,
      "per_price_change": 1.18,
      "total_match_val": 25800000,
      "ceiling_price": 28.0,
      "floor_price": 23.0,
      "ref_price": 25.5,
      "avg_price": 25.6,
      "close_price_adjusted": 25.8,
      "total_match_vol": 1000000,
      "total_deal_val": 25800000,
      "total_deal_vol": 1000000,
      "foreign_buy_vol_total": 100000,
      "foreign_current_room": 500000,
      "foreign_sell_vol_total": 50000,
      "foreign_buy_val_total": 2580000,
      "foreign_sell_val_total": 1290000,
      "total_buy_trade": 1000,
      "total_buy_trade_vol": 1000000,
      "total_sell_trade": 800,
      "total_sell_trade_vol": 1000000,
      "net_buy_sell_vol": 50000,
      "net_buy_sell_val": 1290000,
      "foreign_buy_vol_matched": 100000,
      "foreign_buy_vol_deal": 0,
      "close_raw": 25.8,
      "open_raw": 25.5,
      "high_raw": 26.0,
      "low_raw": 25.2
    }
  ],
  "timestamp": "2025-10-05T03:52:07.665280",
  "response_time_ms": 248.93,
  "raw_response": { ... }
}
```

### 2. Charts History Proxy (URL 2)

```http
GET /ssi-proxy/charts-history
```

**Parameters:**
- `symbol` (required): Mã cổ phiếu (VD: PDR)
- `resolution` (required): Độ phân giải thời gian (1, 1h, 1d, 1w, 1M)
- `from_timestamp` (required): Timestamp Unix bắt đầu
- `to_timestamp` (required): Timestamp Unix kết thúc

**Example:**
```bash
FROM_TS=$(date -v-1d +%s)
TO_TS=$(date +%s)
curl "http://localhost:8001/ssi-proxy/charts-history?symbol=ACB&resolution=1d&from_timestamp=$FROM_TS&to_timestamp=$TO_TS"
```

**Response:**
```json
{
  "success": true,
  "api_endpoint": "charts-history",
  "symbol": "ACB",
  "data": {
    "symbol": "ACB",
    "resolution": "1d",
    "timestamps": [1728086400, 1728172800],
    "open_prices": [25.5, 25.8],
    "high_prices": [26.0, 26.2],
    "low_prices": [25.2, 25.6],
    "close_prices": [25.8, 26.0],
    "volumes": [1000000, 1200000],
    "status": "ok",
    "next_time": 1728259200,
    "data_points": 2
  },
  "timestamp": "2025-10-05T03:52:07.665280",
  "response_time_ms": 195.95,
  "raw_response": { ... }
}
```

### 3. VN100 Group Proxy (URL 3)

```http
GET /ssi-proxy/vn100-group
```

**Parameters:** Không cần tham số

**Example:**
```bash
curl "http://localhost:8001/ssi-proxy/vn100-group"
```

**Response:**
```json
{
  "success": true,
  "api_endpoint": "vn100-group",
  "symbol": null,
  "data": [
    {
      "stock_symbol": "ACB",
      "company_name_vi": "Ngân hàng Thương mại Cổ phần Á Châu",
      "company_name_en": "Asia Commercial Bank",
      "exchange": "HOSE",
      "sector": "Ngân hàng",
      "matched_price": 25.8,
      "price_change": 0.3,
      "price_change_percent": 1.18,
      "isin": "VN000000ACB",
      "board_id": "HOSE",
      "admin_status": "ACTIVE",
      "ca_status": "NORMAL",
      "ceiling": 28.0,
      "floor": 23.0,
      "ref_price": 25.5,
      "par_value": 10000,
      "trading_unit": 100,
      "contract_multiplier": 1,
      "prior_close_price": 25.5,
      "product_id": "S1STOST",
      "last_mf_seq": 12345,
      "remain_foreign_qtty": 500000,
      "best1_bid": 25.7,
      "best1_bid_vol": 10000,
      "best1_offer": 25.8,
      "best1_offer_vol": 15000,
      "best2_bid": 25.6,
      "best2_bid_vol": 20000,
      "best2_offer": 25.9,
      "best2_offer_vol": 25000,
      "best3_bid": 25.5,
      "best3_bid_vol": 30000,
      "best3_offer": 26.0,
      "best3_offer_vol": 35000,
      "expected_last_update": 1728259200,
      "expected_matched_price": 25.8,
      "expected_matched_volume": 1200000,
      "expected_price_change": 0.3,
      "expected_price_change_percent": 1.18,
      "last_me_seq": 54321,
      "avg_price": 25.6,
      "highest": 26.0,
      "lowest": 25.2,
      "matched_volume": 1000000,
      "nm_total_traded_qty": 1000000,
      "nm_total_traded_value": 25800000,
      "open_price": 25.5,
      "stock_sd_vol": 0,
      "stock_vol": 1000000,
      "stock_bu_vol": 0,
      "buy_foreign_qtty": 100000,
      "buy_foreign_value": 2580000,
      "last_mt_seq": 98765,
      "sell_foreign_qtty": 50000,
      "sell_foreign_value": 1290000,
      "session": "AT",
      "odd_session": "PT",
      "session_pt": "PT",
      "odd_session_pt": "PT",
      "session_rt": "RT",
      "odd_session_rt": "RT",
      "odd_session_rt_start": 1728086400,
      "session_rt_start": 1728086400,
      "session_start": 1728086400,
      "odd_session_start": 1728086400,
      "exchange_session": "HOSE",
      "is_pre_session_price": false,
      "weight": 2.5,
      "market_cap": 25800000000
    }
  ],
  "timestamp": "2025-10-05T03:52:07.665280",
  "response_time_ms": 159.75,
  "raw_response": { ... }
}
```

## 🧪 Testing Endpoints

### Test SSI API Connectivity
```http
GET /ssi-proxy/test/{api_name}
```

**Parameters:**
- `api_name`: Tên API để test (stock-info, charts-history, vn100-group)

**Examples:**
```bash
# Test VN100 Group API
curl "http://localhost:8001/ssi-proxy/test/vn100-group"

# Test Stock Info API
curl "http://localhost:8001/ssi-proxy/test/stock-info"

# Test Charts History API
curl "http://localhost:8001/ssi-proxy/test/charts-history"
```

**Response:**
```json
{
  "success": true,
  "api": "vn100-group",
  "status": "connected",
  "data_preview": "{'code': 200, 'message': 'Success', 'data': [...]}",
  "timestamp": "2025-10-05T03:52:07.665280"
}
```

## 🔧 Management Commands

### Using SSI System Manager

```bash
# Start SSI Proxy only
./ssi_system_manager.sh start-proxy

# Start all services (Main API + SSI Proxy)
./ssi_system_manager.sh start

# Check status
./ssi_system_manager.sh status

# Test SSI Proxy endpoints
./ssi_system_manager.sh test-proxy

# View logs
./ssi_system_manager.sh logs-proxy

# Stop all services
./ssi_system_manager.sh stop
```

### Direct Docker Commands

```bash
# Start SSI Proxy service
docker compose up -d tracking_data_ssi_proxy

# Check logs
docker compose logs -f tracking_data_ssi_proxy

# Check status
docker compose ps tracking_data_ssi_proxy

# Stop service
docker compose stop tracking_data_ssi_proxy
```

## 📊 Performance Metrics

### Response Times (Typical)
- **VN100 Group API**: ~160ms
- **Stock Info API**: ~250ms
- **Charts History API**: ~200ms

### Data Volume
- **VN100 Group**: 100 components
- **Stock Info**: 3-10 records per request
- **Charts History**: 0-1000+ data points per request

## 🚨 Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Failed to fetch stock info: Connection timeout"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error in stock-info proxy: SSI API returned invalid data"
}
```

### Error Scenarios
1. **SSI API Unavailable**: Service returns 400 with connection error
2. **Invalid Parameters**: Service returns 422 with validation error
3. **Rate Limiting**: Service returns 429 with rate limit error
4. **Data Parsing Error**: Service returns 500 with parsing error

## 🔒 Security Considerations

### Headers Used
- **User-Agent**: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
- **Accept**: application/json, text/plain, */*
- **Referer**: https://iboard.ssi.com.vn/
- **Origin**: https://iboard.ssi.com.vn

### Rate Limiting
- **Default**: No built-in rate limiting
- **Recommendation**: Implement client-side rate limiting
- **SSI Limits**: Respect SSI API rate limits

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8001/health
```

### Service Status
```bash
docker compose ps tracking_data_ssi_proxy
```

### Logs Monitoring
```bash
docker compose logs -f tracking_data_ssi_proxy
```

## 🎯 Use Cases

### 1. Real-time Data Access
```bash
# Get latest VN100 data
curl "http://localhost:8001/ssi-proxy/vn100-group" | jq '.data[0:5]'
```

### 2. Development and Testing
```bash
# Test with different symbols
curl "http://localhost:8001/ssi-proxy/stock-info?symbol=VIC&from_date=01/10/2025&to_date=05/10/2025"
```

### 3. Data Analysis
```bash
# Get historical data for analysis
FROM_TS=$(date -v-7d +%s)
TO_TS=$(date +%s)
curl "http://localhost:8001/ssi-proxy/charts-history?symbol=ACB&resolution=1d&from_timestamp=$FROM_TS&to_timestamp=$TO_TS"
```

### 4. Integration Testing
```bash
# Test all endpoints
./ssi_system_manager.sh test-proxy
```

## 🔄 Integration with Main API

### Comparison

| Feature | Main API (Port 8000) | SSI Proxy (Port 8001) |
|---------|---------------------|----------------------|
| **Data Storage** | ✅ Database | ❌ No Storage |
| **Real-time** | ❌ Cached | ✅ Live Data |
| **Performance** | ⚡ Fast (cached) | 🐌 Slower (live) |
| **Data Volume** | 📊 Historical | 📊 Current |
| **Use Case** | Production | Development/Testing |

### Recommended Usage
- **Production**: Use Main API (port 8000) for stored data
- **Development**: Use SSI Proxy (port 8001) for real-time testing
- **Monitoring**: Use SSI Proxy for API health checks
- **Integration**: Use SSI Proxy for initial data exploration

---
**Last Updated**: 2025-10-05  
**Version**: 2.1.0  
**Status**: Production Ready ✅
