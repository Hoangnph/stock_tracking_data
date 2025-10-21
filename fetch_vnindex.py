#!/usr/bin/env python3
"""
VN-Index Data Fetcher - Simple Version
=====================================

Simple script to fetch VN-Index data from 2020-01-01 to 2025-10-18.

Usage:
    python fetch_vnindex.py
"""

import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from fetch_vnindex_complete import main

if __name__ == "__main__":
    # Set default arguments for VN-Index from 2020-01-01 to 2025-10-18
    sys.argv = [
        'fetch_vnindex.py',
        '--start', '2020-01-01',
        '--end', '2025-10-18'
    ]
    
    print("Fetching VN-Index data from 2020-01-01 to 2025-10-18...")
    print("This may take a few moments...")
    print()
    
    exit_code = main()
    
    if exit_code == 0:
        print()
        print("✅ VN-Index data has been successfully fetched!")
        print("📁 Check the output directory for the CSV file.")
    else:
        print()
        print("❌ Failed to fetch VN-Index data.")
        print("Please check the error messages above.")
    
    sys.exit(exit_code)

