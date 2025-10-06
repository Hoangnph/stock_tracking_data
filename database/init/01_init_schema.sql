-- Database initialization script for tracking_data
-- This script creates the database schema for SSI stock tracking system

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    exchange VARCHAR(10) DEFAULT 'HOSE',
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create stock_prices table (Time-series data)
CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) REFERENCES companies(symbol),
    timestamp TIMESTAMP NOT NULL,
    resolution VARCHAR(10) NOT NULL, -- '1m', '1h', '1d'
    open_price DECIMAL(15,4),
    high_price DECIMAL(15,4),
    low_price DECIMAL(15,4),
    close_price DECIMAL(15,4),
    volume BIGINT,
    value BIGINT, -- Giá trị giao dịch
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, timestamp, resolution)
);

-- Create stock_statistics table
CREATE TABLE IF NOT EXISTS stock_statistics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) REFERENCES companies(symbol),
    date DATE NOT NULL,
    current_price DECIMAL(15,4),
    change_amount DECIMAL(15,4),
    change_percent DECIMAL(8,4),
    volume BIGINT,
    value BIGINT,
    high_price DECIMAL(15,4),
    low_price DECIMAL(15,4),
    open_price DECIMAL(15,4),
    close_price DECIMAL(15,4),
    pe_ratio DECIMAL(8,2),
    pb_ratio DECIMAL(8,2),
    eps DECIMAL(15,4),
    dividend_yield DECIMAL(8,4),
    market_cap BIGINT,
    page INTEGER,
    page_size INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, date)
);

-- Create market_indices table
CREATE TABLE IF NOT EXISTS market_indices (
    id SERIAL PRIMARY KEY,
    index_name VARCHAR(50) NOT NULL,
    index_value DECIMAL(15,4),
    change_amount DECIMAL(15,4),
    change_percent DECIMAL(8,4),
    total_market_cap BIGINT,
    total_components INTEGER,
    calculation_method VARCHAR(100),
    last_update TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(index_name, last_update)
);

-- Create index_components table
CREATE TABLE IF NOT EXISTS index_components (
    id SERIAL PRIMARY KEY,
    index_name VARCHAR(50) NOT NULL,
    symbol VARCHAR(10) REFERENCES companies(symbol),
    weight DECIMAL(8,4), -- Trọng số trong chỉ số
    market_cap BIGINT,
    current_price DECIMAL(15,4),
    change_amount DECIMAL(15,4),
    change_percent DECIMAL(8,4),
    sector VARCHAR(100),
    exchange VARCHAR(10),
    last_update TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(index_name, symbol, last_update)
);

-- Convert stock_prices to hypertable for time-series optimization
-- First drop the unique constraint that conflicts with partitioning
ALTER TABLE stock_prices DROP CONSTRAINT IF EXISTS stock_prices_symbol_timestamp_resolution_key;
SELECT create_hypertable('stock_prices', 'timestamp', chunk_time_interval => INTERVAL '1 day');

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_time ON stock_prices(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stock_prices_time_symbol ON stock_prices(timestamp DESC, symbol);
CREATE INDEX IF NOT EXISTS idx_stock_statistics_symbol_date ON stock_statistics(symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_index_components_index_symbol ON index_components(index_name, symbol);
CREATE INDEX IF NOT EXISTS idx_companies_symbol ON companies(symbol);
CREATE INDEX IF NOT EXISTS idx_market_indices_name ON market_indices(index_name);

-- Create partial index for recent data
CREATE INDEX IF NOT EXISTS idx_stock_prices_recent ON stock_prices(symbol, timestamp DESC) 
WHERE timestamp > NOW() - INTERVAL '30 days';

-- Create materialized view for daily summary
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_summary AS
SELECT 
    symbol,
    DATE(timestamp) as date,
    AVG(close_price) as avg_price,
    MAX(high_price) as day_high,
    MIN(low_price) as day_low,
    SUM(volume) as total_volume,
    SUM(value) as total_value
FROM stock_prices
WHERE resolution = '1d'
GROUP BY symbol, DATE(timestamp);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_daily_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_summary;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for testing
INSERT INTO companies (symbol, company_name, sector, industry, exchange) VALUES
('ACB', 'Ngân hàng TMCP Á Châu', 'Ngân hàng', 'Dịch vụ tài chính', 'HOSE'),
('PDR', 'Công ty Cổ phần Phát triển Bất động sản Phát Đạt', 'Bất động sản', 'Phát triển bất động sản', 'HOSE'),
('VIC', 'Tập đoàn Vingroup', 'Bất động sản', 'Phát triển bất động sản', 'HOSE'),
('VCB', 'Ngân hàng TMCP Ngoại thương Việt Nam', 'Ngân hàng', 'Dịch vụ tài chính', 'HOSE')
ON CONFLICT (symbol) DO NOTHING;

-- Insert sample market index
INSERT INTO market_indices (index_name, index_value, change_amount, change_percent, total_market_cap, total_components, calculation_method, last_update) VALUES
('VN100', 1250.45, 12.35, 1.00, 1250000000000000, 100, 'Free Float Market Cap Weighted', NOW())
ON CONFLICT (index_name, last_update) DO NOTHING;

-- Insert sample index components
INSERT INTO index_components (index_name, symbol, weight, market_cap, current_price, change_amount, change_percent, sector, exchange, last_update) VALUES
('VN100', 'VIC', 8.5, 106250000000000, 85000, 1000, 1.19, 'Bất động sản', 'HOSE', NOW()),
('VN100', 'VCB', 7.2, 90000000000000, 90000, 500, 0.56, 'Ngân hàng', 'HOSE', NOW()),
('VN100', 'ACB', 2.1, 26250000000000, 28500, 500, 1.79, 'Ngân hàng', 'HOSE', NOW()),
('VN100', 'PDR', 1.8, 22500000000000, 25000, 200, 0.81, 'Bất động sản', 'HOSE', NOW())
ON CONFLICT (index_name, symbol, last_update) DO NOTHING;
