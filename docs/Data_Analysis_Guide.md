# 📊 DATA ANALYSIS GUIDE & QUERY EXAMPLES

## 🎯 TỔNG QUAN

Tài liệu này cung cấp hướng dẫn chi tiết để phân tích dữ liệu chứng khoán từ hệ thống Stock Tracking Data, bao gồm các query SQL mẫu, phân tích kỹ thuật, và các use cases thực tế.

## 📊 DATABASE SCHEMA OVERVIEW

### **🗄️ Main Tables**
```sql
-- Xem cấu trúc các bảng chính
\d stock_statistics
\d companies
\d market_indices
\d index_components
```

### **📈 Key Fields for Analysis**
| Table | Key Fields | Purpose |
|-------|------------|---------|
| **stock_statistics** | symbol, date, current_price, volume, value, open_price, high_price, low_price, close_price | Price và volume data |
| **companies** | symbol, company_name, sector, market_cap | Company information |
| **market_indices** | index_name, date, index_value, change_percent | Market index data |
| **index_components** | symbol, weight, sector, market_cap | VN100 components |

## 🔍 BASIC DATA EXPLORATION

### **📊 System Overview Queries**

#### **1. Tổng quan dữ liệu**
```sql
-- Tổng số records và symbols
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT symbol) as unique_symbols,
    MIN(date) as earliest_date,
    MAX(date) as latest_date
FROM stock_statistics;
```

#### **2. Thống kê theo symbol**
```sql
-- Top 10 symbols có nhiều dữ liệu nhất
SELECT 
    symbol,
    COUNT(*) as record_count,
    MIN(date) as first_date,
    MAX(date) as last_date,
    AVG(current_price) as avg_price,
    MAX(current_price) as max_price,
    MIN(current_price) as min_price
FROM stock_statistics 
GROUP BY symbol 
ORDER BY record_count DESC 
LIMIT 10;
```

#### **3. Thống kê theo thời gian**
```sql
-- Dữ liệu theo năm
SELECT 
    EXTRACT(YEAR FROM date) as year,
    COUNT(*) as records,
    COUNT(DISTINCT symbol) as active_symbols,
    AVG(current_price) as avg_price,
    SUM(volume) as total_volume,
    SUM(value) as total_value
FROM stock_statistics 
GROUP BY EXTRACT(YEAR FROM date)
ORDER BY year;
```

## 📈 TECHNICAL ANALYSIS QUERIES

### **📊 Price Analysis**

#### **1. Price Trends**
```sql
-- Xu hướng giá của một symbol cụ thể
SELECT 
    date,
    current_price,
    open_price,
    high_price,
    low_price,
    close_price,
    change_amount,
    change_percent,
    volume,
    value
FROM stock_statistics 
WHERE symbol = 'ACB' 
  AND date >= '2025-01-01'
ORDER BY date DESC;
```

#### **2. Price Volatility**
```sql
-- Độ biến động giá (volatility)
SELECT 
    symbol,
    AVG(current_price) as avg_price,
    STDDEV(current_price) as price_volatility,
    MIN(current_price) as min_price,
    MAX(current_price) as max_price,
    (MAX(current_price) - MIN(current_price)) / AVG(current_price) * 100 as price_range_percent
FROM stock_statistics 
WHERE date >= '2025-01-01'
GROUP BY symbol 
ORDER BY price_volatility DESC 
LIMIT 10;
```

#### **3. Price Performance**
```sql
-- Hiệu suất giá theo thời gian
WITH price_performance AS (
    SELECT 
        symbol,
        date,
        current_price,
        LAG(current_price) OVER (PARTITION BY symbol ORDER BY date) as prev_price,
        (current_price - LAG(current_price) OVER (PARTITION BY symbol ORDER BY date)) / 
        LAG(current_price) OVER (PARTITION BY symbol ORDER BY date) * 100 as daily_return
    FROM stock_statistics 
    WHERE date >= '2025-01-01'
)
SELECT 
    symbol,
    AVG(daily_return) as avg_daily_return,
    STDDEV(daily_return) as return_volatility,
    COUNT(CASE WHEN daily_return > 0 THEN 1 END) as positive_days,
    COUNT(CASE WHEN daily_return < 0 THEN 1 END) as negative_days
FROM price_performance 
WHERE daily_return IS NOT NULL
GROUP BY symbol 
ORDER BY avg_daily_return DESC 
LIMIT 10;
```

### **📊 Volume Analysis**

