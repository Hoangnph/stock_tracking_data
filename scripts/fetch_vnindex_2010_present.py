#!/usr/bin/env python3
"""
VN-Index Complete Data Fetcher (2010-Present)
============================================

This script fetches complete VN-Index data from 2010-01-01 to present day
with proper handling of missing data and holidays.

Features:
- Fetches data from 2010-01-01 to current date
- Handles missing trading days appropriately
- Provides comprehensive data analysis
- Exports clean CSV with proper formatting
- Includes data validation and gap analysis

Usage:
    python fetch_vnindex_2010_present.py
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import requests


@dataclass
class VNIndexConfig:
    """Configuration for VN-Index data fetching"""
    start_date: date
    end_date: date
    symbol: str = "VNINDEX"
    resolution: str = "1d"
    output_dir: str = "/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output"
    api_url: str = "https://iboard-api.ssi.com.vn/statistics/charts/history"
    timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 2.0


def get_current_date() -> date:
    """Get current date"""
    return date.today()


def date_to_timestamp(d: date) -> int:
    """Convert date to Unix timestamp"""
    dt = datetime.combine(d, datetime.min.time())
    return int(dt.timestamp())


def build_api_url(config: VNIndexConfig) -> str:
    """Build Charts History API URL"""
    from_ts = date_to_timestamp(config.start_date)
    to_ts = date_to_timestamp(config.end_date)
    
    params = {
        "resolution": config.resolution,
        "symbol": config.symbol,
        "from": str(from_ts),
        "to": str(to_ts),
    }
    
    query = "&".join(f"{k}={requests.utils.quote(v)}" for k, v in params.items())
    return f"{config.api_url}?{query}"


def fetch_data_with_retry(url: str, config: VNIndexConfig) -> Dict[str, Any]:
    """Fetch data from API with retry logic"""
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://iboard.ssi.com.vn/",
        "Origin": "https://iboard.ssi.com.vn",
        "Connection": "keep-alive",
    }
    
    for attempt in range(config.retry_attempts):
        try:
            print(f"Fetching data (attempt {attempt + 1}/{config.retry_attempts})...")
            resp = requests.get(url, headers=headers, timeout=config.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < config.retry_attempts - 1:
                print(f"Retrying in {config.retry_delay} seconds...")
                time.sleep(config.retry_delay)
            else:
                raise


def parse_vnindex_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse VN-Index data from Charts History API response"""
    rows = []
    
    if "data" not in data:
        raise ValueError("No 'data' field found in API response")
    
    chart_data = data["data"]
    
    if not isinstance(chart_data, dict):
        raise ValueError("Invalid data format in API response")
    
    # Extract arrays from response
    timestamps = chart_data.get("t", [])
    opens = chart_data.get("o", [])
    highs = chart_data.get("h", [])
    lows = chart_data.get("l", [])
    closes = chart_data.get("c", [])
    volumes = chart_data.get("v", [])
    
    if not timestamps:
        raise ValueError("No timestamp data found")
    
    # Ensure all arrays have the same length
    min_length = min(len(timestamps), len(opens), len(highs), len(lows), len(closes), len(volumes))
    
    print(f"Processing {min_length} data points...")
    
    for i in range(min_length):
        try:
            # Convert timestamp to date
            timestamp = timestamps[i]
            dt = datetime.fromtimestamp(timestamp)
            date_str = dt.date()
            
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


