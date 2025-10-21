#!/usr/bin/env python3
"""
Export OHLCV data for all VN100 symbols from 2020-01-01 to today
"""

import os
import sys
import time
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from automation.automation_vn100_direct import DirectVN100Automation, AutomationConfig


def export_all_vn100():
    """Export all VN100 symbols"""
    # Create output directory with today's date
    run_date = date.today().strftime('%Y-%m-%d')
    output_dir = f"/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output/{run_date}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize automation to get VN100 symbols
    config = AutomationConfig(max_symbols=100)  # Get all VN100 symbols
    automation = DirectVN100Automation(config)
    
    # Fetch VN100 symbols
    symbols = automation.fetch_vn100_symbols()
    if not symbols:
        print("❌ No VN100 symbols found")
        return False
    
    print(f"📊 Found {len(symbols)} VN100 symbols: {symbols}")
    print(f"📁 Output directory: {output_dir}")
    
    # Export each symbol
    success_count = 0
    failed_symbols = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n🔄 [{i}/{len(symbols)}] Exporting {symbol}...")
        
        try:
            # Run export command
            cmd = f"python3 scripts/export_ssi_automation_style.py --symbol {symbol} --start 2020-01-01 --end $(date +%F) --output-dir {output_dir}"
            result = os.system(cmd)
            
            if result == 0:
                success_count += 1
                print(f"✅ {symbol} exported successfully")
            else:
                failed_symbols.append(symbol)
                print(f"❌ {symbol} export failed")
                
        except Exception as e:
            failed_symbols.append(symbol)
            print(f"❌ {symbol} export error: {e}")
        
        # Add delay to avoid rate limiting
        time.sleep(1)
    
    # Summary
    print(f"\n📊 EXPORT SUMMARY")
    print(f"✅ Successful: {success_count}/{len(symbols)}")
    print(f"❌ Failed: {len(failed_symbols)}")
    
    if failed_symbols:
        print(f"Failed symbols: {failed_symbols}")
    
    print(f"📁 Files saved to: {output_dir}")
    
    # List all exported files
    files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    print(f"📄 Total files: {len(files)}")
    
    return success_count == len(symbols)


if __name__ == "__main__":
    success = export_all_vn100()
    sys.exit(0 if success else 1)

