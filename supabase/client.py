#!/usr/bin/env python3
"""
Supabase Client
===============

Client for interacting with Supabase database.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import json

try:
    from supabase import create_client, Client
    from supabase.lib.client_options import ClientOptions
except ImportError:
    print("Error: supabase-py not installed. Run: pip install supabase")
    raise

from .config import SupabaseConfig, TableNames, DatabaseSchema, BatchConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase operations"""
    
    def __init__(self, config: SupabaseConfig):
        """Initialize Supabase client"""
        self.config = config
        self.client: Client = create_client(
            config.url,
            config.key,
            options=ClientOptions(
                auto_refresh_token=True,
                persist_session=True
            )
        )
        logger.info("Supabase client initialized")
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Simple query to test connection
            result = self.client.table("data_sources").select("id").limit(1).execute()
            logger.info("✅ Supabase connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            return False
    
    async def create_tables(self) -> bool:
        """Create database tables"""
        try:
            logger.info("Creating database tables...")
            
            # Note: Supabase doesn't support direct SQL execution from Python client
            # Tables should be created via Supabase dashboard or SQL editor
            logger.info("⚠️  Please create tables manually in Supabase dashboard:")
            logger.info("Tables to create:")
            logger.info(f"- {TableNames.STOCK_DATA}")
            logger.info(f"- {TableNames.VN100_SYMBOLS}")
            logger.info(f"- {TableNames.VNINDEX_DATA}")
            logger.info(f"- {TableNames.DATA_SOURCES}")
            
            return True
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    async def upload_stock_data(self, data: List[Dict[str, Any]], symbol: str) -> bool:
        """Upload stock data for a symbol"""
        try:
            logger.info(f"Uploading {len(data)} records for {symbol}")
            
            # Prepare data for upload
            upload_data = []
            for record in data:
                upload_record = {
                    "symbol": symbol,
                    "date": record["date"],
                    "open": record.get("open"),
                    "high": record.get("high"),
                    "low": record.get("low"),
                    "close": record.get("close"),
                    "volume": record.get("volume", 0)
                }
                upload_data.append(upload_record)
            
            # Upload in batches
            batch_size = BatchConfig.BATCH_SIZE
            total_batches = (len(upload_data) + batch_size - 1) // batch_size
            
            for i in range(0, len(upload_data), batch_size):
                batch = upload_data[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                logger.info(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} records)")
                
                try:
                    result = self.client.table(TableNames.STOCK_DATA).upsert(batch).execute()
                    logger.info(f"✅ Batch {batch_num} uploaded successfully")
                except Exception as e:
                    logger.error(f"❌ Batch {batch_num} failed: {e}")
                    return False
            
            logger.info(f"✅ All data uploaded for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading stock data for {symbol}: {e}")
            return False
    
    async def upload_vnindex_data(self, data: List[Dict[str, Any]]) -> bool:
        """Upload VN-Index data"""
        try:
            logger.info(f"Uploading {len(data)} VN-Index records")
            
            # Prepare data for upload
            upload_data = []
            for record in data:
                upload_record = {
                    "date": record["date"],
                    "open": record.get("open"),
                    "high": record.get("high"),
                    "low": record.get("low"),
                    "close": record.get("close"),
                    "volume": record.get("volume", 0)
                }
                upload_data.append(upload_record)
            
            # Upload in batches
            batch_size = BatchConfig.BATCH_SIZE
            for i in range(0, len(upload_data), batch_size):
                batch = upload_data[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                logger.info(f"Uploading VN-Index batch {batch_num}")
                
                try:
                    result = self.client.table(TableNames.VNINDEX_DATA).upsert(batch).execute()
                    logger.info(f"✅ VN-Index batch {batch_num} uploaded")
                except Exception as e:
                    logger.error(f"❌ VN-Index batch {batch_num} failed: {e}")
                    return False
            
            logger.info("✅ All VN-Index data uploaded")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading VN-Index data: {e}")
            return False
    
    async def upload_vn100_symbols(self, symbols: List[Dict[str, Any]]) -> bool:
        """Upload VN100 symbols list"""
        try:
            logger.info(f"Uploading {len(symbols)} VN100 symbols")
            
            # Prepare data for upload
            upload_data = []
            for symbol_data in symbols:
                upload_record = {
                    "symbol": symbol_data.get("symbol", ""),
                    "company_name": symbol_data.get("company_name", ""),
                    "sector": symbol_data.get("sector", ""),
                    "market_cap": symbol_data.get("market_cap"),
                    "is_active": symbol_data.get("is_active", True)
                }
                upload_data.append(upload_record)
            
            try:
                result = self.client.table(TableNames.VN100_SYMBOLS).upsert(upload_data).execute()
                logger.info("✅ VN100 symbols uploaded successfully")
                return True
            except Exception as e:
                logger.error(f"❌ VN100 symbols upload failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading VN100 symbols: {e}")
            return False
    
    async def get_upload_status(self, symbol: str) -> Dict[str, Any]:
        """Get upload status for a symbol"""
        try:
            result = self.client.table(TableNames.STOCK_DATA).select("date").eq("symbol", symbol).execute()
            
            if result.data:
                dates = [record["date"] for record in result.data]
                return {
                    "symbol": symbol,
                    "record_count": len(dates),
                    "date_range": {
                        "min": min(dates) if dates else None,
                        "max": max(dates) if dates else None
                    },
                    "last_updated": datetime.now().isoformat()
                }
            else:
                return {
                    "symbol": symbol,
                    "record_count": 0,
                    "date_range": None,
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting status for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    async def cleanup_old_data(self, symbol: str, before_date: date) -> bool:
        """Clean up old data for a symbol"""
        try:
            logger.info(f"Cleaning up old data for {symbol} before {before_date}")
            
            result = self.client.table(TableNames.STOCK_DATA).delete().eq("symbol", symbol).lt("date", before_date.isoformat()).execute()
            
            logger.info(f"✅ Cleaned up old data for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up data for {symbol}: {e}")
            return False


# Example usage
async def main():
    """Example usage of SupabaseClient"""
    try:
        # Load configuration
        config = SupabaseConfig.from_env()
        
        # Initialize client
        client = SupabaseClient(config)
        
        # Test connection
        if await client.test_connection():
            print("✅ Supabase connection successful")
        else:
            print("❌ Supabase connection failed")
            return
        
        # Example: Get upload status
        status = await client.get_upload_status("ACB")
        print(f"Upload status: {json.dumps(status, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
