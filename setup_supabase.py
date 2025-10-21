#!/usr/bin/env python3
"""
Supabase Setup Wrapper
======================

Simple wrapper script to setup Supabase integration from the project root.

Usage:
    python setup_supabase.py
"""

import sys
import os

# Add supabase directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'supabase'))

# Import and run the setup script
from setup_supabase import main

if __name__ == "__main__":
    print("🚀 Supabase Integration Setup")
    print("📁 Using supabase/ package")
    print("-" * 40)
    
    exit_code = main()
    sys.exit(exit_code)
