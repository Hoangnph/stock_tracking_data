#!/bin/bash

# Test Runner for Stock Tracking Data System
# This script runs all tests for the system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if database is running
    if ! docker exec tracking_data pg_isready -U postgres -d tracking_data > /dev/null 2>&1; then
        print_error "Database is not running. Please start the database first."
        print_info "Run: cd ../database && ./scripts/db_manager.sh start"
        return 1
    fi
    
    # Check if API is running
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_error "API is not running. Please start the API first."
        print_info "Run: cd ../api && ./api_manager.sh start"
        return 1
    fi
    
    # Check if Python is available
    if ! command -v python3 > /dev/null; then
        print_error "Python 3 is not installed"
        return 1
    fi
    
    print_status "All prerequisites met"
    return 0
}

# Function to install test dependencies
install_test_deps() {
    print_status "Installing test dependencies..."
    cd "$(dirname "$0")"
    
    # Install required packages
    pip install requests psycopg2-binary > /dev/null 2>&1
    
    print_status "Test dependencies installed"
}

# Function to run specific test suite
run_test_suite() {
    local test_file="$1"
    local test_name="$2"
    
    print_info "Running $test_name..."
    
    if python3 "$test_file"; then
        print_status "$test_name: PASSED"
        return 0
    else
        print_error "$test_name: FAILED"
        return 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    cd "$(dirname "$0")"
    
    # Check prerequisites
    if ! check_prerequisites; then
        return 1
    fi
    
    # Install test dependencies
    install_test_deps
    
    # Test results
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    # Run test suites
    test_suites=(
        "test_suite.py:Complete Test Suite"
        "test_api.py:API Tests"
        "test_integration.py:Integration Tests"
        "test_pipeline_unit.py:Pipeline Unit Tests"
    )
    
    for test_suite in "${test_suites[@]}"; do
        IFS=':' read -r test_file test_name <<< "$test_suite"
        total_tests=$((total_tests + 1))
        
        if run_test_suite "$test_file" "$test_name"; then
            passed_tests=$((passed_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
        
        echo ""
    done
    
    # Print summary
    print_info "Test Summary:"
    print_info "Total test suites: $total_tests"
    print_info "Passed: $passed_tests"
    print_info "Failed: $failed_tests"
    
    if [ $failed_tests -eq 0 ]; then
        print_status "All tests passed! 🎉"
        return 0
    else
        print_error "Some tests failed! ❌"
        return 1
    fi
}

# Function to run specific test
run_specific_test() {
    local test_file="$1"
    
    if [ ! -f "$test_file" ]; then
        print_error "Test file not found: $test_file"
        return 1
    fi
    
    print_status "Running specific test: $test_file"
    cd "$(dirname "$0")"
    
    # Check prerequisites
    if ! check_prerequisites; then
        return 1
    fi
    
    # Install test dependencies
    install_test_deps
    
    # Run the test
    if python3 "$test_file"; then
        print_status "Test passed! ✅"
        return 0
    else
        print_error "Test failed! ❌"
        return 1
    fi
}

# Function to run quick tests
run_quick_tests() {
    print_status "Running quick tests..."
    cd "$(dirname "$0")"
    
    # Check prerequisites
    if ! check_prerequisites; then
        return 1
    fi
    
    # Install test dependencies
    install_test_deps
    
    # Run only API tests (quickest)
    if run_test_suite "test_api.py" "API Tests"; then
        print_status "Quick tests passed! ✅"
        return 0
    else
        print_error "Quick tests failed! ❌"
        return 1
    fi
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    cd "$(dirname "$0")"
    
    local report_file="test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Stock Tracking Data System - Test Report"
        echo "Generated: $(date)"
        echo "========================================"
        echo ""
        
        # System info
        echo "System Information:"
        echo "- OS: $(uname -s)"
        echo "- Python: $(python3 --version)"
        echo "- Database: PostgreSQL + TimescaleDB"
        echo "- API: FastAPI"
        echo ""
        
        # Test results
        echo "Test Results:"
        echo "============="
        
        # Run tests and capture output
        for test_file in test_*.py; do
            if [ -f "$test_file" ]; then
                echo ""
                echo "Running $test_file..."
                echo "-------------------"
                python3 "$test_file" 2>&1 || true
            fi
        done
        
    } > "$report_file"
    
    print_status "Test report generated: $report_file"
}

# Function to clean up test data
cleanup_test_data() {
    print_warning "This will clean up test data from the database. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Cleaning up test data..."
        
        # Connect to database and clean up test data
        docker exec tracking_data psql -U postgres -d tracking_data -c "
            DELETE FROM stock_statistics WHERE symbol LIKE 'TEST%';
            DELETE FROM stock_prices WHERE symbol LIKE 'TEST%';
            DELETE FROM index_components WHERE symbol LIKE 'TEST%';
            DELETE FROM companies WHERE symbol LIKE 'TEST%';
        " > /dev/null 2>&1
        
        print_status "Test data cleaned up"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  all                    Run all tests"
    echo "  quick                  Run quick tests (API only)"
    echo "  api                    Run API tests only"
    echo "  integration            Run integration tests only"
    echo "  unit                   Run unit tests only"
    echo "  suite                  Run complete test suite"
    echo "  specific <file>        Run specific test file"
    echo "  report                 Generate test report"
    echo "  cleanup                Clean up test data"
    echo "  help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 all                 # Run all tests"
    echo "  $0 quick               # Run quick tests"
    echo "  $0 specific test_api.py # Run specific test"
    echo "  $0 report              # Generate test report"
}

# Main script logic
case "$1" in
    all)
        run_all_tests
        ;;
    quick)
        run_quick_tests
        ;;
    api)
        run_specific_test "test_api.py"
        ;;
    integration)
        run_specific_test "test_integration.py"
        ;;
    unit)
        run_specific_test "test_pipeline_unit.py"
        ;;
    suite)
        run_specific_test "test_suite.py"
        ;;
    specific)
        if [ -z "$2" ]; then
            print_error "Please specify test file"
            show_help
            exit 1
        fi
        run_specific_test "$2"
        ;;
    report)
        generate_test_report
        ;;
    cleanup)
        cleanup_test_data
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
