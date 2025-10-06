-- Migration Script: Extend Database Schema for Complete SSI API Data
-- Version: 2.0
-- Description: Extend existing schema to store 100% of SSI API data (112 fields)

-- =====================================================
-- PHASE 1: EXTEND EXISTING TABLES
-- =====================================================

-- Extend companies table
ALTER TABLE companies 
ADD COLUMN IF NOT EXISTS company_name_en VARCHAR(255),
ADD COLUMN IF NOT EXISTS isin VARCHAR(20),
ADD COLUMN IF NOT EXISTS board_id VARCHAR(20),
ADD COLUMN IF NOT EXISTS admin_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS ca_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS par_value INTEGER,
ADD COLUMN IF NOT EXISTS trading_unit INTEGER,
ADD COLUMN IF NOT EXISTS contract_multiplier INTEGER,
ADD COLUMN IF NOT EXISTS product_id VARCHAR(20);

-- Extend stock_statistics table
ALTER TABLE stock_statistics 
ADD COLUMN IF NOT EXISTS ceiling_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS floor_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS ref_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS avg_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS close_price_adjusted DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS total_match_vol BIGINT,
ADD COLUMN IF NOT EXISTS total_deal_val BIGINT,
ADD COLUMN IF NOT EXISTS total_deal_vol BIGINT,
ADD COLUMN IF NOT EXISTS foreign_buy_vol_total BIGINT,
ADD COLUMN IF NOT EXISTS foreign_current_room BIGINT,
ADD COLUMN IF NOT EXISTS foreign_sell_vol_total BIGINT,
ADD COLUMN IF NOT EXISTS foreign_buy_val_total BIGINT,
ADD COLUMN IF NOT EXISTS foreign_sell_val_total BIGINT,
ADD COLUMN IF NOT EXISTS foreign_buy_vol_matched BIGINT,
ADD COLUMN IF NOT EXISTS foreign_buy_vol_deal BIGINT,
ADD COLUMN IF NOT EXISTS total_buy_trade INTEGER,
ADD COLUMN IF NOT EXISTS total_buy_trade_vol BIGINT,
ADD COLUMN IF NOT EXISTS total_sell_trade INTEGER,
ADD COLUMN IF NOT EXISTS total_sell_trade_vol BIGINT,
ADD COLUMN IF NOT EXISTS net_buy_sell_vol BIGINT,
ADD COLUMN IF NOT EXISTS net_buy_sell_val BIGINT,
ADD COLUMN IF NOT EXISTS close_raw DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS open_raw DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS high_raw DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS low_raw DECIMAL(15,4);

-- Extend stock_prices table
ALTER TABLE stock_prices 
ADD COLUMN IF NOT EXISTS status VARCHAR(20),
ADD COLUMN IF NOT EXISTS next_time TIMESTAMP;

