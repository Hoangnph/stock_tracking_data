#!/usr/bin/env python3
"""
Fetch VN-Index historical data using SSI Charts History API.

This script uses the Charts History API endpoint which might have better
historical data coverage for market indices like VN-Index.
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
class ChartsConfig:
    symbol: str
    start_date: date
    end_date: date
    resolution: str = "1d"  # Daily resolution
    output_dir: str = "./output"


def date_to_timestamp(d: date) -> int:
    """Convert date to Unix timestamp"""
    dt = datetime.combine(d, datetime.min.time())
    return int(dt.timestamp())


def build_charts_url(config: ChartsConfig) -> str:
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
    return f"https://iboard-api.ssi.com.vn/statistics/charts/history?{query}"


def fetch_charts_data(url: str, timeout: float = 20.0) -> Dict[str, Any]:
    """Fetch data from Charts History API"""
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://iboard.ssi.com.vn/",
        "Origin": "https://iboard.ssi.com.vn",
        "Connection": "keep-alive",
    }
    
    print(f"Fetching from: {url}")
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def parse_charts_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Charts History API response"""
    rows = []
    
    # Charts API returns data in 'data' field with arrays
    if "data" not in data:
        print("No 'data' field found in response")
        return rows
    
    chart_data = data["data"]
    
    # The response has arrays: 't' (timestamps), 'o' (open), 'h' (high), 'l' (low), 'c' (close), 'v' (volume)
    if isinstance(chart_data, dict):
        timestamps = chart_data.get("t", [])
        opens = chart_data.get("o", [])
        highs = chart_data.get("h", [])
        lows = chart_data.get("l", [])
        closes = chart_data.get("c", [])
        volumes = chart_data.get("v", [])
        
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
                print(f"Error parsing data at index {i}: {e}")
                continue
    
    return rows


def write_csv(rows: List[Dict[str, Any]], out_path: str) -> None:
    """Write data to CSV file"""
    fieldnames = ["date", "open", "high", "low", "close", "volume"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in fieldnames})


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Fetch VN-Index data using Charts History API")
    parser.add_argument("--symbol", default="VNINDEX", help="VN-Index symbol")
    parser.add_argument("--start", default="2020-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default=date.today().isoformat(), help="End date YYYY-MM-DD")
    parser.add_argument("--resolution", default="1d", help="Resolution (1d for daily)")
    parser.add_argument("--output-dir", default="/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output", help="Output directory")
    return parser.parse_args(argv)


def main() -> int:
    """Main function"""
    args = parse_args()
    
    try:
        start_d = datetime.strptime(args.start, "%Y-%m-%d").date()
        end_d = datetime.strptime(args.end, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.", file=sys.stderr)
        return 2

    if start_d > end_d:
        print("Start date must be <= end date", file=sys.stderr)
        return 2

    config = ChartsConfig(
        symbol=args.symbol.upper(),
        start_date=start_d,
        end_date=end_d,
        resolution=args.resolution,
        output_dir=args.output_dir,
    )

    try:
        url = build_charts_url(config)
        print(f"Fetching VN-Index data from {config.start_date} to {config.end_date}")
        print(f"Using symbol: {config.symbol}")
        
        data = fetch_charts_data(url)
        rows = parse_charts_response(data)
        
        if not rows:
            print("No data found in response")
            print("Response structure:", data)
            return 1
        
        # Sort by date
        rows.sort(key=lambda x: x["date"])
        
        # Create output filename
        today = date.today().strftime("%Y-%m-%d")
        out_file = os.path.join(
            config.output_dir,
            f"{today}",
            f"VNINDEX_charts_{config.start_date.isoformat()}_{config.end_date.isoformat()}_full.csv",
        )
        
        # Ensure subdirectory exists
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        
        write_csv(rows, out_file)
        print(f"Data saved to: {out_file}")
        print(f"Total records: {len(rows)}")
        
        if rows:
            print(f"Date range: {rows[0]['date']} to {rows[-1]['date']}")
            print(f"Latest close price: {rows[-1]['close']}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
