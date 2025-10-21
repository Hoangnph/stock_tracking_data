-- Supabase Database Schema
-- ========================
-- Run this SQL in Supabase SQL Editor to create the required tables

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Stock Data Table
-- Stores OHLCV data for all stocks
CREATE TABLE IF NOT EXISTS stock_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(15,2),
    high DECIMAL(15,2),
    low DECIMAL(15,2),
    close DECIMAL(15,2),
    volume BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, date)
);

-- VN100 Symbols Table
-- Stores VN100 symbol information
CREATE TABLE IF NOT EXISTS vn100_symbols (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- VN-Index Data Table
-- Stores VN-Index OHLCV data
CREATE TABLE IF NOT EXISTS vnindex_data (
    id BIGSERIAL PRIMARY KEY,
    date DATE PRIMARY KEY,
    open DECIMAL(15,2),
    high DECIMAL(15,2),
    low DECIMAL(15,2),
    close DECIMAL(15,2),
    volume BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data Sources Table
-- Tracks data source information
CREATE TABLE IF NOT EXISTS data_sources (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Indexes for Better Performance
CREATE INDEX IF NOT EXISTS idx_stock_data_symbol ON stock_data(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_data_date ON stock_data(date);
CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date ON stock_data(symbol, date);
CREATE INDEX IF NOT EXISTS idx_vnindex_data_date ON vnindex_data(date);
CREATE INDEX IF NOT EXISTS idx_vn100_symbols_active ON vn100_symbols(is_active);

-- Create Updated At Trigger Function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create Triggers for Updated At
CREATE TRIGGER update_stock_data_updated_at 
    BEFORE UPDATE ON stock_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vn100_symbols_updated_at 
    BEFORE UPDATE ON vn100_symbols 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vnindex_data_updated_at 
    BEFORE UPDATE ON vnindex_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_sources_updated_at 
    BEFORE UPDATE ON data_sources 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert Initial Data Sources
INSERT INTO data_sources (source_name, source_type, status) VALUES
('SSI API', 'stock_data', 'active'),
('SSI Charts History API', 'vnindex_data', 'active'),
('SSI VN100 API', 'vn100_symbols', 'active')
ON CONFLICT DO NOTHING;

-- Create Views for Common Queries
CREATE OR REPLACE VIEW stock_data_summary AS
SELECT 
    symbol,
    COUNT(*) as total_records,
    MIN(date) as first_date,
    MAX(date) as last_date,
    AVG(close) as avg_close_price,
    MAX(volume) as max_volume
FROM stock_data
GROUP BY symbol;

CREATE OR REPLACE VIEW vnindex_summary AS
SELECT 
    COUNT(*) as total_records,
    MIN(date) as first_date,
    MAX(date) as last_date,
    AVG(close) as avg_close_price,
    MAX(volume) as max_volume
FROM vnindex_data;

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE stock_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE vn100_symbols ENABLE ROW LEVEL SECURITY;
ALTER TABLE vnindex_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sources ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Allow public read access" ON stock_data FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON vn100_symbols FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON vnindex_data FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON data_sources FOR SELECT USING (true);

-- Create policies for authenticated users to insert/update
CREATE POLICY "Allow authenticated insert" ON stock_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated update" ON stock_data FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated insert" ON vn100_symbols FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated update" ON vn100_symbols FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated insert" ON vnindex_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated update" ON vnindex_data FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated insert" ON data_sources FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Allow authenticated update" ON data_sources FOR UPDATE USING (auth.role() = 'authenticated');
