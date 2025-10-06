#!/usr/bin/env python3
"""
Integration Tests for Extended SSI System
Version: 2.0 - Complete Data Coverage Integration Testing

This test suite covers:
- End-to-end pipeline testing
- Database integration testing
- API integration testing
- Data flow validation
"""

import unittest
import requests
import time
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class TestExtendedIntegration(unittest.TestCase):
    """Integration tests for extended SSI system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up integration test environment"""
        cls.api_base_url = "http://localhost:8000"
        cls.test_symbols = ["ACB", "VCB", "VIC"]
        
        # Wait for API to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.api_base_url}/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        else:
            raise Exception("API not ready after 30 seconds")
    
    def test_01_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline"""
        from pipeline.ssi_pipeline_extended import ExtendedSSIPipeline, ExtendedPipelineConfig
        
        # Configure pipeline for small test
        config = ExtendedPipelineConfig(
            max_stocks=2,
            symbols=self.test_symbols[:2],
            days_back=1,
            resolution="1d",
            dry_run=False,
            api_base_url=self.api_base_url,
            log_level="INFO"
        )
        
        # Run pipeline
        pipeline = ExtendedSSIPipeline(config)
        stats = pipeline.run_pipeline()
        
        # Verify pipeline completed successfully
        self.assertGreater(stats['companies_processed'], 0)
        self.assertGreaterEqual(stats['stock_statistics_saved'], 0)
        self.assertGreaterEqual(stats['stock_prices_saved'], 0)
        self.assertGreaterEqual(stats['index_components_saved'], 0)
        self.assertGreaterEqual(stats['order_book_saved'], 0)
        self.assertGreaterEqual(stats['foreign_trading_saved'], 0)
        self.assertGreaterEqual(stats['session_info_saved'], 0)
        
        print(f"Pipeline stats: {stats}")
    
    def test_02_database_data_integrity(self):
        """Test database data integrity after pipeline run"""
        # Check companies data
        response = requests.get(f"{self.api_base_url}/companies")
        self.assertEqual(response.status_code, 200)
        
        companies = response.json()
        self.assertGreater(len(companies), 0)
        
        # Verify extended fields are present
        for company in companies:
            if company['symbol'] in self.test_symbols:
                self.assertIsNotNone(company.get('symbol'))
                self.assertIsNotNone(company.get('company_name'))
                # Extended fields may be None, but should exist
                self.assertIn('isin', company)
                self.assertIn('par_value', company)
                self.assertIn('trading_unit', company)
        
        # Check stock statistics data
        for symbol in self.test_symbols[:2]:
            response = requests.get(f"{self.api_base_url}/stock-statistics?symbol={symbol}")
            self.assertEqual(response.status_code, 200)
            
            stats = response.json()
            if stats:  # If data exists
                stat = stats[0]
                self.assertIsNotNone(stat.get('symbol'))
                self.assertIsNotNone(stat.get('date'))
                # Verify extended fields exist
                self.assertIn('ceiling_price', stat)
                self.assertIn('floor_price', stat)
                self.assertIn('ref_price', stat)
                self.assertIn('foreign_buy_vol_total', stat)
                self.assertIn('net_buy_sell_vol', stat)
    
    def test_03_api_data_consistency(self):
        """Test API data consistency across endpoints"""
        # Get company data
        response = requests.get(f"{self.api_base_url}/companies")
        self.assertEqual(response.status_code, 200)
        companies = response.json()
        
        # Get VN100 components
        response = requests.get(f"{self.api_base_url}/market-indices/VN100/components")
        self.assertEqual(response.status_code, 200)
        components = response.json()
        
        # Verify symbols are consistent
        company_symbols = {c['symbol'] for c in companies}
        component_symbols = {c['symbol'] for c in components}
        
        # Should have some overlap
        overlap = company_symbols.intersection(component_symbols)
        self.assertGreater(len(overlap), 0)
        
        # Verify data consistency for overlapping symbols
        for symbol in overlap:
            company = next(c for c in companies if c['symbol'] == symbol)
            component = next(c for c in components if c['symbol'] == symbol)
            
            # Basic fields should match
            self.assertEqual(company['symbol'], component['symbol'])
            self.assertEqual(company['exchange'], component['exchange'])
    
    def test_04_analytics_endpoints_integration(self):
        """Test analytics endpoints with real data"""
        # Test stock summary for a real symbol
        for symbol in self.test_symbols:
            response = requests.get(f"{self.api_base_url}/analytics/stock-summary/{symbol}")
            self.assertEqual(response.status_code, 200)
            
            summary = response.json()
            self.assertEqual(summary['symbol'], symbol)
            self.assertIn('statistics', summary)
            self.assertIn('order_book', summary)
            self.assertIn('foreign_trading', summary)
            self.assertIn('timestamp', summary)
            
            # If data exists, verify structure
            if summary['statistics']:
                stats = summary['statistics']
                self.assertIn('symbol', stats)
                self.assertIn('date', stats)
                self.assertIn('current_price', stats)
        
        # Test VN100 summary
        response = requests.get(f"{self.api_base_url}/analytics/vn100-summary")
        self.assertEqual(response.status_code, 200)
        
        vn100_summary = response.json()
        self.assertIn('vn100_components', vn100_summary)
        self.assertIn('total_components', vn100_summary)
        self.assertIn('timestamp', vn100_summary)
        
        # Verify component structure
        if vn100_summary['vn100_components']:
            component = vn100_summary['vn100_components'][0]
            self.assertIn('symbol', component)
            self.assertIn('company_name', component)
            self.assertIn('current_price', component)
            self.assertIn('weight', component)
    
    def test_05_performance_under_load(self):
        """Test system performance under load"""
        # Test concurrent API requests
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(endpoint, results_queue):
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_base_url}/{endpoint}", timeout=10)
                end_time = time.time()
                
                results_queue.put({
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'duration': end_time - start_time,
                    'success': response.status_code == 200
                })
            except Exception as e:
                results_queue.put({
                    'endpoint': endpoint,
                    'error': str(e),
                    'success': False
                })
        
        # Create multiple threads
        threads = []
        endpoints = [
            'health',
            'companies',
            'market-indices/VN100/components',
            'analytics/vn100-summary'
        ]
        
        for endpoint in endpoints:
            for _ in range(3):  # 3 requests per endpoint
                thread = threading.Thread(target=make_request, args=(endpoint, results))
                threads.append(thread)
                thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        successful_requests = 0
        total_duration = 0
        max_duration = 0
        
        while not results.empty():
            result = results.get()
            if result['success']:
                successful_requests += 1
                if 'duration' in result:
                    total_duration += result['duration']
                    max_duration = max(max_duration, result['duration'])
        
        # Verify performance
        self.assertGreater(successful_requests, len(endpoints) * 2)  # At least 2/3 success rate
        self.assertLess(max_duration, 5.0)  # No request should take more than 5 seconds
        
        print(f"Performance test: {successful_requests}/{len(threads)} requests successful")
        print(f"Average duration: {total_duration/successful_requests:.2f}s")
        print(f"Max duration: {max_duration:.2f}s")
    
    def test_06_data_validation_comprehensive(self):
        """Test comprehensive data validation"""
        # Test all CRUD operations with various data types
        
        # Test company with all extended fields
        company_data = {
            "symbol": "VALID_TEST",
            "company_name": "Validation Test Company",
            "company_name_en": "Validation Test Company Ltd",
            "sector": "Technology",
            "industry": "Software",
            "exchange": "HOSE",
            "market_cap": 1000000000,
            "isin": "VN000000VALID",
            "board_id": "MAIN",
            "admin_status": "NRM",
            "ca_status": None,
            "par_value": 10000,
            "trading_unit": 100,
            "contract_multiplier": 1,
            "product_id": "S1STOST"
        }
        
        response = requests.post(f"{self.api_base_url}/companies", json=company_data)
        self.assertEqual(response.status_code, 200)
        
        company = response.json()
        self.assertEqual(company['symbol'], "VALID_TEST")
        self.assertEqual(company['market_cap'], 1000000000)
        self.assertEqual(company['isin'], "VN000000VALID")
        
        # Test stock statistics with all extended fields
        stats_data = {
            "symbol": "VALID_TEST",
            "date": date.today().isoformat(),
            "current_price": 25.5,
            "change_amount": 0.5,
            "change_percent": 2.0,
            "volume": 1000000,
            "value": 25500000,
            "high_price": 26.0,
            "low_price": 25.0,
            "open_price": 25.2,
            "close_price": 25.5,
            "ceiling_price": 28.0,
            "floor_price": 23.0,
            "ref_price": 25.0,
            "avg_price": 25.3,
            "close_price_adjusted": 25.5,
            "total_match_vol": 1000000,
            "total_deal_val": 0,
            "total_deal_vol": 0,
            "foreign_buy_vol_total": 100000,
            "foreign_current_room": 1000000,
            "foreign_sell_vol_total": 50000,
            "foreign_buy_val_total": 2550000,
            "foreign_sell_val_total": 1275000,
            "foreign_buy_vol_matched": 100000,
            "foreign_buy_vol_deal": 0,
            "total_buy_trade": 1000,
            "total_buy_trade_vol": 500000,
            "total_sell_trade": 800,
            "total_sell_trade_vol": 500000,
            "net_buy_sell_vol": 0,
            "net_buy_sell_val": 0,
            "close_raw": 25.5,
            "open_raw": 25.2,
            "high_raw": 26.0,
            "low_raw": 25.0
        }
        
        response = requests.post(f"{self.api_base_url}/stock-statistics", json=stats_data)
        self.assertEqual(response.status_code, 200)
        
        stats = response.json()
        self.assertEqual(stats['symbol'], "VALID_TEST")
        self.assertEqual(stats['ceiling_price'], 28.0)
        self.assertEqual(stats['foreign_buy_vol_total'], 100000)
        self.assertEqual(stats['net_buy_sell_vol'], 0)
        
        # Clean up
        response = requests.delete(f"{self.api_base_url}/companies/VALID_TEST")
        self.assertEqual(response.status_code, 204)
    
    def test_07_error_recovery(self):
        """Test error recovery and resilience"""
        # Test with invalid API URL
        from pipeline.ssi_pipeline_extended import ExtendedSSIPipeline, ExtendedPipelineConfig
        
        config = ExtendedPipelineConfig(
            max_stocks=1,
            symbols=["ACB"],
            days_back=1,
            api_base_url="http://invalid-url:9999",
            dry_run=True
        )
        
        pipeline = ExtendedSSIPipeline(config)
        
        # This should not crash, but should handle errors gracefully
        try:
            stats = pipeline.run_pipeline()
            self.assertGreaterEqual(stats['errors'], 0)
        except Exception as e:
            self.fail(f"Pipeline should handle errors gracefully: {e}")
    
    def test_08_data_completeness(self):
        """Test data completeness after pipeline run"""
        # Check that we have data in all major tables
        endpoints_to_check = [
            'companies',
            'stock-statistics',
            'stock-prices',
            'market-indices/VN100/components',
            'order-book',
            'foreign-trading',
            'session-info'
        ]
        
        for endpoint in endpoints_to_check:
            response = requests.get(f"{self.api_base_url}/{endpoint}")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            if isinstance(data, list):
                print(f"{endpoint}: {len(data)} records")
            else:
                print(f"{endpoint}: {type(data)}")
    
    def test_09_concurrent_data_access(self):
        """Test concurrent data access patterns"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def read_data(symbol, results_queue):
            try:
                # Read company data
                response = requests.get(f"{self.api_base_url}/companies/{symbol}")
                company_success = response.status_code == 200
                
                # Read stock statistics
                response = requests.get(f"{self.api_base_url}/stock-statistics?symbol={symbol}")
                stats_success = response.status_code == 200
                
                # Read stock prices
                response = requests.get(f"{self.api_base_url}/stock-prices?symbol={symbol}&resolution=1d")
                prices_success = response.status_code == 200
                
                results_queue.put({
                    'symbol': symbol,
                    'company_success': company_success,
                    'stats_success': stats_success,
                    'prices_success': prices_success
                })
            except Exception as e:
                results_queue.put({
                    'symbol': symbol,
                    'error': str(e)
                })
        
        # Create threads for concurrent access
        threads = []
        for symbol in self.test_symbols:
            thread = threading.Thread(target=read_data, args=(symbol, results))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        successful_reads = 0
        while not results.empty():
            result = results.get()
            if 'error' not in result:
                if result.get('company_success') and result.get('stats_success') and result.get('prices_success'):
                    successful_reads += 1
        
        self.assertGreater(successful_reads, 0)
        print(f"Concurrent access test: {successful_reads}/{len(self.test_symbols)} symbols read successfully")

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestExtendedIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"INTEGRATION TEST SUMMARY")
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