#### **1. Volume Trends**
```sql
-- Xu hướng volume giao dịch
SELECT 
    date,
    SUM(volume) as total_volume,
    SUM(value) as total_value,
    COUNT(DISTINCT symbol) as active_symbols,
    AVG(volume) as avg_volume_per_symbol
FROM stock_statistics 
WHERE date >= '2025-01-01'
GROUP BY date 
ORDER BY date DESC;
```

#### **2. Volume vs Price Correlation**
```sql
-- Tương quan giữa volume và giá
SELECT 
    symbol,
    CORR(volume, current_price) as volume_price_correlation,
    CORR(volume, change_percent) as volume_change_correlation,
    AVG(volume) as avg_volume,
    AVG(current_price) as avg_price
FROM stock_statistics 
WHERE date >= '2025-01-01'
GROUP BY symbol 
HAVING COUNT(*) > 100
ORDER BY ABS(volume_price_correlation) DESC 
LIMIT 10;
```

#### **3. Unusual Volume Activity**
```sql
-- Hoạt động volume bất thường
WITH volume_stats AS (
    SELECT 
        symbol,
        AVG(volume) as avg_volume,
        STDDEV(volume) as volume_stddev
    FROM stock_statistics 
    WHERE date >= '2025-01-01'
    GROUP BY symbol
)
SELECT 
    s.symbol,
    s.date,
    s.volume,
    s.current_price,
    s.change_percent,
    (s.volume - vs.avg_volume) / vs.volume_stddev as volume_z_score
FROM stock_statistics s
JOIN volume_stats vs ON s.symbol = vs.symbol
WHERE s.date >= '2025-01-01'
  AND ABS((s.volume - vs.avg_volume) / vs.volume_stddev) > 2
ORDER BY volume_z_score DESC 
LIMIT 20;
```

## 📊 MARKET ANALYSIS QUERIES

### **📈 Market Indices Analysis**

#### **1. VN100 Performance**
```sql
-- Hiệu suất VN100 theo thời gian
SELECT 
    date,
    index_value,
    change_percent,
    LAG(index_value) OVER (ORDER BY date) as prev_index_value,
    (index_value - LAG(index_value) OVER (ORDER BY date)) / 
    LAG(index_value) OVER (ORDER BY date) * 100 as daily_change
FROM market_indices 
WHERE index_name = 'VN100'
  AND date >= '2025-01-01'
ORDER BY date DESC;
```

#### **2. Sector Performance**
```sql
-- Hiệu suất theo sector
SELECT 
    c.sector,
    COUNT(DISTINCT s.symbol) as symbol_count,
    AVG(s.current_price) as avg_price,
    AVG(s.change_percent) as avg_change_percent,
    SUM(s.volume) as total_volume,
    SUM(s.value) as total_value
FROM stock_statistics s
JOIN companies c ON s.symbol = c.symbol
WHERE s.date >= '2025-01-01'
GROUP BY c.sector 
ORDER BY avg_change_percent DESC;
```

#### **3. Market Breadth**
```sql
-- Market breadth (số lượng symbols tăng/giảm)
SELECT 
    date,
    COUNT(*) as total_symbols,
    COUNT(CASE WHEN change_percent > 0 THEN 1 END) as advancing_symbols,
    COUNT(CASE WHEN change_percent < 0 THEN 1 END) as declining_symbols,
    COUNT(CASE WHEN change_percent = 0 THEN 1 END) as unchanged_symbols,
    ROUND(COUNT(CASE WHEN change_percent > 0 THEN 1 END) * 100.0 / COUNT(*), 2) as advance_percent
FROM stock_statistics 
WHERE date >= '2025-01-01'
GROUP BY date 
ORDER BY date DESC;
```

## 📊 ADVANCED ANALYTICS

### **📈 Moving Averages**

#### **1. Simple Moving Averages**
```sql
-- Moving averages (5, 10, 20, 50 days)
WITH moving_averages AS (
    SELECT 
        symbol,
        date,
        current_price,
        AVG(current_price) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) as sma_5,
        AVG(current_price) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) as sma_10,
        AVG(current_price) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) as sma_20,
        AVG(current_price) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) as sma_50
    FROM stock_statistics 
    WHERE symbol = 'ACB' 
      AND date >= '2025-01-01'
)
SELECT 
    date,
    current_price,
    ROUND(sma_5, 2) as sma_5,
    ROUND(sma_10, 2) as sma_10,
    ROUND(sma_20, 2) as sma_20,
    ROUND(sma_50, 2) as sma_50
FROM moving_averages 
ORDER BY date DESC 
LIMIT 20;
```

