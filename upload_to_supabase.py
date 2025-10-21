#!/usr/bin/env python3
"""
Supabase Upload Wrapper
=======================

Simple wrapper script to upload data to Supabase from the project root.

Usage:
    python upload_to_supabase.py --input-dir output/2025-10-20
    python upload_to_supabase.py --test-connection
"""

import sys
import os

# Add supabase directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'supabase'))

# Import and run the main upload script
from upload_to_supabase import main
import asyncio

if __name__ == "__main__":
    print("🚀 Supabase Data Uploader")
    print("📁 Using supabase/ package")
    print("-" * 40)
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
