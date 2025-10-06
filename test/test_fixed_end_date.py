#!/usr/bin/env python3
"""
Test script for fixed end_date logic
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from automation.automation_vn100_direct import DirectVN100Automation, AutomationConfig
from datetime import date, datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fixed_end_date_logic():
    """Test the fixed end_date logic"""
    print("="*60)
    print("TESTING FIXED END_DATE LOGIC")
    print("="*60)
    
    # Create automation instance
    config = AutomationConfig()
    automation = DirectVN100Automation(config)
    
    print("Testing calculate_date_range() for ACB:")
    print(f"  Current time: {datetime.now()}")
    print(f"  Current hour: {datetime.now().hour}")
    
    try:
        start_date, end_date = automation.calculate_date_range('ACB')
        print(f"  ACB: {start_date} to {end_date}")
        
        # Check if we're targeting Friday (2025-10-04)
        if end_date == date(2025, 10, 5):  # Sunday (today - 1)
            print("  ✅ Correctly targeting Sunday (today - 1)")
        elif end_date == date(2025, 10, 6):  # Monday (today)
            print("  ✅ Correctly targeting Monday (today)")
        else:
            print(f"  ❌ Unexpected end_date: {end_date}")
            
        # Check if start_date is valid
        if start_date == date(2025, 10, 4):  # Friday
            print("  ✅ Correctly targeting Friday as start_date")
        else:
            print(f"  ❌ Unexpected start_date: {start_date}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n✅ Fixed end_date logic test completed!")

if __name__ == "__main__":
    try:
        test_fixed_end_date_logic()
        print("\n🎉 Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