-- Extend index_components table
ALTER TABLE index_components 
ADD COLUMN IF NOT EXISTS isin VARCHAR(20),
ADD COLUMN IF NOT EXISTS board_id VARCHAR(20),
ADD COLUMN IF NOT EXISTS admin_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS ca_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS ceiling DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS floor DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS ref_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS par_value INTEGER,
ADD COLUMN IF NOT EXISTS trading_unit INTEGER,
ADD COLUMN IF NOT EXISTS contract_multiplier INTEGER,
ADD COLUMN IF NOT EXISTS prior_close_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS product_id VARCHAR(20),
ADD COLUMN IF NOT EXISTS last_mf_seq BIGINT,
ADD COLUMN IF NOT EXISTS remain_foreign_qtty BIGINT,
ADD COLUMN IF NOT EXISTS best1_bid DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS best1_bid_vol BIGINT,
ADD COLUMN IF NOT EXISTS best1_offer DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS best1_offer_vol BIGINT,
ADD COLUMN IF NOT EXISTS best2_bid DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS best2_bid_vol BIGINT,
ADD COLUMN IF NOT EXISTS best2_offer DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS best2_offer_vol BIGINT,
ADD COLUMN IF NOT EXISTS best3_bid DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS best3_bid_vol BIGINT,
ADD COLUMN IF NOT EXISTS best3_offer DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS best3_offer_vol BIGINT,
ADD COLUMN IF NOT EXISTS expected_last_update TIMESTAMP,
ADD COLUMN IF NOT EXISTS expected_matched_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS expected_matched_volume BIGINT,
ADD COLUMN IF NOT EXISTS expected_price_change DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS expected_price_change_percent DECIMAL(8,4),
ADD COLUMN IF NOT EXISTS last_me_seq BIGINT,
ADD COLUMN IF NOT EXISTS avg_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS highest DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS lowest DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS matched_volume BIGINT,
ADD COLUMN IF NOT EXISTS nm_total_traded_qty BIGINT,
ADD COLUMN IF NOT EXISTS nm_total_traded_value BIGINT,
ADD COLUMN IF NOT EXISTS open_price DECIMAL(15,4),
ADD COLUMN IF NOT EXISTS stock_sd_vol BIGINT,
ADD COLUMN IF NOT EXISTS stock_vol BIGINT,
ADD COLUMN IF NOT EXISTS stock_bu_vol BIGINT,
ADD COLUMN IF NOT EXISTS buy_foreign_qtty BIGINT,
ADD COLUMN IF NOT EXISTS buy_foreign_value BIGINT,
ADD COLUMN IF NOT EXISTS last_mt_seq BIGINT,
ADD COLUMN IF NOT EXISTS sell_foreign_qtty BIGINT,
ADD COLUMN IF NOT EXISTS sell_foreign_value BIGINT,
ADD COLUMN IF NOT EXISTS session VARCHAR(20),
ADD COLUMN IF NOT EXISTS odd_session VARCHAR(20),
ADD COLUMN IF NOT EXISTS session_pt VARCHAR(20),
ADD COLUMN IF NOT EXISTS odd_session_pt VARCHAR(20),
ADD COLUMN IF NOT EXISTS session_rt VARCHAR(20),
ADD COLUMN IF NOT EXISTS odd_session_rt VARCHAR(20),
ADD COLUMN IF NOT EXISTS odd_session_rt_start TIMESTAMP,
ADD COLUMN IF NOT EXISTS session_rt_start TIMESTAMP,
ADD COLUMN IF NOT EXISTS session_start TIMESTAMP,
ADD COLUMN IF NOT EXISTS odd_session_start TIMESTAMP,
ADD COLUMN IF NOT EXISTS exchange_session VARCHAR(20),
ADD COLUMN IF NOT EXISTS is_pre_session_price BOOLEAN;

-- =====================================================
-- PHASE 2: CREATE NEW TABLES
-- =====================================================

-- Create order_book table
CREATE TABLE IF NOT EXISTS order_book (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    bid_price DECIMAL(15,4),
    bid_volume BIGINT,
    offer_price DECIMAL(15,4),
    offer_volume BIGINT,
    level INTEGER NOT NULL, -- 1, 2, 3 for best1, best2, best3
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (symbol) REFERENCES companies(symbol)
);

-- Create foreign_trading table
CREATE TABLE IF NOT EXISTS foreign_trading (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    buy_volume BIGINT,
    buy_value BIGINT,
    sell_volume BIGINT,
    sell_value BIGINT,
    net_volume BIGINT,
    net_value BIGINT,
    current_room BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, date),
    FOREIGN KEY (symbol) REFERENCES companies(symbol)
);

-- Create session_info table
CREATE TABLE IF NOT EXISTS session_info (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    session_type VARCHAR(20),
    odd_session VARCHAR(20),
    session_pt VARCHAR(20),
    odd_session_pt VARCHAR(20),
    session_rt VARCHAR(20),
    odd_session_rt VARCHAR(20),
    odd_session_rt_start TIMESTAMP,
    session_rt_start TIMESTAMP,
    session_start TIMESTAMP,
    odd_session_start TIMESTAMP,
    exchange_session VARCHAR(20),
    is_pre_session_price BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(symbol, date),
    FOREIGN KEY (symbol) REFERENCES companies(symbol)
);

-- =====================================================
-- PHASE 3: CREATE INDEXES
-- =====================================================

