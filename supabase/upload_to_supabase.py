#!/usr/bin/env python3
"""
CSV to Supabase Uploader
========================

Script to upload CSV data files to Supabase database.

Usage:
    python upload_to_supabase.py --input-dir output/2025-10-20
    python upload_to_supabase.py --file output/2025-10-20/ACB_daily_2010-01-01_2025-10-20_full.csv
"""

import argparse
import asyncio
import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .client import SupabaseClient
from .config import SupabaseConfig


class CSVUploader:
    """CSV to Supabase uploader"""
    
    def __init__(self, supabase_client: SupabaseClient):
        """Initialize uploader"""
        self.client = supabase_client
        self.upload_stats = {
            "total_files": 0,
            "successful_uploads": 0,
            "failed_uploads": 0,
            "total_records": 0,
            "start_time": datetime.now(),
            "errors": []
        }
    
    def parse_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV file and return data"""
        data = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string values to appropriate types
                    processed_row = {
                        "date": row["date"],
                        "open": float(row["open"]) if row["open"] and row["open"] != "" else None,
                        "high": float(row["high"]) if row["high"] and row["high"] != "" else None,
                        "low": float(row["low"]) if row["low"] and row["low"] != "" else None,
                        "close": float(row["close"]) if row["close"] and row["close"] != "" else None,
                        "volume": int(float(row["volume"])) if row["volume"] and row["volume"] != "" else 0,
                    }
                    data.append(processed_row)
            
            return data
            
        except Exception as e:
            print(f"Error parsing CSV file {file_path}: {e}")
            return []
    
    def extract_symbol_from_filename(self, filename: str) -> str:
        """Extract symbol from filename"""
        # Example: ACB_daily_2010-01-01_2025-10-20_full.csv -> ACB
        return filename.split('_')[0]
    
    async def upload_csv_file(self, file_path: str) -> bool:
        """Upload a single CSV file"""
        try:
            print(f"📄 Processing: {os.path.basename(file_path)}")
            
            # Parse CSV data
            data = self.parse_csv_file(file_path)
            if not data:
                print(f"❌ No data found in {file_path}")
                self.upload_stats["failed_uploads"] += 1
                self.upload_stats["errors"].append(f"No data in {file_path}")
                return False
            
            # Extract symbol from filename
            symbol = self.extract_symbol_from_filename(os.path.basename(file_path))
            
            # Upload to Supabase
            success = await self.client.upload_stock_data(data, symbol)
            
            if success:
                print(f"✅ {symbol}: {len(data)} records uploaded")
                self.upload_stats["successful_uploads"] += 1
                self.upload_stats["total_records"] += len(data)
                return True
            else:
                print(f"❌ {symbol}: Upload failed")
                self.upload_stats["failed_uploads"] += 1
                self.upload_stats["errors"].append(f"Upload failed for {symbol}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading {file_path}: {e}")
            self.upload_stats["failed_uploads"] += 1
            self.upload_stats["errors"].append(f"Error uploading {file_path}: {e}")
            return False
    
    async def upload_directory(self, input_dir: str, pattern: str = "*.csv") -> bool:
        """Upload all CSV files in a directory"""
        try:
            input_path = Path(input_dir)
            if not input_path.exists():
                print(f"❌ Directory not found: {input_dir}")
                return False
            
            # Find all CSV files
            csv_files = list(input_path.glob(pattern))
            if not csv_files:
                print(f"❌ No CSV files found in {input_dir}")
                return False
            
            print(f"📁 Found {len(csv_files)} CSV files in {input_dir}")
            print("-" * 60)
            
            self.upload_stats["total_files"] = len(csv_files)
            
            # Upload each file
            for csv_file in csv_files:
                await self.upload_csv_file(str(csv_file))
                print("-" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing directory {input_dir}: {e}")
            return False
    
    def print_summary(self):
        """Print upload summary"""
        end_time = datetime.now()
        duration = end_time - self.upload_stats["start_time"]
        
        print("=" * 60)
        print("📊 UPLOAD SUMMARY")
        print("=" * 60)
        print(f"📁 Total files processed: {self.upload_stats['total_files']}")
        print(f"✅ Successful uploads: {self.upload_stats['successful_uploads']}")
        print(f"❌ Failed uploads: {self.upload_stats['failed_uploads']}")
        print(f"📊 Total records uploaded: {self.upload_stats['total_records']:,}")
        print(f"⏱️  Duration: {duration}")
        print(f"🚀 Average speed: {self.upload_stats['total_records'] / duration.total_seconds():.1f} records/second")
        
        if self.upload_stats["errors"]:
            print("\n❌ ERRORS:")
            for error in self.upload_stats["errors"]:
                print(f"  - {error}")
        
        print("=" * 60)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Upload CSV data to Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python upload_to_supabase.py --input-dir output/2025-10-20
  python upload_to_supabase.py --file output/2025-10-20/ACB_daily_2010-01-01_2025-10-20_full.csv
  python upload_to_supabase.py --input-dir output/2025-10-20 --pattern "*VNINDEX*.csv"
        """
    )
    
    parser.add_argument(
        "--input-dir",
        help="Input directory containing CSV files"
    )
    parser.add_argument(
        "--file",
        help="Single CSV file to upload"
    )
    parser.add_argument(
        "--pattern",
        default="*.csv",
        help="File pattern to match (default: *.csv)"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test Supabase connection only"
    )
    
    args = parser.parse_args()
    
    if not args.input_dir and not args.file and not args.test_connection:
        parser.print_help()
        return 1
    
    try:
        # Load Supabase configuration
        config = SupabaseConfig.from_env()
        
        # Initialize Supabase client
        client = SupabaseClient(config)
        
        # Test connection
        if not await client.test_connection():
            print("❌ Supabase connection failed")
            return 1
        
        if args.test_connection:
            print("✅ Supabase connection successful")
            return 0
        
        # Initialize uploader
        uploader = CSVUploader(client)
        
        # Upload data
        if args.file:
            # Upload single file
            success = await uploader.upload_csv_file(args.file)
        elif args.input_dir:
            # Upload directory
            success = await uploader.upload_directory(args.input_dir, args.pattern)
        else:
            print("❌ No input specified")
            return 1
        
        # Print summary
        uploader.print_summary()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
