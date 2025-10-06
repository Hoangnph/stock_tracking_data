#!/usr/bin/env python3
"""
SSI Direct API Proxy - Real-time Data Access
Version: 2.1 - Direct SSI API Integration

This API provides direct access to SSI APIs without database storage.
Useful for real-time data access, testing, and debugging.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
import requests
import json
import os
import time
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5434/tracking_data")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SSI API Configuration
SSI_API_CONFIG = {
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
}

# =====================================================
# PYDANTIC MODELS FOR SSI API RESPONSES
# =====================================================

class SSIStockInfoResponse(BaseModel):
    """Response model for Stock Info API"""
    symbol: str
    trading_date: str
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[int] = None
    price_changed: Optional[float] = None
    per_price_change: Optional[float] = None
    total_match_val: Optional[int] = None
    ceiling_price: Optional[float] = None
    floor_price: Optional[float] = None
    ref_price: Optional[float] = None
    avg_price: Optional[float] = None
    close_price_adjusted: Optional[float] = None
    total_match_vol: Optional[int] = None
    total_deal_val: Optional[int] = None
    total_deal_vol: Optional[int] = None
    foreign_buy_vol_total: Optional[int] = None
    foreign_current_room: Optional[int] = None
    foreign_sell_vol_total: Optional[int] = None
    foreign_buy_val_total: Optional[int] = None
    foreign_sell_val_total: Optional[int] = None
    total_buy_trade: Optional[int] = None
    total_buy_trade_vol: Optional[int] = None
    total_sell_trade: Optional[int] = None
    total_sell_trade_vol: Optional[int] = None
    net_buy_sell_vol: Optional[int] = None
    net_buy_sell_val: Optional[int] = None
    foreign_buy_vol_matched: Optional[int] = None
    foreign_buy_vol_deal: Optional[int] = None
    close_raw: Optional[float] = None
    open_raw: Optional[float] = None
    high_raw: Optional[float] = None
    low_raw: Optional[float] = None

class SSIChartsHistoryResponse(BaseModel):
    """Response model for Charts History API"""
    symbol: str
    resolution: str
    timestamps: List[int]
    open_prices: List[float]
    high_prices: List[float]
    low_prices: List[float]
    close_prices: List[float]
    volumes: List[int]
    status: Optional[str] = None
    next_time: Optional[int] = None
    data_points: int

class SSIVN100Component(BaseModel):
    """Response model for VN100 component"""
    stock_symbol: str
    company_name_vi: str
    company_name_en: Optional[str] = None
    exchange: str
    sector: Optional[str] = None
    matched_price: Optional[float] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    isin: Optional[str] = None
    board_id: Optional[str] = None
    admin_status: Optional[str] = None
    ca_status: Optional[str] = None
    ceiling: Optional[float] = None
    floor: Optional[float] = None
    ref_price: Optional[float] = None
    par_value: Optional[int] = None
    trading_unit: Optional[int] = None
    contract_multiplier: Optional[int] = None
    prior_close_price: Optional[float] = None
    product_id: Optional[str] = None
    last_mf_seq: Optional[int] = None
    remain_foreign_qtty: Optional[int] = None
    best1_bid: Optional[float] = None
    best1_bid_vol: Optional[int] = None
    best1_offer: Optional[float] = None
    best1_offer_vol: Optional[int] = None
    best2_bid: Optional[float] = None
    best2_bid_vol: Optional[int] = None
    best2_offer: Optional[float] = None
    best2_offer_vol: Optional[int] = None
    best3_bid: Optional[float] = None
    best3_bid_vol: Optional[int] = None
    best3_offer: Optional[float] = None
    best3_offer_vol: Optional[int] = None
    expected_last_update: Optional[int] = None
    expected_matched_price: Optional[float] = None
    expected_matched_volume: Optional[int] = None
    expected_price_change: Optional[float] = None
    expected_price_change_percent: Optional[float] = None
    last_me_seq: Optional[int] = None
    avg_price: Optional[float] = None
    highest: Optional[float] = None
    lowest: Optional[float] = None
    matched_volume: Optional[int] = None
    nm_total_traded_qty: Optional[int] = None
    nm_total_traded_value: Optional[int] = None
    open_price: Optional[float] = None
    stock_sd_vol: Optional[int] = None
    stock_vol: Optional[int] = None
    stock_bu_vol: Optional[int] = None
    buy_foreign_qtty: Optional[int] = None
    buy_foreign_value: Optional[int] = None
    last_mt_seq: Optional[int] = None
    sell_foreign_qtty: Optional[int] = None
    sell_foreign_value: Optional[int] = None
    session: Optional[str] = None
    odd_session: Optional[str] = None
    session_pt: Optional[str] = None
    odd_session_pt: Optional[str] = None
    session_rt: Optional[str] = None
    odd_session_rt: Optional[str] = None
    odd_session_rt_start: Optional[int] = None
    session_rt_start: Optional[int] = None
    session_start: Optional[int] = None
    odd_session_start: Optional[int] = None
    exchange_session: Optional[str] = None
    is_pre_session_price: Optional[bool] = None
    weight: Optional[float] = None
    market_cap: Optional[int] = None

class SSIVN100Response(BaseModel):
    """Response model for VN100 Group API"""
    code: int
    message: str
    data: List[SSIVN100Component]
    total_components: int
    timestamp: str

class SSIProxyResponse(BaseModel):
    """Generic response model for SSI proxy"""
    success: bool
    api_endpoint: str
    symbol: Optional[str] = None
    data: Any
    timestamp: str
    response_time_ms: float
    raw_response: Optional[Dict] = None

# =====================================================
# SSI API CLIENT CLASS
# =====================================================

class SSIAPIClient:
    """Client for accessing SSI APIs directly"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://iboard.ssi.com.vn/',
            'Origin': 'https://iboard.ssi.com.vn'
        })
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == '' or value == '-':
            return None
        try:
            return float(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int"""
        if value is None or value == '' or value == '-':
            return None
        try:
            return int(str(value).replace(',', ''))
        except (ValueError, TypeError):
            return None
    
    def fetch_stock_info(self, symbol: str, from_date: str, to_date: str, page: int = 1, page_size: int = 10) -> Dict:
        """Fetch stock info from SSI API"""
        try:
            params = {
                'symbol': symbol,
                'page': page,
                'pageSize': page_size,
                'fromDate': from_date,
                'toDate': to_date
            }
            
            response = self.session.get(
                SSI_API_CONFIG['stock_info']['base_url'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched stock info for {symbol}: {len(data.get('data', []))} records")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching stock info for {symbol}: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch stock info: {str(e)}")
    
    def fetch_charts_history(self, symbol: str, resolution: str, from_timestamp: int, to_timestamp: int) -> Dict:
        """Fetch charts history from SSI API"""
        try:
            params = {
                'symbol': symbol,
                'resolution': resolution,
                'from': from_timestamp,
                'to': to_timestamp
            }
            
            response = self.session.get(
                SSI_API_CONFIG['charts_history']['base_url'],
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched charts history for {symbol}: {len(data.get('data', {}).get('t', []))} data points")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching charts history for {symbol}: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch charts history: {str(e)}")
    
    def fetch_vn100_data(self) -> Dict:
        """Fetch VN100 data from SSI API"""
        try:
            response = self.session.get(
                SSI_API_CONFIG['vn100_group']['base_url'],
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched VN100 data: {len(data.get('data', []))} components")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching VN100 data: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch VN100 data: {str(e)}")

# =====================================================
# FASTAPI APPLICATION SETUP
# =====================================================

app = FastAPI(
    title="SSI Direct API Proxy", 
    version="2.1.0",
    description="Direct access to SSI APIs without database storage"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SSI API client
ssi_client = SSIAPIClient()

# =====================================================
# DEPENDENCIES
# =====================================================

def get_db():
    """Get database session (for health checks)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================
# HEALTH CHECK ENDPOINT
# =====================================================

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    db_status = "disconnected"
    
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    overall_status = "healthy" if db_status == "connected" else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "2.1.0",
        "service": "SSI Direct API Proxy"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
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

# =====================================================
# SSI PROXY ENDPOINTS
# =====================================================

@app.get("/ssi-proxy/stock-info", response_model=SSIProxyResponse)
async def proxy_stock_info(
    symbol: str = Query(..., description="Stock symbol (e.g., ACB)"),
    from_date: str = Query(..., description="Start date (DD/MM/YYYY)"),
    to_date: str = Query(..., description="End date (DD/MM/YYYY)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size")
):
    """Proxy to SSI Stock Info API (URL 1)"""
    start_time = time.time()
    
    try:
        # Fetch data from SSI API
        raw_data = ssi_client.fetch_stock_info(symbol, from_date, to_date, page, page_size)
        
        # Process and format response
        processed_data = []
        if raw_data.get('data'):
            for item in raw_data['data']:
                processed_item = SSIStockInfoResponse(
                    symbol=symbol,
                    trading_date=item.get('tradingDate', ''),
                    open_price=ssi_client._safe_float(item.get('open')),
                    high_price=ssi_client._safe_float(item.get('high')),
                    low_price=ssi_client._safe_float(item.get('low')),
                    close_price=ssi_client._safe_float(item.get('close')),
                    volume=ssi_client._safe_int(item.get('volume')),
                    price_changed=ssi_client._safe_float(item.get('priceChanged')),
                    per_price_change=ssi_client._safe_float(item.get('perPriceChange')),
                    total_match_val=ssi_client._safe_int(item.get('totalMatchVal')),
                    ceiling_price=ssi_client._safe_float(item.get('ceilingPrice')),
                    floor_price=ssi_client._safe_float(item.get('floorPrice')),
                    ref_price=ssi_client._safe_float(item.get('refPrice')),
                    avg_price=ssi_client._safe_float(item.get('avgPrice')),
                    close_price_adjusted=ssi_client._safe_float(item.get('closePriceAdjusted')),
                    total_match_vol=ssi_client._safe_int(item.get('totalMatchVol')),
                    total_deal_val=ssi_client._safe_int(item.get('totalDealVal')),
                    total_deal_vol=ssi_client._safe_int(item.get('totalDealVol')),
                    foreign_buy_vol_total=ssi_client._safe_int(item.get('foreignBuyVolTotal')),
                    foreign_current_room=ssi_client._safe_int(item.get('foreignCurrentRoom')),
                    foreign_sell_vol_total=ssi_client._safe_int(item.get('foreignSellVolTotal')),
                    foreign_buy_val_total=ssi_client._safe_int(item.get('foreignBuyValTotal')),
                    foreign_sell_val_total=ssi_client._safe_int(item.get('foreignSellValTotal')),
                    total_buy_trade=ssi_client._safe_int(item.get('totalBuyTrade')),
                    total_buy_trade_vol=ssi_client._safe_int(item.get('totalBuyTradeVol')),
                    total_sell_trade=ssi_client._safe_int(item.get('totalSellTrade')),
                    total_sell_trade_vol=ssi_client._safe_int(item.get('totalSellTradeVol')),
                    net_buy_sell_vol=ssi_client._safe_int(item.get('netBuySellVol')),
                    net_buy_sell_val=ssi_client._safe_int(item.get('netBuySellVal')),
                    foreign_buy_vol_matched=ssi_client._safe_int(item.get('foreignBuyVolMatched')),
                    foreign_buy_vol_deal=ssi_client._safe_int(item.get('foreignBuyVolDeal')),
                    close_raw=ssi_client._safe_float(item.get('closeRaw')),
                    open_raw=ssi_client._safe_float(item.get('openRaw')),
                    high_raw=ssi_client._safe_float(item.get('highRaw')),
                    low_raw=ssi_client._safe_float(item.get('lowRaw'))
                )
                processed_data.append(processed_item)
        
        response_time = (time.time() - start_time) * 1000
        
        return SSIProxyResponse(
            success=True,
            api_endpoint="stock-info",
            symbol=symbol,
            data=processed_data,
            timestamp=datetime.now().isoformat(),
            response_time_ms=round(response_time, 2),
            raw_response=raw_data
        )
        
    except Exception as e:
        logger.error(f"Error in stock-info proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ssi-proxy/charts-history", response_model=SSIProxyResponse)
async def proxy_charts_history(
    symbol: str = Query(..., description="Stock symbol (e.g., PDR)"),
    resolution: str = Query("1d", description="Resolution (1, 1h, 1d, 1w, 1M)"),
    from_timestamp: int = Query(..., description="Start timestamp (Unix)"),
    to_timestamp: int = Query(..., description="End timestamp (Unix)")
):
    """Proxy to SSI Charts History API (URL 2)"""
    start_time = time.time()
    
    try:
        # Fetch data from SSI API
        raw_data = ssi_client.fetch_charts_history(symbol, resolution, from_timestamp, to_timestamp)
        
        # Process and format response
        chart_data = raw_data.get('data', {})
        timestamps = chart_data.get('t', [])
        opens = chart_data.get('o', [])
        highs = chart_data.get('h', [])
        lows = chart_data.get('l', [])
        closes = chart_data.get('c', [])
        volumes = chart_data.get('v', [])
        
        processed_data = SSIChartsHistoryResponse(
            symbol=symbol,
            resolution=resolution,
            timestamps=timestamps,
            open_prices=opens,
            high_prices=highs,
            low_prices=lows,
            close_prices=closes,
            volumes=volumes,
            status=chart_data.get('s'),
            next_time=chart_data.get('nextTime'),
            data_points=len(timestamps)
        )
        
        response_time = (time.time() - start_time) * 1000
        
        return SSIProxyResponse(
            success=True,
            api_endpoint="charts-history",
            symbol=symbol,
            data=processed_data,
            timestamp=datetime.now().isoformat(),
            response_time_ms=round(response_time, 2),
            raw_response=raw_data
        )
        
    except Exception as e:
        logger.error(f"Error in charts-history proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ssi-proxy/vn100-group", response_model=SSIProxyResponse)
async def proxy_vn100_group():
    """Proxy to SSI VN100 Group API (URL 3)"""
    start_time = time.time()
    
    try:
        # Fetch data from SSI API
        raw_data = ssi_client.fetch_vn100_data()
        
        # Process and format response
        processed_data = []
        if raw_data.get('data'):
            for item in raw_data['data']:
                processed_item = SSIVN100Component(
                    stock_symbol=item.get('stockSymbol', ''),
                    company_name_vi=item.get('companyNameVi', ''),
                    company_name_en=item.get('companyNameEn'),
                    exchange=item.get('exchange', ''),
                    sector=item.get('sector'),
                    matched_price=ssi_client._safe_float(item.get('matchedPrice')),
                    price_change=ssi_client._safe_float(item.get('priceChange')),
                    price_change_percent=ssi_client._safe_float(item.get('priceChangePercent')),
                    isin=item.get('isin'),
                    board_id=item.get('boardId'),
                    admin_status=item.get('adminStatus'),
                    ca_status=item.get('caStatus'),
                    ceiling=ssi_client._safe_float(item.get('ceiling')),
                    floor=ssi_client._safe_float(item.get('floor')),
                    ref_price=ssi_client._safe_float(item.get('refPrice')),
                    par_value=ssi_client._safe_int(item.get('parValue')),
                    trading_unit=ssi_client._safe_int(item.get('tradingUnit')),
                    contract_multiplier=ssi_client._safe_int(item.get('contractMultiplier')),
                    prior_close_price=ssi_client._safe_float(item.get('priorClosePrice')),
                    product_id=item.get('productId'),
                    last_mf_seq=ssi_client._safe_int(item.get('lastMFSeq')),
                    remain_foreign_qtty=ssi_client._safe_int(item.get('remainForeignQtty')),
                    best1_bid=ssi_client._safe_float(item.get('best1Bid')),
                    best1_bid_vol=ssi_client._safe_int(item.get('best1BidVol')),
                    best1_offer=ssi_client._safe_float(item.get('best1Offer')),
                    best1_offer_vol=ssi_client._safe_int(item.get('best1OfferVol')),
                    best2_bid=ssi_client._safe_float(item.get('best2Bid')),
                    best2_bid_vol=ssi_client._safe_int(item.get('best2BidVol')),
                    best2_offer=ssi_client._safe_float(item.get('best2Offer')),
                    best2_offer_vol=ssi_client._safe_int(item.get('best2OfferVol')),
                    best3_bid=ssi_client._safe_float(item.get('best3Bid')),
                    best3_bid_vol=ssi_client._safe_int(item.get('best3BidVol')),
                    best3_offer=ssi_client._safe_float(item.get('best3Offer')),
                    best3_offer_vol=ssi_client._safe_int(item.get('best3OfferVol')),
                    expected_last_update=ssi_client._safe_int(item.get('expectedLastUpdate')),
                    expected_matched_price=ssi_client._safe_float(item.get('expectedMatchedPrice')),
                    expected_matched_volume=ssi_client._safe_int(item.get('expectedMatchedVolume')),
                    expected_price_change=ssi_client._safe_float(item.get('expectedPriceChange')),
                    expected_price_change_percent=ssi_client._safe_float(item.get('expectedPriceChangePercent')),
                    last_me_seq=ssi_client._safe_int(item.get('lastMESeq')),
                    avg_price=ssi_client._safe_float(item.get('avgPrice')),
                    highest=ssi_client._safe_float(item.get('highest')),
                    lowest=ssi_client._safe_float(item.get('lowest')),
                    matched_volume=ssi_client._safe_int(item.get('matchedVolume')),
                    nm_total_traded_qty=ssi_client._safe_int(item.get('nmTotalTradedQty')),
                    nm_total_traded_value=ssi_client._safe_int(item.get('nmTotalTradedValue')),
                    open_price=ssi_client._safe_float(item.get('openPrice')),
                    stock_sd_vol=ssi_client._safe_int(item.get('stockSDVol')),
                    stock_vol=ssi_client._safe_int(item.get('stockVol')),
                    stock_bu_vol=ssi_client._safe_int(item.get('stockBUVol')),
                    buy_foreign_qtty=ssi_client._safe_int(item.get('buyForeignQtty')),
                    buy_foreign_value=ssi_client._safe_int(item.get('buyForeignValue')),
                    last_mt_seq=ssi_client._safe_int(item.get('lastMTSeq')),
                    sell_foreign_qtty=ssi_client._safe_int(item.get('sellForeignQtty')),
                    sell_foreign_value=ssi_client._safe_int(item.get('sellForeignValue')),
                    session=item.get('session'),
                    odd_session=item.get('oddSession'),
                    session_pt=item.get('sessionPt'),
                    odd_session_pt=item.get('oddSessionPt'),
                    session_rt=item.get('sessionRt'),
                    odd_session_rt=item.get('oddSessionRt'),
                    odd_session_rt_start=ssi_client._safe_int(item.get('oddSessionRtStart')),
                    session_rt_start=ssi_client._safe_int(item.get('sessionRtStart')),
                    session_start=ssi_client._safe_int(item.get('sessionStart')),
                    odd_session_start=ssi_client._safe_int(item.get('oddSessionStart')),
                    exchange_session=item.get('exchangeSession'),
                    is_pre_session_price=item.get('isPreSessionPrice'),
                    weight=ssi_client._safe_float(item.get('weight')),
                    market_cap=ssi_client._safe_int(item.get('marketCap'))
                )
                processed_data.append(processed_item)
        
        response_time = (time.time() - start_time) * 1000
        
        return SSIProxyResponse(
            success=True,
            api_endpoint="vn100-group",
            symbol=None,
            data=processed_data,
            timestamp=datetime.now().isoformat(),
            response_time_ms=round(response_time, 2),
            raw_response=raw_data
        )
        
    except Exception as e:
        logger.error(f"Error in vn100-group proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# UTILITY ENDPOINTS
# =====================================================

@app.get("/ssi-proxy/config")
async def get_ssi_config():
    """Get SSI API configuration"""
    return {
        "apis": SSI_API_CONFIG,
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0"
    }

@app.get("/ssi-proxy/test/{api_name}")
async def test_ssi_api(api_name: str):
    """Test SSI API connectivity"""
    try:
        if api_name == "stock-info":
            result = ssi_client.fetch_stock_info("ACB", "01/10/2025", "05/10/2025")
        elif api_name == "charts-history":
            from_timestamp = int(datetime.now().timestamp()) - 86400  # 1 day ago
            to_timestamp = int(datetime.now().timestamp())
            result = ssi_client.fetch_charts_history("ACB", "1d", from_timestamp, to_timestamp)
        elif api_name == "vn100-group":
            result = ssi_client.fetch_vn100_data()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown API: {api_name}")
        
        return {
            "success": True,
            "api": api_name,
            "status": "connected",
            "data_preview": str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "api": api_name,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