-- Performance indexes for new tables
CREATE INDEX IF NOT EXISTS idx_order_book_symbol_timestamp ON order_book(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_order_book_timestamp ON order_book(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_foreign_trading_symbol_date ON foreign_trading(symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_foreign_trading_date ON foreign_trading(date DESC);
CREATE INDEX IF NOT EXISTS idx_session_info_symbol_date ON session_info(symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_session_info_date ON session_info(date DESC);

-- Additional indexes for extended columns
CREATE INDEX IF NOT EXISTS idx_companies_isin ON companies(isin);
CREATE INDEX IF NOT EXISTS idx_companies_board_id ON companies(board_id);
CREATE INDEX IF NOT EXISTS idx_stock_statistics_ceiling_floor ON stock_statistics(ceiling_price, floor_price);
CREATE INDEX IF NOT EXISTS idx_stock_statistics_foreign ON stock_statistics(foreign_buy_vol_total, foreign_sell_vol_total);
CREATE INDEX IF NOT EXISTS idx_index_components_best_bid_offer ON index_components(best1_bid, best1_offer);

-- =====================================================
-- PHASE 4: CONVERT TO HYPERTABLES (TimescaleDB)
-- =====================================================

-- Convert order_book to hypertable
SELECT create_hypertable('order_book', 'timestamp', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);

-- =====================================================
-- PHASE 5: UPDATE CONSTRAINTS
-- =====================================================

-- Update unique constraints for index_components
ALTER TABLE index_components DROP CONSTRAINT IF EXISTS index_components_index_name_symbol_last_update_key;
ALTER TABLE index_components ADD CONSTRAINT index_components_index_name_symbol_last_update_key 
    UNIQUE (index_name, symbol, last_update);

-- =====================================================
-- PHASE 6: CREATE VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for complete stock information
CREATE OR REPLACE VIEW stock_complete_info AS
SELECT 
    c.symbol,
    c.company_name,
    c.company_name_en,
    c.sector,
    c.exchange,
    c.isin,
    c.market_cap,
    s.date,
    s.current_price,
    s.change_amount,
    s.change_percent,
    s.volume,
    s.value,
    s.high_price,
    s.low_price,
    s.open_price,
    s.close_price,
    s.ceiling_price,
    s.floor_price,
    s.ref_price,
    s.avg_price,
    s.foreign_buy_vol_total,
    s.foreign_sell_vol_total,
    s.net_buy_sell_vol,
    s.net_buy_sell_val
FROM companies c
LEFT JOIN stock_statistics s ON c.symbol = s.symbol
WHERE s.date = (SELECT MAX(date) FROM stock_statistics WHERE symbol = c.symbol);

-- View for VN100 components with complete data
CREATE OR REPLACE VIEW vn100_complete AS
SELECT 
    ic.index_name,
    ic.symbol,
    c.company_name,
    c.company_name_en,
    ic.current_price,
    ic.change_amount,
    ic.change_percent,
    ic.weight,
    ic.market_cap,
    ic.best1_bid,
    ic.best1_offer,
    ic.best1_bid_vol,
    ic.best1_offer_vol,
    ic.avg_price,
    ic.highest,
    ic.lowest,
    ic.nm_total_traded_qty,
    ic.nm_total_traded_value,
    ic.buy_foreign_qtty,
    ic.sell_foreign_qtty,
    ic.session,
    ic.is_pre_session_price,
    ic.last_update
FROM index_components ic
JOIN companies c ON ic.symbol = c.symbol
WHERE ic.index_name = 'VN100'
ORDER BY ic.weight DESC NULLS LAST;

-- =====================================================
-- PHASE 7: GRANT PERMISSIONS
-- =====================================================

-- Grant permissions to postgres user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Log migration completion
INSERT INTO migration_log (version, description, executed_at) 
VALUES ('2.0', 'Extended database schema for complete SSI API data', NOW())
ON CONFLICT DO NOTHING;

-- Create migration_log table if it doesn't exist
CREATE TABLE IF NOT EXISTS migration_log (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    executed_at TIMESTAMP DEFAULT NOW()
);
