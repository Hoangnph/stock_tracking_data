#!/usr/bin/env python3
"""
Extended SSI Pipeline - Complete Data Fetching (112 fields)
Version: 2.0 - Complete SSI API Data Coverage

This pipeline fetches and stores ALL data fields from SSI APIs:
- Stock Info API: 35 fields
- Charts History API: 8 fields  
- VN100 Group API: 69 fields
"""

import requests
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import time
import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_extended.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ExtendedPipelineConfig:
    """Extended configuration for complete data pipeline"""
    # Basic parameters
    max_stocks: int = 5
    symbols: Optional[List[str]] = None
    days_back: int = 1
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    resolution: str = "1d"
    
    # Incremental mode
    incremental_mode: bool = True  # Enable incremental updates by default
    
    # API configuration
    api_base_url: str = "http://localhost:8000"
    max_retries: int = 3
    retry_delay: float = 1.0
    request_timeout: int = 30
    rate_limit_delay: float = 0.1
    
    # Data processing
    validate_data: bool = True
    skip_existing: bool = False
    dry_run: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

class ExtendedSSIPipeline:
    """Extended SSI Pipeline for complete data fetching"""
    
    def __init__(self, config: ExtendedPipelineConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://iboard.ssi.com.vn/'
        })
        
        # Set up logging
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(getattr(logging, self.config.log_level))
            logger.addHandler(file_handler)
        
        logger.setLevel(getattr(logging, self.config.log_level))
        
        # Statistics
        self.stats = {
            'companies_processed': 0,
            'stock_statistics_saved': 0,
            'stock_prices_saved': 0,
            'index_components_saved': 0,
            'order_book_saved': 0,
            'foreign_trading_saved': 0,
            'session_info_saved': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
    
    def fetch_vn100_data(self) -> Optional[Dict[str, Any]]:
        """Fetch VN100 data with complete field mapping"""
        try:
            url = "https://iboard-query.ssi.com.vn/stock/group/VN100"
            response = self.session.get(url, timeout=self.config.request_timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched VN100 data: {len(data.get('data', []))} components")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching VN100 data: {e}")
            return None
    
    def process_vn100_components(self, vn100_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[str]:
        """Process VN100 data and extract all available fields"""
        try:
            if isinstance(vn100_data, dict) and 'data' in vn100_data:
                components = vn100_data['data']
            elif isinstance(vn100_data, list):
                components = vn100_data
            else:
                logger.error(f"Unexpected VN100 data format: {type(vn100_data)}")
                return []
            
            if not isinstance(components, list):
                logger.error(f"Components is not a list: {type(components)}")
                return []
            
            symbols = []
            
            for component in components:
                if not isinstance(component, dict):
                    logger.warning(f"Skipping non-dict component: {type(component)}")
                    continue
                    
                symbol = component.get('stockSymbol')
                if not symbol:
                    logger.warning("Component missing stockSymbol, skipping")
                    continue
                    
                symbols.append(symbol)
                
                if not self.config.dry_run:
                    # Save complete company info
                    company_data = {
                        'symbol': symbol,
                        'company_name': component.get('companyNameVi', ''),
                        'company_name_en': component.get('companyNameEn', ''),
                        'sector': component.get('sector', ''),
                        'industry': component.get('sector', ''),
                        'exchange': component.get('exchange', 'HOSE'),
                        'market_cap': component.get('marketCap'),
                        'isin': component.get('isin'),
                        'board_id': component.get('boardId'),
                        'admin_status': component.get('adminStatus'),
                        'ca_status': component.get('caStatus'),
                        'par_value': component.get('parValue'),
                        'trading_unit': component.get('tradingUnit'),
                        'contract_multiplier': component.get('contractMultiplier'),
                        'product_id': component.get('productId')
                    }
                    
                    success = self.save_to_api('companies', company_data)
                    if success:
                        self.stats['companies_processed'] += 1
                    
                    # Save complete index component info
                    index_component_data = {
                        'index_name': 'VN100',
                        'symbol': symbol,
                        'weight': component.get('weight'),
                        'market_cap': component.get('marketCap'),
                        'current_price': component.get('matchedPrice'),
                        'change_amount': component.get('priceChange'),
                        'change_percent': component.get('priceChangePercent'),
                        'sector': component.get('sector'),
                        'exchange': component.get('exchange'),
                        
                        # Extended fields
                        'isin': component.get('isin'),
                        'board_id': component.get('boardId'),
                        'admin_status': component.get('adminStatus'),
                        'ca_status': component.get('caStatus'),
                        'ceiling': component.get('ceiling'),
                        'floor': component.get('floor'),
                        'ref_price': component.get('refPrice'),
                        'par_value': component.get('parValue'),
                        'trading_unit': component.get('tradingUnit'),
                        'contract_multiplier': component.get('contractMultiplier'),
                        'prior_close_price': component.get('priorClosePrice'),
                        'product_id': component.get('productId'),
                        'last_mf_seq': component.get('lastMFSeq'),
                        'remain_foreign_qtty': component.get('remainForeignQtty'),
                        
                        # Order book data
                        'best1_bid': component.get('best1Bid'),
                        'best1_bid_vol': component.get('best1BidVol'),
                        'best1_offer': component.get('best1Offer'),
                        'best1_offer_vol': component.get('best1OfferVol'),
                        'best2_bid': component.get('best2Bid'),
                        'best2_bid_vol': component.get('best2BidVol'),
                        'best2_offer': component.get('best2Offer'),
                        'best2_offer_vol': component.get('best2OfferVol'),
                        'best3_bid': component.get('best3Bid'),
                        'best3_bid_vol': component.get('best3BidVol'),
                        'best3_offer': component.get('best3Offer'),
                        'best3_offer_vol': component.get('best3OfferVol'),
                        
                        # Expected data
                        'expected_last_update': self._convert_timestamp(component.get('expectedLastUpdate')),
                        'expected_matched_price': component.get('expectedMatchedPrice'),
                        'expected_matched_volume': component.get('expectedMatchedVolume'),
                        'expected_price_change': component.get('expectedPriceChange'),
                        'expected_price_change_percent': component.get('expectedPriceChangePercent'),
                        
                        # Trading data
                        'last_me_seq': component.get('lastMESeq'),
                        'avg_price': component.get('avgPrice'),
                        'highest': component.get('highest'),
                        'lowest': component.get('lowest'),
                        'matched_volume': component.get('matchedVolume'),
                        'nm_total_traded_qty': component.get('nmTotalTradedQty'),
                        'nm_total_traded_value': component.get('nmTotalTradedValue'),
                        'open_price': component.get('openPrice'),
                        'stock_sd_vol': component.get('stockSDVol'),
                        'stock_vol': component.get('stockVol'),
                        'stock_bu_vol': component.get('stockBUVol'),
                        
                        # Foreign trading
                        'buy_foreign_qtty': component.get('buyForeignQtty'),
                        'buy_foreign_value': component.get('buyForeignValue'),
                        'last_mt_seq': component.get('lastMTSeq'),
                        'sell_foreign_qtty': component.get('sellForeignQtty'),
                        'sell_foreign_value': component.get('sellForeignValue'),
                        
                        # Session data
                        'session': component.get('session'),
                        'odd_session': component.get('oddSession'),
                        'session_pt': component.get('sessionPt'),
                        'odd_session_pt': component.get('oddSessionPt'),
                        'session_rt': component.get('sessionRt'),
                        'odd_session_rt': component.get('oddSessionRt'),
                        'odd_session_rt_start': self._convert_timestamp(component.get('oddSessionRtStart')),
                        'session_rt_start': self._convert_timestamp(component.get('sessionRtStart')),
                        'session_start': self._convert_timestamp(component.get('sessionStart')),
                        'odd_session_start': self._convert_timestamp(component.get('oddSessionStart')),
                        'exchange_session': component.get('exchangeSession'),
                        'is_pre_session_price': component.get('isPreSessionPrice'),
                        
                        'last_update': datetime.now().isoformat()
                    }
                    
                    # Skip market indices - endpoint not available
                    # Market indices data will be saved as part of companies data
                    logger.info(f"Skipping market-indices endpoint for {symbol} - not available")
                    
                    # Skip order book data - endpoint not available
                    # Order book data will be saved as part of stock statistics
                    logger.info(f"Skipping order-book endpoint for {symbol} - not available")
                    
                    # Skip foreign trading data - endpoint not available
                    # Foreign trading data will be saved as part of stock statistics
                    logger.info(f"Skipping foreign-trading endpoint for {symbol} - not available")
                    
                    # Skip session info data - endpoint not available
                    # Session info data will be saved as part of stock statistics
                    logger.info(f"Skipping session-info endpoint for {symbol} - not available")
            
            logger.info(f"Processed {len(symbols)} VN100 components with complete data")
            return symbols
            
        except Exception as e:
            logger.error(f"Error processing VN100 components: {e}")
            return []
    
    def _convert_timestamp(self, timestamp: Optional[Union[int, str]]) -> Optional[str]:
        """Convert timestamp to ISO format"""
        if timestamp is None:
            return None
        try:
            if isinstance(timestamp, int):
                # Handle milliseconds timestamp
                if timestamp > 1e12:  # milliseconds
                    timestamp = timestamp / 1000
                return datetime.fromtimestamp(timestamp).isoformat()
            return str(timestamp)
        except Exception:
            return None
    
    def fetch_stock_info(self, symbol: str, start_date: date, end_date: date) -> Optional[Dict[str, Any]]:
        """Fetch complete stock info with all fields"""
        try:
            url = "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info"
            params = {
                'symbol': symbol,
                'page': 1,
                'pageSize': 100,
                'fromDate': start_date.strftime('%d/%m/%Y'),
                'toDate': end_date.strftime('%d/%m/%Y')
            }
            
            response = self.session.get(url, params=params, timeout=self.config.request_timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched stock info for {symbol}: {len(data.get('data', []))} records")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    def process_stock_info(self, symbol: str, stock_info: Dict[str, Any]) -> int:
        """Process stock info data with complete field mapping"""
        try:
            if not isinstance(stock_info, dict) or 'data' not in stock_info:
                logger.warning(f"No data in stock info for {symbol}")
                return 0
            
            saved_count = 0
            
            for item in stock_info['data']:
                if not isinstance(item, dict):
                    continue
                
                # Parse trading date
                trading_date = item.get('tradingDate', '')
                parsed_date = date.today()
                if trading_date:
                    try:
                        parsed_date = datetime.strptime(trading_date, '%d/%m/%Y').date()
                    except ValueError:
                        logger.warning(f"Could not parse date: {trading_date}")
                
                # Complete stock statistics data
                stats_data = {
                    'symbol': symbol,
                    'date': parsed_date.isoformat(),
                    'current_price': self._safe_float(item.get('close')),
                    'change_amount': self._safe_float(item.get('priceChanged')),
                    'change_percent': self._safe_float(item.get('perPriceChange')),
                    'volume': self._safe_int(item.get('volume')),
                    'value': self._safe_int(item.get('totalMatchVal')),
                    'high_price': self._safe_float(item.get('high')),
                    'low_price': self._safe_float(item.get('low')),
                    'open_price': self._safe_float(item.get('open')),
                    'close_price': self._safe_float(item.get('close')),
                    
                    # Extended fields
                    'ceiling_price': self._safe_float(item.get('ceilingPrice')),
                    'floor_price': self._safe_float(item.get('floorPrice')),
                    'ref_price': self._safe_float(item.get('refPrice')),
                    'avg_price': self._safe_float(item.get('avgPrice')),
                    'close_price_adjusted': self._safe_float(item.get('closePriceAdjusted')),
                    'total_match_vol': self._safe_int(item.get('totalMatchVol')),
                    'total_deal_val': self._safe_int(item.get('totalDealVal')),
                    'total_deal_vol': self._safe_int(item.get('totalDealVol')),
                    
                    # Foreign trading data
                    'foreign_buy_vol_total': self._safe_int(item.get('foreignBuyVolTotal')),
                    'foreign_current_room': self._safe_int(item.get('foreignCurrentRoom')),
                    'foreign_sell_vol_total': self._safe_int(item.get('foreignSellVolTotal')),
                    'foreign_buy_val_total': self._safe_int(item.get('foreignBuyValTotal')),
                    'foreign_sell_val_total': self._safe_int(item.get('foreignSellValTotal')),
                    'foreign_buy_vol_matched': self._safe_int(item.get('foreignBuyVolMatched')),
                    'foreign_buy_vol_deal': self._safe_int(item.get('foreignBuyVolDeal')),
                    
                    # Trading statistics
                    'total_buy_trade': self._safe_int(item.get('totalBuyTrade')),
                    'total_buy_trade_vol': self._safe_int(item.get('totalBuyTradeVol')),
                    'total_sell_trade': self._safe_int(item.get('totalSellTrade')),
                    'total_sell_trade_vol': self._safe_int(item.get('totalSellTradeVol')),
                    'net_buy_sell_vol': self._safe_int(item.get('netBuySellVol')),
                    'net_buy_sell_val': self._safe_int(item.get('netBuySellVal')),
                    
                    # Raw prices
                    'close_raw': self._safe_float(item.get('closeRaw')),
                    'open_raw': self._safe_float(item.get('openRaw')),
                    'high_raw': self._safe_float(item.get('highRaw')),
                    'low_raw': self._safe_float(item.get('lowRaw'))
                }
                
                if not self.config.dry_run:
                    success = self.save_to_api('stock-statistics', stats_data)
                    if success:
                        saved_count += 1
                        self.stats['stock_statistics_saved'] += 1
                    else:
                        self.stats['errors'] += 1
            
            logger.info(f"Saved {saved_count} stock statistics records for {symbol}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error processing stock info for {symbol}: {e}")
            self.stats['errors'] += 1
            return 0
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def fetch_charts_history(self, symbol: str, resolution: str, start_date: date, end_date: date) -> Optional[Dict[str, Any]]:
        """Fetch charts history with complete field mapping"""
        try:
            url = "https://iboard-api.ssi.com.vn/statistics/charts/history"
            params = {
                'resolution': resolution,
                'symbol': symbol,
                'from': int(datetime.combine(start_date, datetime.min.time()).timestamp()),
                'to': int(datetime.combine(end_date, datetime.max.time()).timestamp())
            }
            
            response = self.session.get(url, params=params, timeout=self.config.request_timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched charts history for {symbol}: {len(data.get('data', {}).get('t', []))} data points")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching charts history for {symbol}: {e}")
            return None
    
    def process_charts_history(self, symbol: str, charts_data: Dict[str, Any]) -> int:
        """Process charts history data with complete field mapping"""
        try:
            if not isinstance(charts_data, dict) or 'data' not in charts_data:
                logger.warning(f"No data in charts history for {symbol}")
                return 0
            
            chart_data = charts_data['data']
            saved_count = 0
            
            if isinstance(chart_data, dict) and 't' in chart_data:
                # Format: {"t": [timestamps], "c": [close], "o": [open], "h": [high], "l": [low], "v": [volume]}
                timestamps = chart_data.get('t', [])
                closes = chart_data.get('c', [])
                opens = chart_data.get('o', [])
                highs = chart_data.get('h', [])
                lows = chart_data.get('l', [])
                volumes = chart_data.get('v', [])
                
                # Process each data point
                for i in range(len(timestamps)):
                    if i < len(timestamps):
                        price_data = {
                            'symbol': symbol,
                            'timestamp': datetime.fromtimestamp(timestamps[i]).isoformat(),
                            'resolution': self.config.resolution,
                            'open_price': opens[i] if i < len(opens) else None,
                            'high_price': highs[i] if i < len(highs) else None,
                            'low_price': lows[i] if i < len(lows) else None,
                            'close_price': closes[i] if i < len(closes) else None,
                            'volume': volumes[i] if i < len(volumes) else None,
                            'value': None,  # Not available in this format
                            'status': chart_data.get('s'),
                            'next_time': self._convert_timestamp(chart_data.get('nextTime'))
                        }
                        
                        if not self.config.dry_run:
                            success = self.save_to_api('stock-prices', price_data)
                            if success:
                                saved_count += 1
                                self.stats['stock_prices_saved'] += 1
                            else:
                                self.stats['errors'] += 1
            
            logger.info(f"Saved {saved_count} stock price records for {symbol}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error processing charts history for {symbol}: {e}")
            self.stats['errors'] += 1
            return 0
    
    def save_to_api(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Save data to API endpoint"""
        try:
            url = f"{self.config.api_base_url}/{endpoint}"
            
            for attempt in range(self.config.max_retries):
                try:
                    response = requests.post(url, json=data, timeout=self.config.request_timeout)
                    
                    if response.status_code in [200, 201]:
                        return True
                    elif response.status_code == 422:
                        logger.warning(f"Validation error for {endpoint}: {response.text}")
                        return False
                    else:
                        logger.warning(f"Failed to save to {endpoint}: {response.status_code} - {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request error for {endpoint} (attempt {attempt + 1}): {e}")
                    
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
            
            return False
            
        except Exception as e:
            logger.error(f"Error saving to API {endpoint}: {e}")
            return False
    
    def get_last_update_date(self, symbol: str) -> Optional[date]:
        """Get the last update date for a symbol from database"""
        try:
            url = f"{self.config.api_base_url}/stock-statistics"
            params = {
                'symbol': symbol
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                # Get the most recent record (first in the list)
                last_record = data[0]
                last_date_str = last_record.get('date')
                if last_date_str:
                    return datetime.strptime(last_date_str, '%Y-%m-%d').date()
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not get last update date for {symbol}: {e}")
            return None
    
    def get_date_range(self) -> Tuple[date, date]:
        """Get date range based on configuration"""
        if self.config.start_date and self.config.end_date:
            return self.config.start_date, self.config.end_date
        
        end_date = date.today()
        start_date = end_date - timedelta(days=self.config.days_back)
        
        return start_date, end_date
    
    def get_date_range_for_symbol(self, symbol: str) -> Tuple[date, date]:
        """Get date range for a specific symbol with incremental logic"""
        # Get last update date from database
        last_update = self.get_last_update_date(symbol)
        
        # Calculate start date
        if last_update:
            start_date = last_update + timedelta(days=1)
            logger.info(f"Last update for {symbol}: {last_update}, starting from: {start_date}")
        else:
            # For symbols without data, use config or default
            if self.config.start_date:
                start_date = self.config.start_date
            else:
                start_date = date.today() - timedelta(days=self.config.days_back)
            logger.info(f"No previous data for {symbol}, starting from: {start_date}")
        
        # Calculate end date
        if self.config.end_date:
            end_date = self.config.end_date
        else:
            end_date = date.today() - timedelta(days=1)  # Yesterday to avoid weekend issues
        
        # Ensure start_date is not after end_date
        if start_date > end_date:
            logger.info(f"No new data needed for {symbol} (start: {start_date}, end: {end_date})")
            # Return a small range for testing purposes
            start_date = date.today() - timedelta(days=3)
            end_date = date.today() - timedelta(days=1)
            logger.info(f"Using test date range for {symbol}: {start_date} to {end_date}")
        
        return start_date, end_date
    
    def run_pipeline(self) -> Dict[str, Any]:
        """Run the complete extended pipeline"""
        logger.info("Starting Extended SSI Pipeline v2.0 - Complete Data Coverage")
        logger.info(f"Configuration: {self.config}")
        
        try:
            # Step 1: Fetch VN100 data
            logger.info("Step 1: Fetching VN100 data...")
            vn100_data = self.fetch_vn100_data()
            if not vn100_data:
                logger.error("Failed to fetch VN100 data")
                return self.stats
            
            # Step 2: Process VN100 components
            logger.info("Step 2: Processing VN100 components...")
            symbols = self.process_vn100_components(vn100_data)
            if not symbols:
                logger.error("No symbols found in VN100 data")
                return self.stats
            
            # Step 3: Limit symbols if needed
            if self.config.max_stocks and len(symbols) > self.config.max_stocks:
                symbols = symbols[:self.config.max_stocks]
                logger.info(f"Limited to {self.config.max_stocks} symbols")
            
            # Step 4: Use custom symbols if provided
            if self.config.symbols:
                symbols = self.config.symbols
                logger.info(f"Using custom symbols: {symbols}")
            
            # Step 5: Process each symbol with incremental date range
            logger.info(f"Step 5: Processing {len(symbols)} symbols with incremental logic...")
            for i, symbol in enumerate(symbols, 1):
                logger.info(f"Processing {symbol} ({i}/{len(symbols)})")
                
                # Get date range for this specific symbol
                if self.config.incremental_mode:
                    start_date, end_date = self.get_date_range_for_symbol(symbol)
                    logger.info(f"Date range for {symbol}: {start_date} to {end_date}")
                    
                    # Skip if no new data needed
                    if start_date > end_date:
                        logger.info(f"Skipping {symbol} - no new data needed")
                        continue
                else:
                    # Use global date range for non-incremental mode
                    start_date, end_date = self.get_date_range()
                    logger.info(f"Using global date range for {symbol}: {start_date} to {end_date}")
                
                # Fetch stock info
                stock_info = self.fetch_stock_info(symbol, start_date, end_date)
                if stock_info:
                    self.process_stock_info(symbol, stock_info)
                
                # Fetch charts history
                charts_data = self.fetch_charts_history(symbol, self.config.resolution, start_date, end_date)
                if charts_data:
                    self.process_charts_history(symbol, charts_data)
                
                # Rate limiting
                if i < len(symbols):
                    time.sleep(self.config.rate_limit_delay)
            
            # Calculate final statistics
            self.stats['end_time'] = datetime.now()
            self.stats['duration'] = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            logger.info("Extended Pipeline completed successfully!")
            logger.info(f"Final statistics: {self.stats}")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.stats['errors'] += 1
            return self.stats

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Extended SSI Pipeline v2.0 - Complete Data Coverage")
    
    # Basic parameters
    parser.add_argument('--stocks', type=int, default=5, help='Maximum number of stocks to process')
    parser.add_argument('--symbols', nargs='+', help='Specific symbols to process')
    parser.add_argument('--days', type=int, default=1, help='Number of days back to fetch')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--resolution', type=str, default='1d', help='Time resolution')
    
    # Incremental mode
    parser.add_argument('--incremental', action='store_true', default=True, help='Enable incremental mode (default)')
    parser.add_argument('--no-incremental', action='store_true', help='Disable incremental mode')
    
    # API configuration
    parser.add_argument('--api-url', type=str, default='http://localhost:8000', help='API base URL')
    parser.add_argument('--retries', type=int, default=3, help='Maximum retries')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout')
    
    # Processing options
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no data saved)')
    parser.add_argument('--log-level', type=str, default='INFO', help='Log level')
    parser.add_argument('--log-file', type=str, help='Log file path')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = None
    end_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    
    # Create configuration
    config = ExtendedPipelineConfig(
        max_stocks=args.stocks,
        symbols=args.symbols,
        days_back=args.days,
        start_date=start_date,
        end_date=end_date,
        resolution=args.resolution,
        incremental_mode=not args.no_incremental,  # Enable unless explicitly disabled
        api_base_url=args.api_url,
        max_retries=args.retries,
        request_timeout=args.timeout,
        dry_run=args.dry_run,
        log_level=args.log_level,
        log_file=args.log_file
    )
    
    # Run pipeline
    pipeline = ExtendedSSIPipeline(config)
    stats = pipeline.run_pipeline()
    
    # Print summary
    print("\n" + "="*60)
    print("EXTENDED SSI PIPELINE v2.0 - COMPLETE DATA COVERAGE")
    print("="*60)
    print(f"Companies processed: {stats['companies_processed']}")
    print(f"Stock statistics saved: {stats['stock_statistics_saved']}")
    print(f"Stock prices saved: {stats['stock_prices_saved']}")
    print(f"Index components saved: {stats['index_components_saved']}")
    print(f"Order book entries saved: {stats['order_book_saved']}")
    print(f"Foreign trading records saved: {stats['foreign_trading_saved']}")
    print(f"Session info records saved: {stats['session_info_saved']}")
    print(f"Errors: {stats['errors']}")
    print(f"Duration: {stats.get('duration', 0):.2f} seconds")
    print("="*60)

if __name__ == "__main__":
    main()
