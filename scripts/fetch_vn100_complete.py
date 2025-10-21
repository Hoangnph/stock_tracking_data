#!/usr/bin/env python3
"""
VN100 Complete Data Fetcher - Improved Version
==============================================

This script fetches complete OHLCV data for all VN100 symbols from 2010-01-01 to present day
using Charts History API (same as VN-Index) for better data coverage.

Features:
- Uses Charts History API for complete data coverage
- Fetches VN100 symbol list from SSI API
- Handles missing data appropriately
- Provides progress tracking and error handling
- Exports to CSV format compatible with existing system

Usage:
    python fetch_vn100_complete.py
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
    charts_api_url: str = "https://iboard-api.ssi.com.vn/statistics/charts/history"
    timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 2.0
    rate_limit_delay: float = 1.5


def get_current_date() -> date:
    """Get current date"""
    return date.today()


def date_to_timestamp(d: date) -> int:
    """Convert date to Unix timestamp"""
    dt = datetime.combine(d, datetime.min.time())
    return int(dt.timestamp())


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


def build_charts_url(symbol: str, config: VN100Config) -> str:
    """Build Charts History API URL"""
    from_ts = date_to_timestamp(config.start_date)
    to_ts = date_to_timestamp(config.end_date)
    
    params = {
        "resolution": "1d",
        "symbol": symbol,
        "from": str(from_ts),
        "to": str(to_ts),
    }
    
    query = "&".join(f"{k}={requests.utils.quote(v)}" for k, v in params.items())
    return f"{config.charts_api_url}?{query}"


def fetch_charts_data(url: str, timeout: float = 30.0) -> Dict[str, Any]:
    """Fetch data from Charts History API"""
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://iboard.ssi.com.vn/",
        "Origin": "https://iboard.ssi.com.vn",
        "Connection": "keep-alive",
    }
    
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def parse_charts_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Charts History API response"""
    rows = []
    
    if "data" not in data:
        return rows
    
    chart_data = data["data"]
    
    if not isinstance(chart_data, dict):
        return rows
    
    # Extract arrays from response
    timestamps = chart_data.get("t", [])
    opens = chart_data.get("o", [])
    highs = chart_data.get("h", [])
    lows = chart_data.get("l", [])
    closes = chart_data.get("c", [])
    volumes = chart_data.get("v", [])
    
    if not timestamps:
        return rows
    
    # Ensure all arrays have the same length
    min_length = min(len(timestamps), len(opens), len(highs), len(lows), len(closes), len(volumes))
    
    for i in range(min_length):
        try:
            # Convert timestamp to date
            timestamp = timestamps[i]
            dt = datetime.fromtimestamp(timestamp)
            date_str = dt.date().isoformat()
            
            row = {
                "date": date_str,
                "open": opens[i] if i < len(opens) else None,
                "high": highs[i] if i < len(highs) else None,
                "low": lows[i] if i < len(lows) else None,
                "close": closes[i] if i < len(closes) else None,
                "volume": volumes[i] if i < len(volumes) else 0,
            }
            rows.append(row)
        except Exception as e:
            print(f"Warning: Error parsing data at index {i}: {e}")
            continue
    
    return rows


def fetch_symbol_data(symbol: str, config: VN100Config) -> List[Dict[str, Any]]:
    """Fetch OHLCV data for a single symbol using Charts History API"""
    try:
        url = build_charts_url(symbol, config)
        data = fetch_charts_data(url, config.timeout)
        rows = parse_charts_response(data)
        
        # Sort by date
        rows.sort(key=lambda x: x["date"])
        
        return rows
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return []


def write_csv(rows: List[Dict[str, Any]], symbol: str, config: VN100Config) -> str:
    """Write data to CSV file"""
    fieldnames = ["date", "open", "high", "low", "close", "volume"]
    
    # Generate output filename
    today = date.today().strftime("%Y-%m-%d")
    out_file = os.path.join(
        config.output_dir,
        f"{today}",
        f"{symbol}_daily_{config.start_date.isoformat()}_{config.end_date.isoformat()}_full.csv",
    )
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in fieldnames})
    
    return out_file


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Fetch complete OHLCV data for all VN100 symbols",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_vn100_complete.py
  python fetch_vn100_complete.py --start 2015-01-01
  python fetch_vn100_complete.py --end 2024-12-31
  python fetch_vn100_complete.py --max-symbols 10
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
        print("VN100 COMPLETE DATA FETCHER - IMPROVED VERSION")
        print("=" * 80)
        print(f"Date Range: {config.start_date} to {config.end_date}")
        print(f"Output Directory: {config.output_dir}")
        print(f"API: Charts History API (same as VN-Index)")
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
        total_records = 0
        
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] Processing {symbol}...")
            
            try:
                # Fetch data
                rows = fetch_symbol_data(symbol, config)
                
                if rows:
                    # Save to CSV
                    out_file = write_csv(rows, symbol, config)
                    print(f"  ✅ {symbol}: {len(rows)} records saved")
                    print(f"      Date range: {rows[0]['date']} to {rows[-1]['date']}")
                    print(f"      File: {os.path.basename(out_file)}")
                    success_count += 1
                    total_records += len(rows)
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
        print(f"📊 Total records: {total_records:,}")
        
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
