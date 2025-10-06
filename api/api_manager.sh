#!/bin/bash

# API management script for tracking_data
# This script provides commands to manage the FastAPI application

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

# Function to check if API is running
check_api() {
    print_status "Checking API status..."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "API is running and healthy"
        return 0
    else
        print_error "API is not running or not healthy"
        return 1
    fi
}

# Function to install dependencies
install_deps() {
    print_status "Installing API dependencies..."
    cd "$(dirname "$0")"
    pip install -r requirements.txt
    print_status "Dependencies installed successfully"
}

# Function to start API
start_api() {
    print_status "Starting tracking_data API..."
    cd "$(dirname "$0")"
    
    # Check if database is running
    if ! docker exec tracking_data pg_isready -U postgres -d tracking_data > /dev/null 2>&1; then
        print_error "Database is not running. Please start the database first."
        print_info "Run: cd ../database && ./scripts/db_manager.sh start"
        return 1
    fi
    
    # Start API
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    API_PID=$!
    echo $API_PID > api.pid
    
    sleep 3
    check_api
}

# Function to stop API
stop_api() {
    print_status "Stopping tracking_data API..."
    cd "$(dirname "$0")"
    
    if [ -f api.pid ]; then
        PID=$(cat api.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            print_status "API stopped successfully"
        else
            print_warning "API process not found"
        fi
        rm -f api.pid
    else
        print_warning "No API process file found"
    fi
}

# Function to restart API
restart_api() {
    print_status "Restarting tracking_data API..."
    stop_api
    sleep 2
    start_api
}

# Function to show API logs
logs_api() {
    print_status "Showing API logs..."
    cd "$(dirname "$0")"
    
    if [ -f api.pid ]; then
        PID=$(cat api.pid)
        if kill -0 $PID 2>/dev/null; then
            print_info "API is running with PID: $PID"
            print_info "API documentation available at: http://localhost:8000/docs"
            print_info "API health check: http://localhost:8000/health"
        else
            print_error "API is not running"
        fi
    else
        print_error "No API process file found"
    fi
}

# Function to test API endpoints
test_api() {
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    print_info "Testing health endpoint..."
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_status "Health endpoint: OK"
    else
        print_error "Health endpoint: FAILED"
        return 1
    fi
    
    # Test companies endpoint
    print_info "Testing companies endpoint..."
    if curl -s http://localhost:8000/companies | grep -q "symbol"; then
        print_status "Companies endpoint: OK"
    else
        print_error "Companies endpoint: FAILED"
        return 1
    fi
    
    # Test market indices endpoint
    print_info "Testing market indices endpoint..."
    if curl -s http://localhost:8000/market-indices | grep -q "index_name"; then
        print_status "Market indices endpoint: OK"
    else
        print_error "Market indices endpoint: FAILED"
        return 1
    fi
    
    print_status "All API endpoints tested successfully!"
}

# Function to show API documentation
docs_api() {
    print_status "Opening API documentation..."
    print_info "API documentation is available at:"
    print_info "  - Swagger UI: http://localhost:8000/docs"
    print_info "  - ReDoc: http://localhost:8000/redoc"
    print_info "  - OpenAPI JSON: http://localhost:8000/openapi.json"
    
    # Try to open in browser (macOS)
    if command -v open > /dev/null; then
        open http://localhost:8000/docs
    else
        print_info "Please open the URLs above in your browser"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install    Install API dependencies"
    echo "  start      Start the API server"
    echo "  stop       Stop the API server"
    echo "  restart    Restart the API server"
    echo "  status     Show API status"
    echo "  logs       Show API logs and info"
    echo "  test       Test API endpoints"
    echo "  docs       Show API documentation"
    echo "  help       Show this help message"
}

# Main script logic
case "$1" in
    install)
        install_deps
        ;;
    start)
        start_api
        ;;
    stop)
        stop_api
        ;;
    restart)
        restart_api
        ;;
    status)
        check_api
        ;;
    logs)
        logs_api
        ;;
    test)
        test_api
        ;;
    docs)
        docs_api
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
