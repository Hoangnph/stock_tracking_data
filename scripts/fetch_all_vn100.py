#!/usr/bin/env python3
"""
VN100 Complete Data Fetcher
===========================

This script fetches OHLCV data for all VN100 symbols from 2010-01-01 to present day.

Features:
- Fetches VN100 symbol list from SSI API
- Downloads OHLCV data for each symbol
- Handles missing data appropriately
- Provides progress tracking and error handling
- Exports to CSV format compatible with existing system

Usage:
    python fetch_all_vn100.py
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests


@dataclass
class VN100Config:
    """Configuration for VN100 data fetching"""
    start_date: date
    end_date: date
    output_dir: str = "/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output"
    vn100_api_url: str = "https://iboard-query.ssi.com.vn/stock/group/VN100"
    stock_info_api_url: str = "https://iboard-api.ssi.com.vn/statistics/company/ssmi/stock-info"
    timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 2.0
    rate_limit_delay: float = 1.0


def get_current_date() -> date:
    """Get current date"""
    return date.today()


def date_to_timestamp(d: date) -> int:
    """Convert date to Unix timestamp"""
    dt = datetime.combine(d, datetime.min.time())
    return int(dt.timestamp())


def format_ddmmyyyy(d: date) -> str:
    """Format date to DD/MM/YYYY format"""
    return d.strftime("%d/%m/%Y")


def fetch_vn100_symbols(config: VN100Config) -> List[str]:
    """Fetch VN100 symbols from SSI API"""
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://iboard.ssi.com.vn/",
        "Origin": "https://iboard.ssi.com.vn",
        "Connection": "keep-alive",
    }
    
    for attempt in range(config.retry_attempts):
        try:
            print(f"Fetching VN100 symbols (attempt {attempt + 1}/{config.retry_attempts})...")
            resp = requests.get(config.vn100_api_url, headers=headers, timeout=config.timeout)
            resp.raise_for_status()
            
            data = resp.json()
            symbols = []
            
            if isinstance(data, dict) and 'data' in data:
                raw_components = data['data']
            elif isinstance(data, list):
                raw_components = data
            else:
                print("Error: Invalid VN100 data format")
                return []
            
            for item in raw_components:
                symbol = item.get('stock_symbol', '') or item.get('stockSymbol', '')
                if symbol:
                    symbols.append(symbol)
            
            print(f"Found {len(symbols)} VN100 symbols")
            return symbols
            
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < config.retry_attempts - 1:
                print(f"Retrying in {config.retry_delay} seconds...")
                time.sleep(config.retry_delay)
            else:
                raise


def build_stock_info_url(symbol: str, config: VN100Config, page: int) -> str:
    """Build Stock Info API URL"""
    params = {
        "symbol": symbol,
        "page": str(page),
        "pageSize": "100",
        "fromDate": format_ddmmyyyy(config.start_date),
        "toDate": format_ddmmyyyy(config.end_date),
    }
    
    query = "&".join(f"{k}={requests.utils.quote(v)}" for k, v in params.items())
    return f"{config.stock_info_api_url}?{query}"


def safe_get(d: Dict[str, Any], keys: List[str]) -> Optional[Any]:
    """Safely get value from dictionary with multiple possible keys"""
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def parse_stock_row(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse a single row from Stock Info API response"""
    # Date may appear as 'date' or 'tradingDate'
    date_str = safe_get(raw, ["date", "tradingDate"])
    if not date_str:
        return None
    
    # Normalize date to YYYY-MM-DD
    try:
        if len(date_str) == 10 and date_str[2] == "/":
            # dd/mm/yyyy
            dt = datetime.strptime(date_str, "%d/%m/%Y").date()
        else:
            # yyyy-mm-dd
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None

    open_val = safe_get(raw, ["open_price", "openPrice", "open", "open_raw"])
    high_val = safe_get(raw, ["high_price", "highPrice", "high", "high_raw"])
    low_val = safe_get(raw, ["low_price", "lowPrice", "low", "low_raw"])
    close_val = safe_get(raw, ["close_price", "closePrice", "close", "close_raw"])
    volume_val = safe_get(raw, ["volume", "totalMatchVol", "total_match_vol"])

    return {
        "date": dt.isoformat(),
        "open": try_float(open_val),
        "high": try_float(high_val),
        "low": try_float(low_val),
        "close": try_float(close_val),
        "volume": try_int(volume_val),
    }


def try_float(v: Any) -> Optional[float]:
    """Safely convert value to float"""
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def try_int(v: Any) -> Optional[int]:
    """Safely convert value to int"""
    try:
        if v is None:
            return None
        return int(float(v))
    except Exception:
        return None


