#!/usr/bin/env python3
"""
Comprehensive Test Suite for Extended SSI API System
Version: 2.0 - Complete Data Coverage Testing

This test suite covers:
- Database schema validation
- API endpoint testing
- Pipeline functionality testing
- Data integrity validation
- Performance testing
"""

import unittest
import requests
import json
import time
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class TestExtendedSSISystem(unittest.TestCase):
    """Comprehensive test suite for extended SSI system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.api_base_url = "http://localhost:8000"
        cls.test_symbol = "ACB"
        cls.test_date = date.today()
        
        # Test data samples
        cls.sample_company_data = {
            "symbol": "TEST",
            "company_name": "Test Company",
            "company_name_en": "Test Company Ltd",
            "sector": "Technology",
            "exchange": "HOSE",
            "isin": "VN000000TEST",
            "par_value": 10000,
            "trading_unit": 100
        }
        
        cls.sample_stock_statistics = {
            "symbol": "TEST",
            "date": cls.test_date.isoformat(),
            "current_price": 25.5,
            "change_amount": 0.5,
            "change_percent": 2.0,
            "volume": 1000000,
            "value": 25500000,
            "ceiling_price": 28.0,
            "floor_price": 23.0,
            "ref_price": 25.0,
            "avg_price": 25.3,
            "foreign_buy_vol_total": 100000,
            "foreign_sell_vol_total": 50000,
            "net_buy_sell_vol": 50000,
            "net_buy_sell_val": 1275000
        }
        
        cls.sample_stock_price = {
            "symbol": "TEST",
            "timestamp": datetime.now().isoformat(),
            "resolution": "1d",
            "open_price": 25.0,
            "high_price": 26.0,
            "low_price": 24.5,
            "close_price": 25.5,
            "volume": 1000000,
            "status": "ok"
        }
        
        cls.sample_order_book = {
            "symbol": "TEST",
            "timestamp": datetime.now().isoformat(),
            "bid_price": 25.4,
            "bid_volume": 10000,
            "offer_price": 25.6,
            "offer_volume": 15000,
            "level": 1
        }
        
        cls.sample_foreign_trading = {
            "symbol": "TEST",
            "date": cls.test_date.isoformat(),
            "buy_volume": 100000,
            "buy_value": 2550000,
            "sell_volume": 50000,
            "sell_value": 1275000,
            "net_volume": 50000,
            "net_value": 1275000,
            "current_room": 1000000
        }
        
        cls.sample_session_info = {
            "symbol": "TEST",
            "date": cls.test_date.isoformat(),
            "session_type": "NORMAL",
            "odd_session": "NORMAL",
            "session_pt": "NORMAL",
            "exchange_session": "HOSE",
            "is_pre_session_price": False
        }
    
    def test_01_health_check(self):
        """Test API health check endpoint"""
        response = requests.get(f"{self.api_base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["version"], "2.0.0")
        self.assertEqual(data["fields_coverage"], "112/112 (100%)")
        self.assertIn("database", data)
        self.assertIn("redis", data)
    
    def test_02_companies_crud(self):
        """Test companies CRUD operations with extended fields"""
        # Create company
        response = requests.post(f"{self.api_base_url}/companies", json=self.sample_company_data)
        self.assertEqual(response.status_code, 200)
        
        company = response.json()
        self.assertEqual(company["symbol"], "TEST")
        self.assertEqual(company["company_name_en"], "Test Company Ltd")
        self.assertEqual(company["isin"], "VN000000TEST")
        self.assertEqual(company["par_value"], 10000)
        
        # Get company
        response = requests.get(f"{self.api_base_url}/companies/TEST")
        self.assertEqual(response.status_code, 200)
        
        company = response.json()
        self.assertEqual(company["symbol"], "TEST")
        self.assertEqual(company["trading_unit"], 100)
        
        # Update company
        update_data = self.sample_company_data.copy()
        update_data["company_name"] = "Updated Test Company"
        update_data["market_cap"] = 1000000000
        
        response = requests.put(f"{self.api_base_url}/companies/TEST", json=update_data)
        self.assertEqual(response.status_code, 200)
        
        company = response.json()
        self.assertEqual(company["company_name"], "Updated Test Company")
        self.assertEqual(company["market_cap"], 1000000000)
        
        # Clean up
        response = requests.delete(f"{self.api_base_url}/companies/TEST")
        self.assertEqual(response.status_code, 204)
    
    def test_03_stock_statistics_crud(self):
        """Test stock statistics CRUD with all extended fields"""
        # Create stock statistics
        response = requests.post(f"{self.api_base_url}/stock-statistics", json=self.sample_stock_statistics)
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        self.assertEqual(stats["symbol"], "TEST")
        self.assertEqual(stats["current_price"], 25.5)
        self.assertEqual(stats["ceiling_price"], 28.0)
        self.assertEqual(stats["floor_price"], 23.0)
        self.assertEqual(stats["foreign_buy_vol_total"], 100000)
        self.assertEqual(stats["net_buy_sell_vol"], 50000)
        
        # Get stock statistics
        response = requests.get(f"{self.api_base_url}/stock-statistics?symbol=TEST")
        self.assertEqual(response.status_code, 200)
        
        stats_list = response.json()
        self.assertGreater(len(stats_list), 0)
        self.assertEqual(stats_list[0]["symbol"], "TEST")
        self.assertEqual(stats_list[0]["ref_price"], 25.0)
        self.assertEqual(stats_list[0]["avg_price"], 25.3)
    
    def test_04_stock_prices_crud(self):
        """Test stock prices CRUD with extended fields"""
        # Create stock price
        response = requests.post(f"{self.api_base_url}/stock-prices", json=self.sample_stock_price)
        self.assertEqual(response.status_code, 200)
        
        price = response.json()
        self.assertEqual(price["symbol"], "TEST")
        self.assertEqual(price["resolution"], "1d")
        self.assertEqual(price["status"], "ok")
        
        # Get stock prices
        response = requests.get(f"{self.api_base_url}/stock-prices?symbol=TEST&resolution=1d")
        self.assertEqual(response.status_code, 200)
        
        prices = response.json()
        self.assertGreater(len(prices), 0)
        self.assertEqual(prices[0]["symbol"], "TEST")
        self.assertEqual(prices[0]["close_price"], 25.5)
    
    def test_05_order_book_crud(self):
        """Test order book CRUD operations"""
        # Create order book entry
        response = requests.post(f"{self.api_base_url}/order-book", json=self.sample_order_book)
        self.assertEqual(response.status_code, 200)
        
        order = response.json()
        self.assertEqual(order["symbol"], "TEST")
        self.assertEqual(order["level"], 1)
        self.assertEqual(order["bid_price"], 25.4)
        self.assertEqual(order["offer_price"], 25.6)
        
        # Get order book
        response = requests.get(f"{self.api_base_url}/order-book?symbol=TEST")
        self.assertEqual(response.status_code, 200)
        
        orders = response.json()
        self.assertGreater(len(orders), 0)
        self.assertEqual(orders[0]["symbol"], "TEST")
        self.assertEqual(orders[0]["bid_volume"], 10000)
    
    def test_06_foreign_trading_crud(self):
        """Test foreign trading CRUD operations"""
        # Create foreign trading data
        response = requests.post(f"{self.api_base_url}/foreign-trading", json=self.sample_foreign_trading)
        self.assertEqual(response.status_code, 200)
        
        trading = response.json()
        self.assertEqual(trading["symbol"], "TEST")
        self.assertEqual(trading["buy_volume"], 100000)
        self.assertEqual(trading["net_volume"], 50000)
        self.assertEqual(trading["current_room"], 1000000)
        
        # Get foreign trading data
        response = requests.get(f"{self.api_base_url}/foreign-trading?symbol=TEST")
        self.assertEqual(response.status_code, 200)
        
        trading_list = response.json()
        self.assertGreater(len(trading_list), 0)
        self.assertEqual(trading_list[0]["symbol"], "TEST")
        self.assertEqual(trading_list[0]["sell_value"], 1275000)
    
    def test_07_session_info_crud(self):
        """Test session info CRUD operations"""
        # Create session info
        response = requests.post(f"{self.api_base_url}/session-info", json=self.sample_session_info)
        self.assertEqual(response.status_code, 200)
        
        session = response.json()
        self.assertEqual(session["symbol"], "TEST")
        self.assertEqual(session["session_type"], "NORMAL")
        self.assertEqual(session["exchange_session"], "HOSE")
        self.assertFalse(session["is_pre_session_price"])
        
        # Get session info
        response = requests.get(f"{self.api_base_url}/session-info?symbol=TEST")
        self.assertEqual(response.status_code, 200)
        
        sessions = response.json()
        self.assertGreater(len(sessions), 0)
        self.assertEqual(sessions[0]["symbol"], "TEST")
        self.assertEqual(sessions[0]["odd_session"], "NORMAL")
    
    def test_08_analytics_endpoints(self):
        """Test analytics endpoints"""
        # Test stock summary
        response = requests.get(f"{self.api_base_url}/analytics/stock-summary/{self.test_symbol}")
        self.assertEqual(response.status_code, 200)
        
        summary = response.json()
        self.assertEqual(summary["symbol"], self.test_symbol)
        self.assertIn("statistics", summary)
        self.assertIn("order_book", summary)
        self.assertIn("foreign_trading", summary)
        
        # Test VN100 summary
        response = requests.get(f"{self.api_base_url}/analytics/vn100-summary")
        self.assertEqual(response.status_code, 200)
        
        vn100_summary = response.json()
        self.assertIn("vn100_components", vn100_summary)
        self.assertIn("total_components", vn100_summary)
        self.assertGreaterEqual(vn100_summary["total_components"], 0)
    
    def test_09_data_validation(self):
        """Test data validation and error handling"""
        # Test invalid company data
        invalid_company = {"symbol": ""}  # Empty symbol
        response = requests.post(f"{self.api_base_url}/companies", json=invalid_company)
        self.assertIn(response.status_code, [400, 422])
        
        # Test invalid stock statistics
        invalid_stats = {"symbol": "TEST", "date": "invalid-date"}
        response = requests.post(f"{self.api_base_url}/stock-statistics", json=invalid_stats)
        self.assertIn(response.status_code, [400, 422])
        
        # Test invalid stock price
        invalid_price = {"symbol": "TEST", "timestamp": "invalid-timestamp"}
        response = requests.post(f"{self.api_base_url}/stock-prices", json=invalid_price)
        self.assertIn(response.status_code, [400, 422])
    
    def test_10_performance_testing(self):
        """Test API performance"""
        # Test bulk operations
        start_time = time.time()
        
        # Create multiple companies
        for i in range(10):
            company_data = self.sample_company_data.copy()
            company_data["symbol"] = f"PERF{i:03d}"
            company_data["company_name"] = f"Performance Test Company {i}"
            
            response = requests.post(f"{self.api_base_url}/companies", json=company_data)
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (10 seconds for 10 operations)
        self.assertLess(duration, 10.0)
        print(f"Performance test: 10 company creations in {duration:.2f} seconds")
        
        # Clean up
        for i in range(10):
            response = requests.delete(f"{self.api_base_url}/companies/PERF{i:03d}")
            self.assertEqual(response.status_code, 204)
    
    def test_11_cors_headers(self):
        """Test CORS headers"""
        response = requests.options(f"{self.api_base_url}/companies")
        self.assertIn("Access-Control-Allow-Origin", response.headers)
        self.assertIn("Access-Control-Allow-Methods", response.headers)
        self.assertIn("Access-Control-Allow-Headers", response.headers)
    
    def test_12_pagination(self):
        """Test pagination functionality"""
        # Test companies pagination
        response = requests.get(f"{self.api_base_url}/companies?skip=0&limit=5")
        self.assertEqual(response.status_code, 200)
        
        companies = response.json()
        self.assertLessEqual(len(companies), 5)
        
        # Test stock statistics pagination
        response = requests.get(f"{self.api_base_url}/stock-statistics?symbol={self.test_symbol}&skip=0&limit=10")
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        self.assertLessEqual(len(stats), 10)
    
    def test_13_filtering(self):
        """Test filtering functionality"""
        # Test company filtering by sector
        response = requests.get(f"{self.api_base_url}/companies?sector=Technology")
        self.assertEqual(response.status_code, 200)
        
        # Test stock statistics filtering by date range
        from_date = (date.today() - timedelta(days=7)).isoformat()
        to_date = date.today().isoformat()
        
        response = requests.get(f"{self.api_base_url}/stock-statistics?symbol={self.test_symbol}&from_date={from_date}&to_date={to_date}")
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        for stat in stats:
            self.assertGreaterEqual(stat["date"], from_date)
            self.assertLessEqual(stat["date"], to_date)
    
    def test_14_error_handling(self):
        """Test error handling"""
        # Test 404 for non-existent company
        response = requests.get(f"{self.api_base_url}/companies/NONEXISTENT")
        self.assertEqual(response.status_code, 404)
        
        # Test 404 for non-existent stock statistics
        response = requests.get(f"{self.api_base_url}/stock-statistics?symbol=NONEXISTENT")
        self.assertEqual(response.status_code, 200)  # Should return empty list
        
        # Test invalid endpoint
        response = requests.get(f"{self.api_base_url}/invalid-endpoint")
        self.assertEqual(response.status_code, 404)
    
    def test_15_data_integrity(self):
        """Test data integrity and constraints"""
        # Test unique constraint on company symbol
        company_data = self.sample_company_data.copy()
        company_data["symbol"] = "UNIQUE_TEST"
        
        # First creation should succeed
        response = requests.post(f"{self.api_base_url}/companies", json=company_data)
        self.assertEqual(response.status_code, 200)
        
        # Second creation with same symbol should update (ON CONFLICT DO UPDATE)
        company_data["company_name"] = "Updated Unique Test"
        response = requests.post(f"{self.api_base_url}/companies", json=company_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = requests.get(f"{self.api_base_url}/companies/UNIQUE_TEST")
        self.assertEqual(response.status_code, 200)
        company = response.json()
        self.assertEqual(company["company_name"], "Updated Unique Test")
        
        # Clean up
        response = requests.delete(f"{self.api_base_url}/companies/UNIQUE_TEST")
        self.assertEqual(response.status_code, 204)

class TestExtendedPipeline(unittest.TestCase):
    """Test extended pipeline functionality"""
    
    def test_pipeline_config(self):
        """Test pipeline configuration"""
        from pipeline.ssi_pipeline_extended import ExtendedPipelineConfig
        
        config = ExtendedPipelineConfig(
            max_stocks=3,
            days_back=2,
            resolution="1d",
            dry_run=True
        )
        
        self.assertEqual(config.max_stocks, 3)
        self.assertEqual(config.days_back, 2)
        self.assertEqual(config.resolution, "1d")
        self.assertTrue(config.dry_run)
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        from pipeline.ssi_pipeline_extended import ExtendedSSIPipeline, ExtendedPipelineConfig
        
        config = ExtendedPipelineConfig(dry_run=True)
        pipeline = ExtendedSSIPipeline(config)
        
        self.assertIsNotNone(pipeline.session)
        self.assertIsNotNone(pipeline.stats)
        self.assertEqual(pipeline.stats['companies_processed'], 0)
    
    def test_data_conversion_methods(self):
        """Test data conversion methods"""
        from pipeline.ssi_pipeline_extended import ExtendedSSIPipeline, ExtendedPipelineConfig
        
        config = ExtendedPipelineConfig(dry_run=True)
        pipeline = ExtendedSSIPipeline(config)
        
        # Test safe float conversion
        self.assertEqual(pipeline._safe_float("25.5"), 25.5)
        self.assertEqual(pipeline._safe_float(""), None)
        self.assertEqual(pipeline._safe_float(None), None)
        
        # Test safe int conversion
        self.assertEqual(pipeline._safe_int("1000"), 1000)
        self.assertEqual(pipeline._safe_int(""), None)
        self.assertEqual(pipeline._safe_int(None), None)
        
        # Test timestamp conversion
        timestamp = pipeline._convert_timestamp(1640995200)  # 2022-01-01 00:00:00
        self.assertIsNotNone(timestamp)
        self.assertIn("2022-01-01", timestamp)

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_suite.addTest(unittest.makeSuite(TestExtendedSSISystem))
    test_suite.addTest(unittest.makeSuite(TestExtendedPipeline))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print(f"{'='*60}")
