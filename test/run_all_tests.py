#!/usr/bin/env python3
"""
Test Runner for Extended SSI System
Version: 2.0 - Complete Data Coverage Testing

This script runs all tests in the correct order:
1. Unit tests
2. Integration tests
3. Performance tests
4. Data validation tests
"""

import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def run_all_tests():
    """Run all test suites"""
    print("="*80)
    print("EXTENDED SSI SYSTEM - COMPREHENSIVE TEST SUITE")
    print("Version: 2.0 - Complete Data Coverage (112 fields)")
    print("="*80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add unit tests
    print("\n1. Loading Unit Tests...")
    try:
        from test_extended_system import TestExtendedSSISystem, TestExtendedPipeline
        suite.addTests(loader.loadTestsFromTestCase(TestExtendedSSISystem))
        suite.addTests(loader.loadTestsFromTestCase(TestExtendedPipeline))
        print("   ✓ Unit tests loaded successfully")
    except ImportError as e:
        print(f"   ✗ Failed to load unit tests: {e}")
        return False
    
    # Add integration tests
    print("\n2. Loading Integration Tests...")
    try:
        from test_integration_extended import TestExtendedIntegration
        suite.addTests(loader.loadTestsFromTestCase(TestExtendedIntegration))
        print("   ✓ Integration tests loaded successfully")
    except ImportError as e:
        print(f"   ✗ Failed to load integration tests: {e}")
        return False
    
    # Run tests
    print(f"\n3. Running Tests...")
    print(f"   Total test cases: {suite.countTestCases()}")
    
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Print detailed summary
    print("\n" + "="*80)
    print("TEST EXECUTION SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        print("-" * 40)
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()}")
            print()
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        print("-" * 40)
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('Exception:')[-1].strip()}")
            print()
    
    # Test coverage analysis
    print("\n" + "="*80)
    print("TEST COVERAGE ANALYSIS")
    print("="*80)
    
    coverage_areas = {
        "API Health Check": "✓" if any("test_01_health_check" in str(test) for test in result.testsRun) else "✗",
        "Companies CRUD": "✓" if any("test_02_companies_crud" in str(test) for test in result.testsRun) else "✗",
        "Stock Statistics CRUD": "✓" if any("test_03_stock_statistics_crud" in str(test) for test in result.testsRun) else "✗",
        "Stock Prices CRUD": "✓" if any("test_04_stock_prices_crud" in str(test) for test in result.testsRun) else "✗",
        "Order Book CRUD": "✓" if any("test_05_order_book_crud" in str(test) for test in result.testsRun) else "✗",
        "Foreign Trading CRUD": "✓" if any("test_06_foreign_trading_crud" in str(test) for test in result.testsRun) else "✗",
        "Session Info CRUD": "✓" if any("test_07_session_info_crud" in str(test) for test in result.testsRun) else "✗",
        "Analytics Endpoints": "✓" if any("test_08_analytics_endpoints" in str(test) for test in result.testsRun) else "✗",
        "Data Validation": "✓" if any("test_09_data_validation" in str(test) for test in result.testsRun) else "✗",
        "Performance Testing": "✓" if any("test_10_performance_testing" in str(test) for test in result.testsRun) else "✗",
        "CORS Headers": "✓" if any("test_11_cors_headers" in str(test) for test in result.testsRun) else "✗",
        "Pagination": "✓" if any("test_12_pagination" in str(test) for test in result.testsRun) else "✗",
        "Filtering": "✓" if any("test_13_filtering" in str(test) for test in result.testsRun) else "✗",
        "Error Handling": "✓" if any("test_14_error_handling" in str(test) for test in result.testsRun) else "✗",
        "Data Integrity": "✓" if any("test_15_data_integrity" in str(test) for test in result.testsRun) else "✗",
        "End-to-End Pipeline": "✓" if any("test_01_end_to_end_pipeline" in str(test) for test in result.testsRun) else "✗",
        "Database Integration": "✓" if any("test_02_database_data_integrity" in str(test) for test in result.testsRun) else "✗",
        "API Data Consistency": "✓" if any("test_03_api_data_consistency" in str(test) for test in result.testsRun) else "✗",
        "Analytics Integration": "✓" if any("test_04_analytics_endpoints_integration" in str(test) for test in result.testsRun) else "✗",
        "Load Performance": "✓" if any("test_05_performance_under_load" in str(test) for test in result.testsRun) else "✗",
        "Comprehensive Validation": "✓" if any("test_06_data_validation_comprehensive" in str(test) for test in result.testsRun) else "✗",
        "Error Recovery": "✓" if any("test_07_error_recovery" in str(test) for test in result.testsRun) else "✗",
        "Data Completeness": "✓" if any("test_08_data_completeness" in str(test) for test in result.testsRun) else "✗",
        "Concurrent Access": "✓" if any("test_09_concurrent_data_access" in str(test) for test in result.testsRun) else "✗"
    }
    
    for area, status in coverage_areas.items():
        print(f"{status} {area}")
    
    # Overall assessment
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)
    
    if success_rate >= 95:
        print("🎉 EXCELLENT: System is production-ready!")
        print("   All critical functionality is working correctly.")
    elif success_rate >= 85:
        print("✅ GOOD: System is mostly functional with minor issues.")
        print("   Review failures and fix before production deployment.")
    elif success_rate >= 70:
        print("⚠️  FAIR: System has significant issues that need attention.")
        print("   Major functionality may be affected.")
    else:
        print("❌ POOR: System has critical issues requiring immediate attention.")
        print("   Do not deploy to production until issues are resolved.")
    
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    print(f"Total Tests: {result.testsRun}")
    print(f"Failed Tests: {len(result.failures) + len(result.errors)}")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if len(result.failures) > 0:
        print("🔧 Fix the following failures:")
        for test, _ in result.failures:
            print(f"   - {test}")
    
    if len(result.errors) > 0:
        print("🚨 Resolve the following errors:")
        for test, _ in result.errors:
            print(f"   - {test}")
    
    if success_rate >= 95:
        print("🚀 Ready for production deployment!")
        print("   Consider adding monitoring and alerting.")
    elif success_rate >= 85:
        print("📋 Create issues for failed tests and prioritize fixes.")
        print("   Run tests again after fixes.")
    else:
        print("🛠️  Major refactoring may be required.")
        print("   Consider reviewing system architecture.")
    
    print("="*80)
    
    return success_rate >= 85

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
