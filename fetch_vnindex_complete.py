#!/usr/bin/env python3
"""
VN-Index Data Fetcher - Complete Version (2010-Present)
======================================================

Simple script to fetch complete VN-Index data from 2010-01-01 to present day.

Usage:
    python fetch_vnindex_complete.py
"""

import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from fetch_vnindex_2010_present import main

if __name__ == "__main__":
    print("🚀 Fetching VN-Index data from 2010-01-01 to present day...")
    print("📊 This will include all trading days with proper gap handling...")
    print("⏳ This may take a few moments...")
    print()
    
    exit_code = main()
    
    if exit_code == 0:
        print()
        print("✅ VN-Index complete data has been successfully fetched!")
        print("📁 Check the output directory for the CSV file.")
        print("📈 Data includes proper handling of missing trading days.")
    else:
        print()
        print("❌ Failed to fetch VN-Index data.")
        print("Please check the error messages above.")
    
    sys.exit(exit_code)
