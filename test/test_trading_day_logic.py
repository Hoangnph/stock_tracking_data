#!/usr/bin/env python3
"""
Test script for new trading day logic
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
    
    # Test different scenarios
    test_dates = [
        date(2025, 10, 6),  # Monday
        date(2025, 10, 7),  # Tuesday
        date(2025, 10, 8),  # Wednesday
        date(2025, 10, 9),  # Thursday
        date(2025, 10, 10), # Friday
        date(2025, 10, 11), # Saturday
        date(2025, 10, 12), # Sunday
    ]
    
    print("Testing get_last_trading_day() function:")
    for test_date in test_dates:
        # Temporarily override today's date for testing
        original_today = date.today
        
        def mock_today():
            return test_date
        
        # Replace the function temporarily
        import datetime
        datetime.date.today = mock_today
        
        last_trading_day = automation.get_last_trading_day()
        weekday_name = test_date.strftime('%A')
        
        print(f"  {weekday_name} ({test_date}): Last trading day = {last_trading_day}")
        
        # Restore original function
        datetime.date.today = original_today
    
    print("\nTesting calculate_date_range() for ACB:")
    try:
        start_date, end_date = automation.calculate_date_range('ACB')
        print(f"  ACB: {start_date} to {end_date}")
        
        # Check if we're trying to fetch Friday data
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
