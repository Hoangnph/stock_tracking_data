#!/usr/bin/env python3
"""
VN100 Progress Monitor
======================

Monitor the progress of VN100 data fetching.

Usage:
    python monitor_vn100.py
"""

import os
import time
from datetime import datetime

def monitor_progress():
    """Monitor VN100 fetching progress"""
    output_dir = "/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output/2025-10-20"
    
    print("🔍 Monitoring VN100 data fetching progress...")
    print("📁 Output directory:", output_dir)
    print("⏰ Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("-" * 60)
    
    last_count = 0
    start_time = time.time()
    
    while True:
        try:
            if os.path.exists(output_dir):
                files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
                vn100_files = [f for f in files if not f.startswith('VNINDEX')]
                
                current_count = len(vn100_files)
                elapsed_time = time.time() - start_time
                
                if current_count > last_count:
                    print(f"✅ Progress: {current_count}/100 VN100 symbols completed")
                    print(f"⏱️  Elapsed time: {elapsed_time/60:.1f} minutes")
                    print(f"📊 Rate: {current_count/(elapsed_time/60):.1f} symbols/minute")
                    
                    if current_count >= 100:
                        print("🎉 All VN100 symbols completed!")
                        break
                    
                    last_count = current_count
                
                # Show latest files
                if vn100_files:
                    latest_files = sorted(vn100_files)[-3:]
                    print(f"📄 Latest files: {', '.join(latest_files)}")
                
                print("-" * 60)
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_progress()
