"""
Supabase Integration Package
===========================

Package for integrating with Supabase database for stock data management.

Modules:
- config: Supabase configuration and database schema
- client: Supabase client for database operations
- uploader: CSV data uploader
- setup: Setup script for easy installation
"""

__version__ = "1.0.0"
__author__ = "Stock Tracking Data Team"

# Import main classes for easy access
from .config import SupabaseConfig, TableNames, DatabaseSchema, BatchConfig
from .client import SupabaseClient

__all__ = [
    "SupabaseConfig",
    "TableNames", 
    "DatabaseSchema",
    "BatchConfig",
    "SupabaseClient"
]
