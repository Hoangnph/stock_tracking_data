#!/usr/bin/env python3
"""
VN100 Data Fetcher - Simple Version
===================================

Simple script to fetch all VN100 symbols data from 2010-01-01 to present day.

Usage:
    python fetch_vn100.py
"""

import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from fetch_vn100_complete import main

if __name__ == "__main__":
    print("🚀 Fetching all VN100 symbols data from 2010-01-01 to present day...")
    print("📊 This will fetch data for all 100 VN100 symbols...")
    print("⏳ This may take 10-15 minutes...")
    print("🔧 Using Charts History API for complete data coverage...")
    print()
    
    exit_code = main()
    
    if exit_code == 0:
        print()
        print("✅ VN100 data has been successfully fetched!")
        print("📁 Check the output directory for the CSV files.")
        print("📈 Data includes complete OHLCV from 2010 to present.")
    else:
        print()
        print("❌ Failed to fetch VN100 data.")
        print("Please check the error messages above.")
    
    sys.exit(exit_code)
