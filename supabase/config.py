#!/usr/bin/env python3
"""
Supabase Configuration
=====================

Configuration file for Supabase integration.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SupabaseConfig:
    """Configuration for Supabase connection"""
    url: str
    key: str
    service_role_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'SupabaseConfig':
        """Load configuration from environment variables"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
        
        return cls(
            url=url,
            key=key,
            service_role_key=service_role_key
        )


# Database table names
class TableNames:
    """Database table names"""
    STOCK_DATA = "stock_data"
    VN100_SYMBOLS = "vn100_symbols"
    VNINDEX_DATA = "vnindex_data"
    DATA_SOURCES = "data_sources"


# Database schema
class DatabaseSchema:
    """Database schema definitions"""
    
    STOCK_DATA_TABLE = """
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
    """
    
    VN100_SYMBOLS_TABLE = """
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
    """
    
    VNINDEX_DATA_TABLE = """
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
    """
    
    DATA_SOURCES_TABLE = """
    CREATE TABLE IF NOT EXISTS data_sources (
        id BIGSERIAL PRIMARY KEY,
        source_name VARCHAR(100) NOT NULL,
        source_type VARCHAR(50) NOT NULL,
        last_updated TIMESTAMP WITH TIME ZONE,
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # Indexes for better performance
    INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_stock_data_symbol ON stock_data(symbol);",
        "CREATE INDEX IF NOT EXISTS idx_stock_data_date ON stock_data(date);",
        "CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date ON stock_data(symbol, date);",
        "CREATE INDEX IF NOT EXISTS idx_vnindex_data_date ON vnindex_data(date);",
    ]


# Batch upload configuration
class BatchConfig:
    """Configuration for batch uploads"""
    BATCH_SIZE = 1000  # Records per batch
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    CONCURRENT_BATCHES = 5  # Number of concurrent batch uploads