def fetch_stock_data(symbol: str, config: VN100Config) -> List[Dict[str, Any]]:
    """Fetch OHLCV data for a single symbol"""
    all_rows: List[Dict[str, Any]] = []
    
    for page in range(1, 1000):  # Reasonable limit
        url = build_stock_info_url(symbol, config, page)
        
        try:
            headers = {
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
                "Referer": "https://iboard.ssi.com.vn/",
                "Origin": "https://iboard.ssi.com.vn",
                "Connection": "keep-alive",
            }
            
            resp = requests.get(url, headers=headers, timeout=config.timeout)
            resp.raise_for_status()
            payload = resp.json()
            
        except Exception as exc:
            if page == 1:
                print(f"Error fetching first page for {symbol}: {exc}")
                return []
            break

        # Extract items from response
        items = []
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            for key in ["data", "items", "rows", "list", "records", "payload"]:
                if key in payload and isinstance(payload[key], list):
                    items = payload[key]
                    break
            # Sometimes nested like { data: { items: [] } }
            if not items and "data" in payload and isinstance(payload["data"], dict):
                data = payload["data"]
                for key in ["items", "rows", "list", "records"]:
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break

        if not items:
            break

        parsed = [r for r in (parse_stock_row(item) for item in items) if r is not None]
        if not parsed:
            break

        all_rows.extend(parsed)

        # If returned less than page size, likely last page
        if len(items) < 100:
            break

        time.sleep(config.rate_limit_delay)

    # Deduplicate by date (keep latest occurrence)
    dedup: Dict[str, Dict[str, Any]] = {}
    for r in all_rows:
        dedup[r["date"]] = r
    # Sort ascending by date
    result = [dedup[k] for k in sorted(dedup.keys())]
    
    return result


def write_csv(rows: List[Dict[str, Any]], out_path: str) -> None:
    """Write data to CSV file"""
    fieldnames = ["date", "open", "high", "low", "close", "volume"]
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in fieldnames})


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Fetch OHLCV data for all VN100 symbols",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_all_vn100.py
  python fetch_all_vn100.py --start 2015-01-01
  python fetch_all_vn100.py --end 2024-12-31
        """
    )
    parser.add_argument(
        "--start", 
        default="2010-01-01", 
        help="Start date in YYYY-MM-DD format (default: 2010-01-01)"
    )
    parser.add_argument(
        "--end", 
        help="End date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--output-dir", 
        default="/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output",
        help="Output directory for CSV files"
    )
    parser.add_argument(
        "--max-symbols",
        type=int,
        help="Maximum number of symbols to process (for testing)"
    )
    return parser.parse_args(argv)


def main() -> int:
    """Main function"""
    args = parse_args()
    
    try:
        start_d = datetime.strptime(args.start, "%Y-%m-%d").date()
        end_d = datetime.strptime(args.end, "%Y-%m-%d").date() if args.end else get_current_date()
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD.", file=sys.stderr)
        return 2

    if start_d > end_d:
        print("Error: Start date must be <= end date", file=sys.stderr)
        return 2

    config = VN100Config(
        start_date=start_d,
        end_date=end_d,
        output_dir=args.output_dir,
    )

    try:
        print("=" * 80)
        print("VN100 COMPLETE DATA FETCHER")
        print("=" * 80)
        print(f"Date Range: {config.start_date} to {config.end_date}")
        print(f"Output Directory: {config.output_dir}")
        print("-" * 80)
        
        # Fetch VN100 symbols
        symbols = fetch_vn100_symbols(config)
        if not symbols:
            print("Error: No VN100 symbols found", file=sys.stderr)
            return 1
        
        # Limit symbols if specified
        if args.max_symbols:
            symbols = symbols[:args.max_symbols]
            print(f"Limited to {len(symbols)} symbols for testing")
        
        print(f"Processing {len(symbols)} VN100 symbols...")
        print("-" * 80)
        
        # Process each symbol
        success_count = 0
        failed_symbols = []
        
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] Processing {symbol}...")
            
            try:
                # Fetch data
                rows = fetch_stock_data(symbol, config)
                
                if rows:
                    # Generate output filename
                    today = date.today().strftime("%Y-%m-%d")
                    out_file = os.path.join(
                        config.output_dir,
                        f"{today}",
                        f"{symbol}_daily_{config.start_date.isoformat()}_{config.end_date.isoformat()}_full.csv",
                    )
                    
                    # Write CSV
                    write_csv(rows, out_file)
                    
                    print(f"  ✅ {symbol}: {len(rows)} records saved")
                    success_count += 1
                else:
                    print(f"  ⚠️  {symbol}: No data found")
                    failed_symbols.append(symbol)
                
            except Exception as e:
                print(f"  ❌ {symbol}: Error - {e}")
                failed_symbols.append(symbol)
            
            # Rate limiting
            if i < len(symbols):
                time.sleep(config.rate_limit_delay)
        
        # Summary
        print("-" * 80)
        print("SUMMARY")
        print("-" * 80)
        print(f"✅ Successful: {success_count}/{len(symbols)}")
        print(f"❌ Failed: {len(failed_symbols)}")
        
        if failed_symbols:
            print(f"Failed symbols: {failed_symbols}")
        
        # List output files
        today = date.today().strftime("%Y-%m-%d")
        output_path = os.path.join(config.output_dir, f"{today}")
        if os.path.exists(output_path):
            files = [f for f in os.listdir(output_path) if f.endswith('.csv')]
            print(f"📄 Total CSV files created: {len(files)}")
            print(f"📁 Files saved to: {output_path}")
        
        print("=" * 80)
        
        return 0 if success_count > 0 else 1
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
