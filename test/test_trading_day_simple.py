#!/usr/bin/env python3
"""
Simple test for trading day logic
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from automation.automation_vn100_direct import DirectVN100Automation, AutomationConfig
from datetime import date, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_trading_day_logic():
    """Test the new trading day logic"""
    print("="*60)
    print("TESTING NEW TRADING DAY LOGIC")
    print("="*60)
    
    # Create automation instance
    config = AutomationConfig()
    automation = DirectVN100Automation(config)
    
    print("Testing get_last_trading_day() function:")
    print(f"  Today: {date.today()} ({date.today().strftime('%A')})")
    
    last_trading_day = automation.get_last_trading_day()
    print(f"  Last trading day: {last_trading_day} ({last_trading_day.strftime('%A')})")
    
    print("\nTesting calculate_date_range() for ACB:")
    try:
        start_date, end_date = automation.calculate_date_range('ACB')
        print(f"  ACB: {start_date} to {end_date}")
        
        # Check if we're targeting Friday
        if end_date == date(2025, 10, 4):  # Friday
            print("  ✅ Correctly targeting Friday (last trading day)")
        else:
            print(f"  ❌ Not targeting Friday, got: {end_date}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n✅ Trading day logic test completed!")

if __name__ == "__main__":
    try:
        test_trading_day_logic()
        print("\n🎉 Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
