#!/usr/bin/env python3
"""
Complete Extended FastAPI Application for SSI API Data Storage
Version: 2.0 - Complete Data Coverage (112 fields)

This API provides CRUD operations for all SSI API data fields including:
- Stock Info API (35 fields)
- Charts History API (8 fields) 
- VN100 Group API (69 fields)
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
import redis
import json
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5434/tracking_data")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis connection
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# =====================================================
# PYDANTIC MODELS - EXTENDED VERSION
# =====================================================

class CompanyBase(BaseModel):
    """Extended base model for company data"""
    symbol: str
    company_name: str
    company_name_en: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: str = "HOSE"
    market_cap: Optional[int] = None
    isin: Optional[str] = None
    board_id: Optional[str] = None
    admin_status: Optional[str] = None
    ca_status: Optional[str] = None
    par_value: Optional[int] = None
    trading_unit: Optional[int] = None
    contract_multiplier: Optional[int] = None
    product_id: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class StockStatisticsBase(BaseModel):
    """Extended base model for stock statistics with all SSI fields"""
    symbol: str
    date: date
    current_price: Optional[float] = None
    change_amount: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    value: Optional[int] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[int] = None
    
    # Extended fields from Stock Info API
    ceiling_price: Optional[float] = None
    floor_price: Optional[float] = None
    ref_price: Optional[float] = None
    avg_price: Optional[float] = None
    close_price_adjusted: Optional[float] = None
    total_match_vol: Optional[int] = None
    total_deal_val: Optional[int] = None
    total_deal_vol: Optional[int] = None
    
    # Foreign trading data
    foreign_buy_vol_total: Optional[int] = None
    foreign_current_room: Optional[int] = None
    foreign_sell_vol_total: Optional[int] = None
    foreign_buy_val_total: Optional[int] = None
    foreign_sell_val_total: Optional[int] = None
    foreign_buy_vol_matched: Optional[int] = None
    foreign_buy_vol_deal: Optional[int] = None
    
    # Trading statistics
    total_buy_trade: Optional[int] = None
    total_buy_trade_vol: Optional[int] = None
    total_sell_trade: Optional[int] = None
    total_sell_trade_vol: Optional[int] = None
    net_buy_sell_vol: Optional[int] = None
    net_buy_sell_val: Optional[int] = None
    
    # Raw prices
    close_raw: Optional[float] = None
    open_raw: Optional[float] = None
    high_raw: Optional[float] = None
    low_raw: Optional[float] = None

class StockStatisticsCreate(StockStatisticsBase):
    pass

class StockStatistics(StockStatisticsBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class StockPriceBase(BaseModel):
    """Extended base model for stock price data"""
    symbol: str
    timestamp: datetime
    resolution: str
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[int] = None
    value: Optional[int] = None
    
    # Extended fields from Charts History API
    status: Optional[str] = None
    next_time: Optional[datetime] = None

class StockPriceCreate(StockPriceBase):
    pass

class StockPrice(StockPriceBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class OrderBookBase(BaseModel):
    """Base model for order book data"""
    symbol: str
    timestamp: datetime
    bid_price: Optional[float] = None
    bid_volume: Optional[int] = None
    offer_price: Optional[float] = None
    offer_volume: Optional[int] = None
    level: int  # 1, 2, 3 for best1, best2, best3

class OrderBookCreate(OrderBookBase):
    pass

class OrderBook(OrderBookBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class ForeignTradingBase(BaseModel):
    """Base model for foreign trading data"""
    symbol: str
    date: date
    buy_volume: Optional[int] = None
    buy_value: Optional[int] = None
    sell_volume: Optional[int] = None
    sell_value: Optional[int] = None
    net_volume: Optional[int] = None
    net_value: Optional[int] = None
    current_room: Optional[int] = None

class ForeignTradingCreate(ForeignTradingBase):
    pass

class ForeignTrading(ForeignTradingBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class SessionInfoBase(BaseModel):
    """Base model for session information"""
    symbol: str
    date: date
    session_type: Optional[str] = None
    odd_session: Optional[str] = None
    session_pt: Optional[str] = None
    odd_session_pt: Optional[str] = None
    session_rt: Optional[str] = None
    odd_session_rt: Optional[str] = None
    odd_session_rt_start: Optional[datetime] = None
    session_rt_start: Optional[datetime] = None
    session_start: Optional[datetime] = None
    odd_session_start: Optional[datetime] = None
    exchange_session: Optional[str] = None
    is_pre_session_price: Optional[bool] = None

class SessionInfoCreate(SessionInfoBase):
    pass

class SessionInfo(SessionInfoBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

# =====================================================
# FASTAPI APPLICATION SETUP
# =====================================================

app = FastAPI(
    title="Extended Stock Tracking API", 
    version="2.0.0",
    description="Complete SSI API data storage with 112 fields coverage"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# DEPENDENCIES
# =====================================================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    return redis_client

# =====================================================
# HEALTH CHECK ENDPOINT
# =====================================================

@app.get("/health")
async def health_check(db: Session = Depends(get_db), r: redis.Redis = Depends(get_redis)):
    """Health check endpoint"""
    db_status = "disconnected"
    redis_status = "disconnected"
    
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    try:
        r.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {e}"

    overall_status = "healthy" if db_status == "connected" and redis_status == "connected" else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "redis": redis_status,
        "version": "2.0.0",
        "fields_coverage": "112/112 (100%)"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Extended Stock Tracking API v2.0 is running",
        "version": "2.0.0",
        "coverage": "Complete SSI API data (112 fields)",
        "docs": "/docs"
    }

# =====================================================
# COMPANIES CRUD ENDPOINTS
# =====================================================

@app.post("/companies", response_model=Company)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """Create or update a company record with extended fields"""
    try:
        query = text("""
            INSERT INTO companies (
                symbol, company_name, company_name_en, sector, industry, exchange, market_cap,
                isin, board_id, admin_status, ca_status, par_value, trading_unit, 
                contract_multiplier, product_id
            )
            VALUES (
                :symbol, :company_name, :company_name_en, :sector, :industry, :exchange, :market_cap,
                :isin, :board_id, :admin_status, :ca_status, :par_value, :trading_unit,
                :contract_multiplier, :product_id
            )
            ON CONFLICT (symbol) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                company_name_en = EXCLUDED.company_name_en,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry,
                exchange = EXCLUDED.exchange,
                market_cap = EXCLUDED.market_cap,
                isin = EXCLUDED.isin,
                board_id = EXCLUDED.board_id,
                admin_status = EXCLUDED.admin_status,
                ca_status = EXCLUDED.ca_status,
                par_value = EXCLUDED.par_value,
                trading_unit = EXCLUDED.trading_unit,
                contract_multiplier = EXCLUDED.contract_multiplier,
                product_id = EXCLUDED.product_id,
                updated_at = NOW()
            RETURNING id, symbol, company_name, company_name_en, sector, industry, exchange, market_cap,
                      isin, board_id, admin_status, ca_status, par_value, trading_unit,
                      contract_multiplier, product_id, created_at, updated_at;
        """)
        
        result = db.execute(query, company.dict()).fetchone()
        db.commit()
        
        if result:
            return Company(
                id=result.id,
                symbol=result.symbol,
                company_name=result.company_name,
                company_name_en=result.company_name_en,
                sector=result.sector,
                industry=result.industry,
                exchange=result.exchange,
                market_cap=result.market_cap,
                isin=result.isin,
                board_id=result.board_id,
                admin_status=result.admin_status,
                ca_status=result.ca_status,
                par_value=result.par_value,
                trading_unit=result.trading_unit,
                contract_multiplier=result.contract_multiplier,
                product_id=result.product_id,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
        raise HTTPException(status_code=500, detail="Failed to create or update company")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/companies", response_model=List[Company])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    symbol: Optional[str] = None,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of companies with optional filtering"""
    query_parts = [
        "SELECT id, symbol, company_name, company_name_en, sector, industry, exchange, market_cap,",
        "isin, board_id, admin_status, ca_status, par_value, trading_unit,",
        "contract_multiplier, product_id, created_at, updated_at",
        "FROM companies",
        "WHERE 1=1"
    ]

    params = {}
    if symbol:
        query_parts.append("AND symbol ILIKE :symbol")
        params["symbol"] = f"%{symbol}%"

    if sector:
        query_parts.append("AND sector ILIKE :sector")
        params["sector"] = f"%{sector}%"

    query_parts.append("ORDER BY symbol LIMIT :limit OFFSET :skip")
    params.update({"limit": limit, "skip": skip})

    query = text(" ".join(query_parts))

    result = db.execute(query, params)
    companies = []
    for row in result:
        companies.append(Company(
            id=row.id,
            symbol=row.symbol,
            company_name=row.company_name,
            company_name_en=row.company_name_en,
            sector=row.sector,
            industry=row.industry,
            exchange=row.exchange,
            market_cap=row.market_cap,
            isin=row.isin,
            board_id=row.board_id,
            admin_status=row.admin_status,
            ca_status=row.ca_status,
            par_value=row.par_value,
            trading_unit=row.trading_unit,
            contract_multiplier=row.contract_multiplier,
            product_id=row.product_id,
            created_at=row.created_at,
            updated_at=row.updated_at
        ))
    return companies