#### **2. Moving Average Crossovers**
```sql
-- Tín hiệu crossover (SMA 5 cắt SMA 20)
WITH moving_averages AS (
    SELECT 
        symbol,
        date,
        current_price,
        AVG(current_price) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) as sma_5,
        AVG(current_price) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) as sma_20
    FROM stock_statistics 
    WHERE date >= '2025-01-01'
),
crossover_signals AS (
    SELECT 
        symbol,
        date,
        current_price,
        sma_5,
        sma_20,
        LAG(sma_5) OVER (PARTITION BY symbol ORDER BY date) as prev_sma_5,
        LAG(sma_20) OVER (PARTITION BY symbol ORDER BY date) as prev_sma_20
    FROM moving_averages
)
SELECT 
    symbol,
    date,
    current_price,
    ROUND(sma_5, 2) as sma_5,
    ROUND(sma_20, 2) as sma_20,
    CASE 
        WHEN sma_5 > sma_20 AND prev_sma_5 <= prev_sma_20 THEN 'BUY'
        WHEN sma_5 < sma_20 AND prev_sma_5 >= prev_sma_20 THEN 'SELL'
        ELSE 'HOLD'
    END as signal
FROM crossover_signals 
WHERE date >= '2025-01-01'
  AND (sma_5 > sma_20 AND prev_sma_5 <= prev_sma_20) 
   OR (sma_5 < sma_20 AND prev_sma_5 >= prev_sma_20)
ORDER BY date DESC;
```

### **📊 Technical Indicators**

#### **1. RSI (Relative Strength Index)**
```sql
-- RSI calculation
WITH price_changes AS (
    SELECT 
        symbol,
        date,
        current_price,
        change_amount,
        CASE WHEN change_amount > 0 THEN change_amount ELSE 0 END as gain,
        CASE WHEN change_amount < 0 THEN ABS(change_amount) ELSE 0 END as loss
    FROM stock_statistics 
    WHERE symbol = 'ACB' 
      AND date >= '2025-01-01'
),
rsi_calculation AS (
    SELECT 
        symbol,
        date,
        current_price,
        AVG(gain) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
        ) as avg_gain,
        AVG(loss) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
        ) as avg_loss
    FROM price_changes
)
SELECT 
    date,
    current_price,
    ROUND(avg_gain, 2) as avg_gain,
    ROUND(avg_loss, 2) as avg_loss,
    ROUND(100 - (100 / (1 + (avg_gain / NULLIF(avg_loss, 0)))), 2) as rsi
FROM rsi_calculation 
ORDER BY date DESC 
LIMIT 20;
```

#### **2. Bollinger Bands**
```sql
-- Bollinger Bands calculation
WITH bollinger_bands AS (
    SELECT 
        symbol,
        date,
        current_price,
        AVG(current_price) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) as sma_20,
        STDDEV(current_price) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) as stddev_20
    FROM stock_statistics 
    WHERE symbol = 'ACB' 
      AND date >= '2025-01-01'
)
SELECT 
    date,
    current_price,
    ROUND(sma_20, 2) as middle_band,
    ROUND(sma_20 + (2 * stddev_20), 2) as upper_band,
    ROUND(sma_20 - (2 * stddev_20), 2) as lower_band,
    CASE 
        WHEN current_price > (sma_20 + (2 * stddev_20)) THEN 'OVERBOUGHT'
        WHEN current_price < (sma_20 - (2 * stddev_20)) THEN 'OVERSOLD'
        ELSE 'NEUTRAL'
    END as signal
FROM bollinger_bands 
ORDER BY date DESC 
LIMIT 20;
```

## 📊 PORTFOLIO ANALYSIS

### **📈 Portfolio Performance**

#### **1. Portfolio Returns**
```sql
-- Portfolio returns calculation
WITH portfolio_symbols AS (
    SELECT DISTINCT symbol 
    FROM stock_statistics 
    WHERE symbol IN ('ACB', 'VCB', 'VIC', 'VHM', 'HPG')
),
portfolio_returns AS (
    SELECT 
        s.symbol,
        s.date,
        s.current_price,
        LAG(s.current_price) OVER (PARTITION BY s.symbol ORDER BY s.date) as prev_price,
        (s.current_price - LAG(s.current_price) OVER (PARTITION BY s.symbol ORDER BY s.date)) / 
        LAG(s.current_price) OVER (PARTITION BY s.symbol ORDER BY s.date) * 100 as daily_return
    FROM stock_statistics s
    JOIN portfolio_symbols p ON s.symbol = p.symbol
    WHERE s.date >= '2025-01-01'
)
SELECT 
    date,
    AVG(daily_return) as portfolio_return,
    STDDEV(daily_return) as portfolio_volatility,
    COUNT(*) as symbols_count
FROM portfolio_returns 
WHERE daily_return IS NOT NULL
GROUP BY date 
ORDER BY date DESC 
LIMIT 20;
```