def validate_and_clean_data(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and clean the data"""
    validated_rows = []
    
    for row in rows:
        # Check for required fields
        if not row.get("date") or not row.get("close"):
            continue
            
        # Validate numeric values
        try:
            if row["open"] is not None:
                float(row["open"])
            if row["high"] is not None:
                float(row["high"])
            if row["low"] is not None:
                float(row["low"])
            if row["close"] is not None:
                float(row["close"])
            if row["volume"] is not None:
                int(row["volume"])
        except (ValueError, TypeError):
            print(f"Warning: Invalid numeric data for date {row['date']}")
            continue
            
        validated_rows.append(row)
    
    return validated_rows


def analyze_data_completeness(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze data completeness and gaps"""
    if not rows:
        return {}
    
    # Sort data by date
    rows.sort(key=lambda x: x["date"])
    
    start_date = rows[0]["date"]
    end_date = rows[-1]["date"]
    
    # Calculate expected trading days (excluding weekends)
    expected_days = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            expected_days += 1
        current_date += timedelta(days=1)
    
    actual_days = len(rows)
    missing_days = expected_days - actual_days
    
    # Analyze gaps
    gaps = []
    prev_date = None
    
    for row in rows:
        current_date = row["date"]
        if prev_date:
            days_diff = (current_date - prev_date).days
            if days_diff > 1:
                gaps.append({
                    'start': prev_date,
                    'end': current_date,
                    'gap_days': days_diff - 1
                })
        prev_date = current_date
    
    return {
        'total_records': actual_days,
        'expected_trading_days': expected_days,
        'missing_days': missing_days,
        'completeness_percentage': (actual_days / expected_days * 100) if expected_days > 0 else 0,
        'date_range': f"{start_date} to {end_date}",
        'total_gaps': len(gaps),
        'significant_gaps': len([g for g in gaps if g['gap_days'] > 3])
    }


def write_csv(rows: List[Dict[str, Any]], out_path: str) -> None:
    """Write data to CSV file"""
    fieldnames = ["date", "open", "high", "low", "close", "volume"]
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in rows:
            writer.writerow({
                'date': r['date'].strftime('%Y-%m-%d'),
                'open': r.get('open'),
                'high': r.get('high'),
                'low': r.get('low'),
                'close': r.get('close'),
                'volume': r.get('volume')
            })


def generate_summary(rows: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary statistics"""
    if not rows:
        return {}
    
    closes = [float(r["close"]) for r in rows if r["close"] is not None]
    volumes = [int(r["volume"]) for r in rows if r["volume"] is not None]
    
    return {
        "total_records": len(rows),
        "date_range": analysis.get('date_range', ''),
        "completeness": f"{analysis.get('completeness_percentage', 0):.1f}%",
        "missing_days": analysis.get('missing_days', 0),
        "first_close": rows[0]["close"],
        "last_close": rows[-1]["close"],
        "min_close": min(closes) if closes else None,
        "max_close": max(closes) if closes else None,
        "avg_volume": sum(volumes) / len(volumes) if volumes else 0,
        "total_volume": sum(volumes) if volumes else 0,
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Fetch complete VN-Index data from 2010 to present",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_vnindex_2010_present.py
  python fetch_vnindex_2010_present.py --start 2015-01-01
  python fetch_vnindex_2010_present.py --end 2024-12-31
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
        "--symbol",
        default="VNINDEX",
        help="VN-Index symbol (default: VNINDEX)"
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

    config = VNIndexConfig(
        symbol=args.symbol.upper(),
        start_date=start_d,
        end_date=end_d,
        output_dir=args.output_dir,
    )

    try:
        print("=" * 80)
        print("VN-INDEX COMPLETE DATA FETCHER (2010-PRESENT)")
        print("=" * 80)
        print(f"Symbol: {config.symbol}")
        print(f"Date Range: {config.start_date} to {config.end_date}")
        print(f"Output Directory: {config.output_dir}")
        print("-" * 80)
        
        # Build API URL
        url = build_api_url(config)
        print(f"API URL: {url}")
        print("-" * 80)
        
        # Fetch data
        data = fetch_data_with_retry(url, config)
        
        # Parse data
        print("Parsing data...")
        rows = parse_vnindex_data(data)
        
        # Validate and clean data
        print("Validating and cleaning data...")
        validated_rows = validate_and_clean_data(rows)
        
        if not validated_rows:
            print("Error: No valid data found", file=sys.stderr)
            return 1
        
        # Analyze data completeness
        print("Analyzing data completeness...")
        analysis = analyze_data_completeness(validated_rows)
        
        # Generate output filename
        today = date.today().strftime("%Y-%m-%d")
        out_file = os.path.join(
            config.output_dir,
            f"{today}",
            f"VNINDEX_complete_{config.start_date.isoformat()}_{config.end_date.isoformat()}_full.csv",
        )
        
        # Write CSV
        print("Writing CSV file...")
        write_csv(validated_rows, out_file)
        
        # Generate summary
        summary = generate_summary(validated_rows, analysis)
        
        print("-" * 80)
        print("SUCCESS!")
        print("-" * 80)
        print(f"📁 Data saved to: {out_file}")
        print(f"📊 Total records: {summary['total_records']:,}")
        print(f"📅 Date range: {summary['date_range']}")
        print(f"✅ Data completeness: {summary['completeness']}")
        print(f"⚠️  Missing days: {summary['missing_days']}")
        print(f"📈 First close price: {summary['first_close']}")
        print(f"📈 Last close price: {summary['last_close']}")
        print(f"📉 Min close price: {summary['min_close']}")
        print(f"📈 Max close price: {summary['max_close']}")
        print(f"📊 Average volume: {summary['avg_volume']:,.0f}")
        print(f"📊 Total volume: {summary['total_volume']:,.0f}")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
