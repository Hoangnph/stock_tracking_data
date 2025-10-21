#!/usr/bin/env python3
"""
VN100 Simple Data Fetcher
=========================

Simple script to fetch VN100 symbols and their data from 2010 to present.

Usage:
    python fetch_vn100_simple.py
"""

import sys
import os
import requests
import csv
import time
from datetime import date, datetime

def get_vn100_symbols():
    """Get VN100 symbols from SSI API"""
    url = "https://iboard-query.ssi.com.vn/stock/group/VN100"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://iboard.ssi.com.vn/",
        "Origin": "https://iboard.ssi.com.vn",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        symbols = []
        if isinstance(data, dict) and 'data' in data:
            components = data['data']
        elif isinstance(data, list):
            components = data
        else:
            return []
        
        for item in components:
            symbol = item.get('stock_symbol', '') or item.get('stockSymbol', '')
            if symbol:
                symbols.append(symbol)
        
        return symbols
    except Exception as e:
        print(f"Error fetching VN100 symbols: {e}")
        return []

def fetch_symbol_data(symbol, start_date="2010-01-01", end_date=None):
    """Fetch data for a single symbol using Charts History API"""
    if end_date is None:
        end_date = date.today().strftime("%Y-%m-%d")
    
    # Convert dates to timestamps
    start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
    
    url = f"https://iboard-api.ssi.com.vn/statistics/charts/history?resolution=1d&symbol={symbol}&from={start_ts}&to={end_ts}"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Referer": "https://iboard.ssi.com.vn/",
        "Origin": "https://iboard.ssi.com.vn",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "data" not in data:
            return []
        
        chart_data = data["data"]
        if not isinstance(chart_data, dict):
            return []
        
        # Extract arrays
        timestamps = chart_data.get("t", [])
        opens = chart_data.get("o", [])
        highs = chart_data.get("h", [])
        lows = chart_data.get("l", [])
        closes = chart_data.get("c", [])
        volumes = chart_data.get("v", [])
        
        rows = []
        min_length = min(len(timestamps), len(opens), len(highs), len(lows), len(closes), len(volumes))
        
        for i in range(min_length):
            try:
                dt = datetime.fromtimestamp(timestamps[i])
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
                continue
        
        return rows
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return []

def save_to_csv(rows, symbol, output_dir):
    """Save data to CSV file"""
    today = date.today().strftime("%Y-%m-%d")
    output_path = os.path.join(output_dir, f"{today}")
    os.makedirs(output_path, exist_ok=True)
    
    filename = f"{symbol}_daily_2010-01-01_{date.today().strftime('%Y-%m-%d')}_full.csv"
    filepath = os.path.join(output_path, filename)
    
    fieldnames = ["date", "open", "high", "low", "close", "volume"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    
    return filepath

def main():
    """Main function"""
    print("🚀 Fetching VN100 symbols and data from 2010-01-01 to present...")
    print("⏳ This may take several minutes...")
    print()
    
    # Get VN100 symbols
    print("📊 Fetching VN100 symbols...")
    symbols = get_vn100_symbols()
    if not symbols:
        print("❌ No VN100 symbols found")
        return 1
    
    print(f"✅ Found {len(symbols)} VN100 symbols")
    print(f"Symbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
    print()
    
    # Setup output directory
    output_dir = "/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output"
    
    # Process each symbol
    success_count = 0
    failed_symbols = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] Processing {symbol}...")
        
        try:
            # Fetch data
            rows = fetch_symbol_data(symbol)
            
            if rows:
                # Save to CSV
                filepath = save_to_csv(rows, symbol, output_dir)
                print(f"  ✅ {symbol}: {len(rows)} records saved to {os.path.basename(filepath)}")
                success_count += 1
            else:
                print(f"  ⚠️  {symbol}: No data found")
                failed_symbols.append(symbol)
            
        except Exception as e:
            print(f"  ❌ {symbol}: Error - {e}")
            failed_symbols.append(symbol)
        
        # Rate limiting
        if i < len(symbols):
            time.sleep(1)
    
    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{len(symbols)}")
    print(f"❌ Failed: {len(failed_symbols)}")
    
    if failed_symbols:
        print(f"Failed symbols: {failed_symbols}")
    
    # List output files
    today = date.today().strftime("%Y-%m-%d")
    output_path = os.path.join(output_dir, f"{today}")
    if os.path.exists(output_path):
        files = [f for f in os.listdir(output_path) if f.endswith('.csv')]
        print(f"📄 Total CSV files created: {len(files)}")
        print(f"📁 Files saved to: {output_path}")
    
    print("=" * 60)
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