#### **2. Risk Metrics**
```sql
-- Risk metrics (Sharpe ratio, VaR)
WITH daily_returns AS (
    SELECT 
        symbol,
        date,
        (current_price - LAG(current_price) OVER (PARTITION BY symbol ORDER BY date)) / 
        LAG(current_price) OVER (PARTITION BY symbol ORDER BY date) * 100 as daily_return
    FROM stock_statistics 
    WHERE symbol = 'ACB' 
      AND date >= '2025-01-01'
),
risk_metrics AS (
    SELECT 
        symbol,
        AVG(daily_return) as avg_return,
        STDDEV(daily_return) as volatility,
        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY daily_return) as var_5_percent
    FROM daily_returns 
    WHERE daily_return IS NOT NULL
    GROUP BY symbol
)
SELECT 
    symbol,
    ROUND(avg_return, 4) as avg_daily_return,
    ROUND(volatility, 4) as daily_volatility,
    ROUND(avg_return / volatility, 4) as sharpe_ratio,
    ROUND(var_5_percent, 4) as var_5_percent
FROM risk_metrics;
```

## 📊 REAL-TIME ANALYSIS

### **📈 Live Market Analysis**

#### **1. Today's Market Summary**
```sql
-- Tóm tắt thị trường hôm nay
SELECT 
    COUNT(*) as total_symbols,
    COUNT(CASE WHEN change_percent > 0 THEN 1 END) as advancing_symbols,
    COUNT(CASE WHEN change_percent < 0 THEN 1 END) as declining_symbols,
    COUNT(CASE WHEN change_percent = 0 THEN 1 END) as unchanged_symbols,
    ROUND(AVG(change_percent), 2) as avg_change_percent,
    ROUND(SUM(volume), 0) as total_volume,
    ROUND(SUM(value), 0) as total_value
FROM stock_statistics 
WHERE date = CURRENT_DATE;
```

#### **2. Top Gainers and Losers**
```sql
-- Top gainers và losers hôm nay
(SELECT 
    'GAINER' as type,
    symbol,
    current_price,
    change_amount,
    change_percent,
    volume,
    value
FROM stock_statistics 
WHERE date = CURRENT_DATE 
  AND change_percent > 0
ORDER BY change_percent DESC 
LIMIT 10)
UNION ALL
(SELECT 
    'LOSER' as type,
    symbol,
    current_price,
    change_amount,
    change_percent,
    volume,
    value
FROM stock_statistics 
WHERE date = CURRENT_DATE 
  AND change_percent < 0
ORDER BY change_percent ASC 
LIMIT 10)
ORDER BY type, change_percent DESC;
```

#### **3. Volume Leaders**
```sql
-- Top volume leaders hôm nay
SELECT 
    symbol,
    current_price,
    change_percent,
    volume,
    value,
    ROUND(value / 1000000000, 2) as value_billion_vnd
FROM stock_statistics 
WHERE date = CURRENT_DATE 
ORDER BY volume DESC 
LIMIT 20;
```

## 📊 API INTEGRATION EXAMPLES

### **🔗 Using APIs for Analysis**

#### **1. Python Analysis Script**
```python
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# API base URL
API_BASE = "http://localhost:8000"

def get_stock_data(symbol, days=30):
    """Get stock data for analysis"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    url = f"{API_BASE}/stock-statistics"
    params = {
        'symbol': symbol,
        'from_date': start_date,
        'to_date': end_date,
        'limit': 1000
    }
    
    response = requests.get(url, params=params)
    return pd.DataFrame(response.json())

def calculate_technical_indicators(df):
    """Calculate technical indicators"""
    df['sma_5'] = df['current_price'].rolling(window=5).mean()
    df['sma_20'] = df['current_price'].rolling(window=20).mean()
    df['rsi'] = calculate_rsi(df['current_price'])
    return df

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Example usage
symbol = 'ACB'
data = get_stock_data(symbol, days=100)
data_with_indicators = calculate_technical_indicators(data)
print(data_with_indicators.tail())
```

