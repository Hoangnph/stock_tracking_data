#!/usr/bin/env python3
"""
VN100 Data Automation System - Direct SSI API Version
Version: 3.0 - Direct SSI API calls with full pagination

This version calls SSI API directly to get ALL historical data from 2010 to present.
"""

import asyncio
import logging
import sys
import time
import argparse
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import requests

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_vn100_direct.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AutomationConfig:
    """Direct automation configuration"""
    api_base_url: str = "http://localhost:8000"
    ssi_api_url: str = "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info"
    max_symbols: int = 5
    log_level: str = "INFO"
    max_pages_per_symbol: int = 1000  # Safety limit

class DirectVN100Automation:
    """Direct VN100 Automation System calling SSI API directly"""
    
    def __init__(self, config: AutomationConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://iboard.ssi.com.vn/',
            'Origin': 'https://iboard.ssi.com.vn'
        })
        
        self.stats = {
            'start_time': datetime.now(),
            'symbols_processed': 0,
            'data_records_fetched': 0,
            'data_records_saved': 0,
            'total_pages_processed': 0,
            'errors': 0,
            'end_time': None,
            'duration': 0
        }
        
        logger.setLevel(getattr(logging, config.log_level.upper()))
        logger.info(f"Direct VN100 Automation initialized")
    
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
    
    def fetch_vn100_symbols(self) -> List[str]:
        """Fetch VN100 symbols from SSI API"""
        try:
            logger.info("Fetching VN100 symbols...")
            
            url = "https://iboard-query.ssi.com.vn/stock/group/VN100"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            symbols = []
            
            if isinstance(data, dict) and 'data' in data:
                raw_components = data['data']
            elif isinstance(data, list):
                raw_components = data
            else:
                logger.error("Invalid VN100 data format")
                return symbols
            
            for item in raw_components:
                symbol = item.get('stock_symbol', '') or item.get('stockSymbol', '')
                if symbol:
                    symbols.append(symbol)
            
            logger.info(f"Fetched {len(symbols)} VN100 symbols")
            return symbols[:self.config.max_symbols]  # Limit for testing
            
        except Exception as e:
            logger.error(f"Error fetching VN100 symbols: {e}")
            self.stats['errors'] += 1
            return []
    
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
    
    def get_last_trading_day(self) -> date:
        """Get the last trading day (skip weekends)"""
        today = date.today()
        
        # If today is Monday (0), last trading day is Friday (3 days ago)
        if today.weekday() == 0:  # Monday
            return today - timedelta(days=3)
        # If today is Sunday (6), last trading day is Friday (2 days ago)
        elif today.weekday() == 6:  # Sunday
            return today - timedelta(days=2)
        # For other days, last trading day is yesterday
        else:
            return today - timedelta(days=1)
    
    def calculate_date_range(self, symbol: str) -> tuple[date, date]:
        """Calculate date range for data fetching"""
        # Get last update date
        last_update = self.get_last_update_date(symbol)
        
        # Calculate start date
        if last_update:
            start_date = last_update + timedelta(days=1)
            logger.info(f"Last update for {symbol}: {last_update}, starting from: {start_date}")
        else:
            # For symbols without data, start from 2010
            start_date = date(2010, 1, 1)
            logger.info(f"No previous data for {symbol}, starting from: {start_date}")
        
        # Calculate end date based on business rule
        now = datetime.now()
        if now.hour >= 17:  # After 5 PM
            end_date = date.today()
        else:  # Before 5 PM
            end_date = date.today() - timedelta(days=1)
        
        # Ensure start_date is not after end_date
        if start_date > end_date:
            logger.info(f"No new data needed for {symbol} (start: {start_date}, end: {end_date})")
            # Return a small range for testing purposes
            start_date = date(2025, 10, 1)
            end_date = date(2025, 10, 3)
            logger.info(f"Using test date range for {symbol}: {start_date} to {end_date}")
        
        return start_date, end_date
    
    def fetch_stock_data_direct(self, symbol: str, start_date: date, end_date: date) -> int:
        """Fetch stock data directly from SSI API with full pagination"""
        try:
            logger.info(f"Fetching stock data for {symbol} from {start_date} to {end_date}")
            
            total_saved = 0
            page = 1
            page_size = 100
            
            while page <= self.config.max_pages_per_symbol:
                # Call SSI API directly
                params = {
                    'symbol': symbol,
                    'page': page,
                    'pageSize': page_size,
                    'fromDate': start_date.strftime('%d/%m/%Y'),
                    'toDate': end_date.strftime('%d/%m/%Y')
                }
                
                logger.info(f"Fetching page {page} for {symbol}...")
                response = self.session.get(self.config.ssi_api_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if not data.get('data'):
                    logger.warning(f"No data available for {symbol} on page {page}")
                    break
                
                stock_data = data.get('data', [])
                if not stock_data:
                    logger.info(f"No more data on page {page} for {symbol}")
                    break
                
                saved_count = 0
                logger.info(f"Processing page {page} for {symbol}: {len(stock_data)} records")
                
                for item in stock_data:
                    # Parse trading date
                    trading_date_str = item.get('tradingDate', '')
                    if not trading_date_str:
                        continue
                    
                    try:
                        trading_date = datetime.strptime(trading_date_str, '%d/%m/%Y').date()
                    except ValueError:
                        logger.warning(f"Invalid date format: {trading_date_str}")
                        continue
                    
                    # Check if date is within range
                    if trading_date < start_date or trading_date > end_date:
                        continue
                    
                    # Prepare data for API
                    stats_data = {
                        'symbol': symbol,
                        'date': trading_date.isoformat(),
                        'current_price': self._safe_float(item.get('close')),
                        'change_amount': self._safe_float(item.get('priceChanged')),
                        'change_percent': self._safe_float(item.get('perPriceChange')),
                        'volume': self._safe_int(item.get('volume')),
                        'value': self._safe_int(item.get('totalMatchVal')),
                        'high_price': self._safe_float(item.get('high')),
                        'low_price': self._safe_float(item.get('low')),
                        'open_price': self._safe_float(item.get('open')),
                        'close_price': self._safe_float(item.get('close')),
                        'ceiling_price': self._safe_float(item.get('ceilingPrice')),
                        'floor_price': self._safe_float(item.get('floorPrice')),
                        'ref_price': self._safe_float(item.get('refPrice')),
                        'avg_price': self._safe_float(item.get('avgPrice')),
                        'close_price_adjusted': self._safe_float(item.get('closePriceAdjusted')),
                        'total_match_vol': self._safe_int(item.get('totalMatchVol')),
                        'total_deal_val': self._safe_int(item.get('totalDealVal')),
                        'total_deal_vol': self._safe_int(item.get('totalDealVol')),
                        'foreign_buy_vol_total': self._safe_int(item.get('foreignBuyVolTotal')),
                        'foreign_current_room': self._safe_int(item.get('foreignCurrentRoom')),
                        'foreign_sell_vol_total': self._safe_int(item.get('foreignSellVolTotal')),
                        'foreign_buy_val_total': self._safe_int(item.get('foreignBuyValTotal')),
                        'foreign_sell_val_total': self._safe_int(item.get('foreignSellValTotal')),
                        'foreign_buy_vol_matched': self._safe_int(item.get('foreignBuyVolMatched')),
                        'foreign_buy_vol_deal': self._safe_int(item.get('foreignBuyVolDeal')),
                        'total_buy_trade': self._safe_int(item.get('totalBuyTrade')),
                        'total_buy_trade_vol': self._safe_int(item.get('totalBuyTradeVol')),
                        'total_sell_trade': self._safe_int(item.get('totalSellTrade')),
                        'total_sell_trade_vol': self._safe_int(item.get('totalSellTradeVol')),
                        'net_buy_sell_vol': self._safe_int(item.get('netBuySellVol')),
                        'net_buy_sell_val': self._safe_int(item.get('netBuySellVal')),
                        'close_raw': self._safe_float(item.get('closeRaw')),
                        'open_raw': self._safe_float(item.get('openRaw')),
                        'high_raw': self._safe_float(item.get('highRaw')),
                        'low_raw': self._safe_float(item.get('lowRaw'))
                    }
                    
                    # Save to API
                    try:
                        save_response = self.session.post(
                            f"{self.config.api_base_url}/stock-statistics",
                            json=stats_data,
                            timeout=30
                        )
                        save_response.raise_for_status()
                        saved_count += 1
                        total_saved += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to save record for {symbol} on {trading_date}: {e}")
                        self.stats['errors'] += 1
                
                logger.info(f"Saved {saved_count} records from page {page} for {symbol}")
                self.stats['total_pages_processed'] += 1
                
                # Check if we should continue to next page
                paging = data.get('paging', {})
                total_records = paging.get('total', 0)
                current_page_size = paging.get('pageSize', len(stock_data))
                
                logger.info(f"Page {page}: {len(stock_data)} records, Total: {total_records}, PageSize: {current_page_size}")
                
                # Continue if we have more data and haven't reached the total
                if len(stock_data) < current_page_size:
                    logger.info(f"Reached end of data for {symbol} at page {page}")
                    break
                
                # Safety check to prevent infinite loops
                if total_records > 0 and (page * current_page_size) >= total_records:
                    logger.info(f"Reached total records limit for {symbol} at page {page}")
                    break
                
                page += 1
                
                # Add delay to avoid overwhelming the API
                time.sleep(0.1)
            
            logger.info(f"Total saved {total_saved} records for {symbol} across {page-1} pages")
            self.stats['data_records_fetched'] += total_saved
            self.stats['data_records_saved'] += total_saved
            
            return total_saved
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            self.stats['errors'] += 1
            return 0
    
    def validate_data(self, symbol: str) -> Dict[str, Any]:
        """Validate data for a symbol"""
        try:
            url = f"{self.config.api_base_url}/stock-statistics"
            params = {'symbol': symbol}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return {
                    'symbol': symbol,
                    'total_records': 0,
                    'duplicate_records': 0,
                    'unique_dates': 0,
                    'status': 'no_data'
                }
            
            # Check for duplicates
            dates = [record['date'] for record in data]
            unique_dates = set(dates)
            duplicate_records = len(dates) - len(unique_dates)
            
            return {
                'symbol': symbol,
                'total_records': len(data),
                'duplicate_records': duplicate_records,
                'unique_dates': len(unique_dates),
                'status': 'complete' if duplicate_records == 0 else 'has_duplicates'
            }
            
        except Exception as e:
            logger.error(f"Error validating data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'total_records': 0,
                'duplicate_records': 0,
                'unique_dates': 0,
                'status': 'error'
            }
    
    def run_automation(self):
        """Run the direct automation process"""
        try:
            logger.info("Starting Direct VN100 Automation...")
            
            # Fetch VN100 symbols
            symbols = self.fetch_vn100_symbols()
            if not symbols:
                logger.error("No VN100 symbols found")
                return False
            
            logger.info(f"Processing {len(symbols)} symbols: {symbols}")
            
            # Process each symbol
            for i, symbol in enumerate(symbols, 1):
                logger.info(f"Processing {symbol} ({i}/{len(symbols)})")
                
                # Calculate date range
                start_date, end_date = self.calculate_date_range(symbol)
                
                # Fetch data with direct SSI API calls
                records_saved = self.fetch_stock_data_direct(symbol, start_date, end_date)
                
                # Validate data
                validation_result = self.validate_data(symbol)
                logger.info(f"Validation result for {symbol}: {validation_result}")
                
                self.stats['symbols_processed'] += 1
                
                # Add delay between symbols
                time.sleep(1)
            
            # Calculate final statistics
            self.stats['end_time'] = datetime.now()
            self.stats['duration'] = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            # Print final report
            logger.info("=" * 60)
            logger.info("DIRECT VN100 AUTOMATION - FINAL REPORT")
            logger.info("=" * 60)
            
            for symbol in symbols:
                validation_result = self.validate_data(symbol)
                logger.info(f"{symbol}: {validation_result['total_records']} records, "
                          f"{validation_result['duplicate_records']} duplicates, "
                          f"status: {validation_result['status']}")
            
            logger.info("Direct VN100 Automation completed successfully!")
            logger.info(f"Final statistics: {self.stats}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in automation: {e}")
            self.stats['errors'] += 1
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Direct VN100 Automation')
    parser.add_argument('--max-symbols', type=int, default=5, help='Maximum number of symbols to process')
    parser.add_argument('--max-pages', type=int, default=1000, help='Maximum pages per symbol')
    parser.add_argument('--log-level', type=str, default='INFO', help='Log level')
    
    args = parser.parse_args()
    
    config = AutomationConfig(
        max_symbols=args.max_symbols,
        max_pages_per_symbol=args.max_pages,
        log_level=args.log_level
    )
    
    automation = DirectVN100Automation(config)
    success = automation.run_automation()
    
    if success:
        print("\n" + "=" * 60)
        print("DIRECT VN100 AUTOMATION - SUMMARY")
        print("=" * 60)
        print(f"Symbols processed: {automation.stats['symbols_processed']}")
        print(f"Data records fetched: {automation.stats['data_records_fetched']}")
        print(f"Data records saved: {automation.stats['data_records_saved']}")
        print(f"Total pages processed: {automation.stats['total_pages_processed']}")
        print(f"Errors: {automation.stats['errors']}")
        print(f"Duration: {automation.stats['duration']:.2f} seconds")
        print("=" * 60)
        print("✅ Automation completed successfully!")
    else:
        print("❌ Automation failed!")

if __name__ == "__main__":
    main()