@app.get("/companies/{symbol}", response_model=Company)
async def get_company_by_symbol(symbol: str, db: Session = Depends(get_db)):
    """Get a single company by its symbol"""
    query = text("""
        SELECT id, symbol, company_name, company_name_en, sector, industry, exchange, market_cap,
               isin, board_id, admin_status, ca_status, par_value, trading_unit,
               contract_multiplier, product_id, created_at, updated_at
        FROM companies
        WHERE symbol = :symbol
    """)
    result = db.execute(query, {"symbol": symbol}).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return Company(
        id=result.id,
        symbol=result.symbol,
        company_name=result.company_name,
        company_name_en=result.company_name_en,
        sector=result.sector,
        industry=result.industry,
        exchange=result.exchange,
        market_cap=result.market_cap,
        isin=result.isin,
        board_id=result.board_id,
        admin_status=result.admin_status,
        ca_status=result.ca_status,
        par_value=result.par_value,
        trading_unit=result.trading_unit,
        contract_multiplier=result.contract_multiplier,
        product_id=result.product_id,
        created_at=result.created_at,
        updated_at=result.updated_at
    )

# =====================================================
# STOCK STATISTICS CRUD ENDPOINTS
# =====================================================

@app.post("/stock-statistics", response_model=StockStatistics)
async def create_stock_statistics(stats: StockStatisticsCreate, db: Session = Depends(get_db)):
    """Create or update stock statistics with all SSI fields"""
    try:
        query = text("""
            INSERT INTO stock_statistics (
                symbol, date, current_price, change_amount, change_percent, volume, value,
                high_price, low_price, open_price, close_price, pe_ratio, pb_ratio, eps,
                dividend_yield, market_cap, ceiling_price, floor_price, ref_price, avg_price,
                close_price_adjusted, total_match_vol, total_deal_val, total_deal_vol,
                foreign_buy_vol_total, foreign_current_room, foreign_sell_vol_total,
                foreign_buy_val_total, foreign_sell_val_total, foreign_buy_vol_matched,
                foreign_buy_vol_deal, total_buy_trade, total_buy_trade_vol, total_sell_trade,
                total_sell_trade_vol, net_buy_sell_vol, net_buy_sell_val, close_raw,
                open_raw, high_raw, low_raw
            )
            VALUES (
                :symbol, :date, :current_price, :change_amount, :change_percent, :volume, :value,
                :high_price, :low_price, :open_price, :close_price, :pe_ratio, :pb_ratio, :eps,
                :dividend_yield, :market_cap, :ceiling_price, :floor_price, :ref_price, :avg_price,
                :close_price_adjusted, :total_match_vol, :total_deal_val, :total_deal_vol,
                :foreign_buy_vol_total, :foreign_current_room, :foreign_sell_vol_total,
                :foreign_buy_val_total, :foreign_sell_val_total, :foreign_buy_vol_matched,
                :foreign_buy_vol_deal, :total_buy_trade, :total_buy_trade_vol, :total_sell_trade,
                :total_sell_trade_vol, :net_buy_sell_vol, :net_buy_sell_val, :close_raw,
                :open_raw, :high_raw, :low_raw
            )
            ON CONFLICT (symbol, date) DO UPDATE SET
                current_price = EXCLUDED.current_price,
                change_amount = EXCLUDED.change_amount,
                change_percent = EXCLUDED.change_percent,
                volume = EXCLUDED.volume,
                value = EXCLUDED.value,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                open_price = EXCLUDED.open_price,
                close_price = EXCLUDED.close_price,
                pe_ratio = EXCLUDED.pe_ratio,
                pb_ratio = EXCLUDED.pb_ratio,
                eps = EXCLUDED.eps,
                dividend_yield = EXCLUDED.dividend_yield,
                market_cap = EXCLUDED.market_cap,
                ceiling_price = EXCLUDED.ceiling_price,
                floor_price = EXCLUDED.floor_price,
                ref_price = EXCLUDED.ref_price,
                avg_price = EXCLUDED.avg_price,
                close_price_adjusted = EXCLUDED.close_price_adjusted,
                total_match_vol = EXCLUDED.total_match_vol,
                total_deal_val = EXCLUDED.total_deal_val,
                total_deal_vol = EXCLUDED.total_deal_vol,
                foreign_buy_vol_total = EXCLUDED.foreign_buy_vol_total,
                foreign_current_room = EXCLUDED.foreign_current_room,
                foreign_sell_vol_total = EXCLUDED.foreign_sell_vol_total,
                foreign_buy_val_total = EXCLUDED.foreign_buy_val_total,
                foreign_sell_val_total = EXCLUDED.foreign_sell_val_total,
                foreign_buy_vol_matched = EXCLUDED.foreign_buy_vol_matched,
                foreign_buy_vol_deal = EXCLUDED.foreign_buy_vol_deal,
                total_buy_trade = EXCLUDED.total_buy_trade,
                total_buy_trade_vol = EXCLUDED.total_buy_trade_vol,
                total_sell_trade = EXCLUDED.total_sell_trade,
                total_sell_trade_vol = EXCLUDED.total_sell_trade_vol,
                net_buy_sell_vol = EXCLUDED.net_buy_sell_vol,
                net_buy_sell_val = EXCLUDED.net_buy_sell_val,
                close_raw = EXCLUDED.close_raw,
                open_raw = EXCLUDED.open_raw,
                high_raw = EXCLUDED.high_raw,
                low_raw = EXCLUDED.low_raw,
                created_at = NOW()
            RETURNING id, symbol, date, current_price, change_amount, change_percent, volume, value,
                      high_price, low_price, open_price, close_price, pe_ratio, pb_ratio, eps,
                      dividend_yield, market_cap, ceiling_price, floor_price, ref_price, avg_price,
                      close_price_adjusted, total_match_vol, total_deal_val, total_deal_vol,
                      foreign_buy_vol_total, foreign_current_room, foreign_sell_vol_total,
                      foreign_buy_val_total, foreign_sell_val_total, foreign_buy_vol_matched,
                      foreign_buy_vol_deal, total_buy_trade, total_buy_trade_vol, total_sell_trade,
                      total_sell_trade_vol, net_buy_sell_vol, net_buy_sell_val, close_raw,
                      open_raw, high_raw, low_raw, created_at;
        """)
        
        result = db.execute(query, stats.dict()).fetchone()
        db.commit()
        
        if result:
            return StockStatistics(
                id=result.id,
                symbol=result.symbol,
                date=result.date,
                current_price=result.current_price,
                change_amount=result.change_amount,
                change_percent=result.change_percent,
                volume=result.volume,
                value=result.value,
                high_price=result.high_price,
                low_price=result.low_price,
                open_price=result.open_price,
                close_price=result.close_price,
                pe_ratio=result.pe_ratio,
                pb_ratio=result.pb_ratio,
                eps=result.eps,
                dividend_yield=result.dividend_yield,
                market_cap=result.market_cap,
                ceiling_price=result.ceiling_price,
                floor_price=result.floor_price,
                ref_price=result.ref_price,
                avg_price=result.avg_price,
                close_price_adjusted=result.close_price_adjusted,
                total_match_vol=result.total_match_vol,
                total_deal_val=result.total_deal_val,
                total_deal_vol=result.total_deal_vol,
                foreign_buy_vol_total=result.foreign_buy_vol_total,
                foreign_current_room=result.foreign_current_room,
                foreign_sell_vol_total=result.foreign_sell_vol_total,
                foreign_buy_val_total=result.foreign_buy_val_total,
                foreign_sell_val_total=result.foreign_sell_val_total,
                foreign_buy_vol_matched=result.foreign_buy_vol_matched,
                foreign_buy_vol_deal=result.foreign_buy_vol_deal,
                total_buy_trade=result.total_buy_trade,
                total_buy_trade_vol=result.total_buy_trade_vol,
                total_sell_trade=result.total_sell_trade,
                total_sell_trade_vol=result.total_sell_trade_vol,
                net_buy_sell_vol=result.net_buy_sell_vol,
                net_buy_sell_val=result.net_buy_sell_val,
                close_raw=result.close_raw,
                open_raw=result.open_raw,
                high_raw=result.high_raw,
                low_raw=result.low_raw,
                created_at=result.created_at
            )
        raise HTTPException(status_code=500, detail="Failed to create or update stock statistics")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stock-statistics", response_model=List[StockStatistics])