#### **2. Real-time Monitoring Script**
```python
import requests
import time
from datetime import datetime

def monitor_market():
    """Monitor market in real-time"""
    while True:
        try:
            # Get market summary
            response = requests.get(f"{API_BASE}/market-summary")
            market_data = response.json()
            
            print(f"\n=== Market Update - {datetime.now()} ===")
            print(f"Total Symbols: {market_data['total_symbols']}")
            print(f"Advancing: {market_data['advancing_symbols']}")
            print(f"Declining: {market_data['declining_symbols']}")
            print(f"Average Change: {market_data['avg_change_percent']:.2f}%")
            
            time.sleep(60)  # Update every minute
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

# Run monitoring
monitor_market()
```

## 📊 DATA EXPORT AND VISUALIZATION

### **📈 Export Data for Analysis**

#### **1. Export to CSV**
```sql
-- Export data to CSV
COPY (
    SELECT 
        symbol,
        date,
        current_price,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        value,
        change_percent
    FROM stock_statistics 
    WHERE date >= '2025-01-01'
    ORDER BY symbol, date
) TO '/tmp/stock_data.csv' WITH CSV HEADER;
```

#### **2. Export to JSON**
```sql
-- Export data to JSON
SELECT json_agg(
    json_build_object(
        'symbol', symbol,
        'date', date,
        'price', current_price,
        'volume', volume,
        'change_percent', change_percent
    )
) as stock_data
FROM stock_statistics 
WHERE symbol = 'ACB' 
  AND date >= '2025-01-01'
ORDER BY date;
```

### **📊 Visualization Examples**

#### **1. Price Chart Data**
```sql
-- Data for price chart
SELECT 
    date,
    current_price as close,
    open_price as open,
    high_price as high,
    low_price as low,
    volume
FROM stock_statistics 
WHERE symbol = 'ACB' 
  AND date >= '2025-01-01'
ORDER BY date;
```

#### **2. Volume Chart Data**
```sql
-- Data for volume chart
SELECT 
    date,
    volume,
    value,
    current_price
FROM stock_statistics 
WHERE symbol = 'ACB' 
  AND date >= '2025-01-01'
ORDER BY date;
```

## 📊 PERFORMANCE OPTIMIZATION

### **⚡ Query Optimization Tips**

#### **1. Use Indexes**
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_stock_statistics_symbol_date ON stock_statistics(symbol, date);
CREATE INDEX CONCURRENTLY idx_stock_statistics_date ON stock_statistics(date);
CREATE INDEX CONCURRENTLY idx_stock_statistics_symbol ON stock_statistics(symbol);
```

#### **2. Use LIMIT and WHERE**
```sql
-- Always use LIMIT for large datasets
SELECT * FROM stock_statistics 
WHERE symbol = 'ACB' 
  AND date >= '2025-01-01'
ORDER BY date DESC 
LIMIT 100;
```

#### **3. Use EXPLAIN ANALYZE**
```sql
-- Analyze query performance
EXPLAIN ANALYZE 
SELECT symbol, AVG(current_price) 
FROM stock_statistics 
WHERE date >= '2025-01-01'
GROUP BY symbol;
```

## 📋 ANALYSIS CHECKLIST

### **✅ Daily Analysis**
- [ ] Market summary
- [ ] Top gainers/losers
- [ ] Volume leaders
- [ ] Market breadth
- [ ] Sector performance

### **✅ Weekly Analysis**
- [ ] Price trends
- [ ] Technical indicators
- [ ] Volume analysis
- [ ] Risk metrics
- [ ] Portfolio performance

### **✅ Monthly Analysis**
- [ ] Long-term trends
- [ ] Sector rotation
- [ ] Market cycles
- [ ] Correlation analysis
- [ ] Performance attribution

---

## 🎯 CONCLUSION

Tài liệu này cung cấp hướng dẫn chi tiết để phân tích dữ liệu chứng khoán từ hệ thống Stock Tracking Data. Các query và examples được thiết kế để:

- ✅ **Comprehensive Analysis**: Từ basic đến advanced analytics
- ✅ **Real-time Monitoring**: Live market analysis
- ✅ **Technical Indicators**: RSI, Moving Averages, Bollinger Bands
- ✅ **Portfolio Analysis**: Risk metrics và performance
- ✅ **API Integration**: Python scripts cho automation
- ✅ **Performance Optimization**: Query optimization tips

**Hệ thống cung cấp đầy đủ dữ liệu và tools để thực hiện phân tích chứng khoán chuyên nghiệp.**