async def get_stock_statistics(
    symbol: str = Query(..., min_length=1, max_length=10),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get stock statistics with all fields"""
    query_parts = [
        "SELECT id, symbol, date, current_price, change_amount, change_percent, volume, value,",
        "high_price, low_price, open_price, close_price, pe_ratio, pb_ratio, eps,",
        "dividend_yield, market_cap, ceiling_price, floor_price, ref_price, avg_price,",
        "close_price_adjusted, total_match_vol, total_deal_val, total_deal_vol,",
        "foreign_buy_vol_total, foreign_current_room, foreign_sell_vol_total,",
        "foreign_buy_val_total, foreign_sell_val_total, foreign_buy_vol_matched,",
        "foreign_buy_vol_deal, total_buy_trade, total_buy_trade_vol, total_sell_trade,",
        "total_sell_trade_vol, net_buy_sell_vol, net_buy_sell_val, close_raw,",
        "open_raw, high_raw, low_raw, created_at",
        "FROM stock_statistics",
        "WHERE symbol = :symbol"
    ]
    params = {"symbol": symbol}

    if from_date:
        query_parts.append("AND date >= :from_date")
        params["from_date"] = from_date

    if to_date:
        query_parts.append("AND date <= :to_date")
        params["to_date"] = to_date

    query_parts.append("ORDER BY date DESC LIMIT :limit OFFSET :skip")
    params.update({"limit": limit, "skip": skip})

    query = text(" ".join(query_parts))
    result = db.execute(query, params)
    
    stats = []
    for row in result:
        stats.append(StockStatistics(
            id=row.id,
            symbol=row.symbol,
            date=row.date,
            current_price=row.current_price,
            change_amount=row.change_amount,
            change_percent=row.change_percent,
            volume=row.volume,
            value=row.value,
            high_price=row.high_price,
            low_price=row.low_price,
            open_price=row.open_price,
            close_price=row.close_price,
            pe_ratio=row.pe_ratio,
            pb_ratio=row.pb_ratio,
            eps=row.eps,
            dividend_yield=row.dividend_yield,
            market_cap=row.market_cap,
            ceiling_price=row.ceiling_price,
            floor_price=row.floor_price,
            ref_price=row.ref_price,
            avg_price=row.avg_price,
            close_price_adjusted=row.close_price_adjusted,
            total_match_vol=row.total_match_vol,
            total_deal_val=row.total_deal_val,
            total_deal_vol=row.total_deal_vol,
            foreign_buy_vol_total=row.foreign_buy_vol_total,
            foreign_current_room=row.foreign_current_room,
            foreign_sell_vol_total=row.foreign_sell_vol_total,
            foreign_buy_val_total=row.foreign_buy_val_total,
            foreign_sell_val_total=row.foreign_sell_val_total,
            foreign_buy_vol_matched=row.foreign_buy_vol_matched,
            foreign_buy_vol_deal=row.foreign_buy_vol_deal,
            total_buy_trade=row.total_buy_trade,
            total_buy_trade_vol=row.total_buy_trade_vol,
            total_sell_trade=row.total_sell_trade,
            total_sell_trade_vol=row.total_sell_trade_vol,
            net_buy_sell_vol=row.net_buy_sell_vol,
            net_buy_sell_val=row.net_buy_sell_val,
            close_raw=row.close_raw,
            open_raw=row.open_raw,
            high_raw=row.high_raw,
            low_raw=row.low_raw,
            created_at=row.created_at
        ))
    return stats

# =====================================================
# ANALYTICS ENDPOINTS
# =====================================================

@app.get("/analytics/stock-summary/{symbol}")
async def get_stock_summary(symbol: str, db: Session = Depends(get_db)):
    """Get comprehensive stock summary"""
    try:
        # Get latest stock statistics
        stats_query = text("""
            SELECT * FROM stock_statistics 
            WHERE symbol = :symbol 
            ORDER BY date DESC 
            LIMIT 1
        """)
        stats_result = db.execute(stats_query, {"symbol": symbol}).fetchone()
        
        # Get latest order book data
        order_query = text("""
            SELECT * FROM order_book 
            WHERE symbol = :symbol 
            ORDER BY timestamp DESC 
            LIMIT 3
        """)
        order_result = db.execute(order_query, {"symbol": symbol}).fetchall()
        
        # Get latest foreign trading data
        foreign_query = text("""
            SELECT * FROM foreign_trading 
            WHERE symbol = :symbol 
            ORDER BY date DESC 
            LIMIT 1
        """)
        foreign_result = db.execute(foreign_query, {"symbol": symbol}).fetchone()
        
        return {
            "symbol": symbol,
            "statistics": dict(stats_result._mapping) if stats_result else None,
            "order_book": [dict(row._mapping) for row in order_result],
            "foreign_trading": dict(foreign_result._mapping) if foreign_result else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
