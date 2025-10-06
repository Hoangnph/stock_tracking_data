#!/bin/bash

# SSI Tracking Data System Manager
# Manages both Main API (port 8000) and SSI Proxy API (port 8001)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for database
    print_status "Waiting for database..."
    timeout 60 bash -c 'until docker exec tracking_data_db pg_isready -U postgres -d tracking_data > /dev/null 2>&1; do sleep 2; done'
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout 60 bash -c 'until docker exec tracking_data_redis redis-cli ping > /dev/null 2>&1; do sleep 2; done'
    
    # Wait for Main API
    print_status "Waiting for Main API..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health > /dev/null 2>&1; do sleep 2; done'
    
    # Wait for SSI Proxy API
    print_status "Waiting for SSI Proxy API..."
    timeout 60 bash -c 'until curl -f http://localhost:8001/health > /dev/null 2>&1; do sleep 2; done'
    
    print_success "All services are healthy!"
}

# Function to start all services
start_all() {
    print_status "Starting SSI Tracking Data System..."
    check_docker
    check_docker_compose
    
    docker compose up --build -d
    
    print_status "Waiting for services to be healthy..."
    wait_for_services
    
    print_success "SSI Tracking Data System started successfully!"
    print_status "Services available at:"
    print_status "  📊 Main API (Database): http://localhost:8000"
    print_status "  📊 Main API Docs: http://localhost:8000/docs"
    print_status "  🔗 SSI Proxy API: http://localhost:8001"
    print_status "  🔗 SSI Proxy Docs: http://localhost:8001/docs"
    print_status "  🗄️ Database: localhost:5434"
    print_status "  🚀 Redis: localhost:6379"
}

# Function to start only main API
start_main() {
    print_status "Starting Main API only..."
    check_docker
    check_docker_compose
    
    docker compose up --build -d tracking_data_db tracking_data_redis tracking_data_api
    
    print_status "Waiting for services to be healthy..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health > /dev/null 2>&1; do sleep 2; done'
    
    print_success "Main API started successfully!"
    print_status "Main API available at: http://localhost:8000"
    print_status "Main API Docs: http://localhost:8000/docs"
}

# Function to start only SSI proxy
start_proxy() {
    print_status "Starting SSI Proxy API only..."
    check_docker
    check_docker_compose
    
    docker compose up --build -d tracking_data_db tracking_data_redis tracking_data_ssi_proxy
    
    print_status "Waiting for services to be healthy..."
    timeout 60 bash -c 'until curl -f http://localhost:8001/health > /dev/null 2>&1; do sleep 2; done'
    
    print_success "SSI Proxy API started successfully!"
    print_status "SSI Proxy API available at: http://localhost:8001"
    print_status "SSI Proxy Docs: http://localhost:8001/docs"
}

# Function to stop all services
stop_all() {
    print_status "Stopping SSI Tracking Data System..."
    docker compose down
    print_success "All services stopped!"
}

# Function to restart all services
restart_all() {
    print_status "Restarting SSI Tracking Data System..."
    stop_all
    sleep 2
    start_all
}

# Function to check status
status_all() {
    print_status "Checking SSI Tracking Data System status..."
    
    echo ""
    print_status "=== Docker Services Status ==="
    docker compose ps
    
    echo ""
    print_status "=== Service Health Checks ==="
    
    # Check database
    if docker exec tracking_data_db pg_isready -U postgres -d tracking_data > /dev/null 2>&1; then
        print_success "Database: ✅ Healthy"
    else
        print_error "Database: ❌ Unhealthy"
    fi
    
    # Check Redis
    if docker exec tracking_data_redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis: ✅ Healthy"
    else
        print_error "Redis: ❌ Unhealthy"
    fi
    
    # Check Main API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Main API: ✅ Healthy"
    else
        print_error "Main API: ❌ Unhealthy"
    fi
    
    # Check SSI Proxy API
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        print_success "SSI Proxy API: ✅ Healthy"
    else
        print_error "SSI Proxy API: ❌ Unhealthy"
    fi
    
    echo ""
    print_status "=== API Endpoints ==="
    print_status "Main API (Database): http://localhost:8000"
    print_status "SSI Proxy API: http://localhost:8001"
}

# Function to show logs
logs_all() {
    print_status "Showing logs for all services..."
    docker compose logs -f
}

logs_main() {
    print_status "Showing logs for Main API..."
    docker compose logs -f tracking_data_api
}

logs_proxy() {
    print_status "Showing logs for SSI Proxy API..."
    docker compose logs -f tracking_data_ssi_proxy
}

logs_db() {
    print_status "Showing logs for Database..."
    docker compose logs -f tracking_data_db
}

# Function to test SSI proxy endpoints
test_proxy() {
    print_status "Testing SSI Proxy API endpoints..."
    
    echo ""
    print_status "=== Testing SSI Proxy Health ==="
    curl -s http://localhost:8001/health | jq .
    
    echo ""
    print_status "=== Testing SSI Proxy Config ==="
    curl -s http://localhost:8001/ssi-proxy/config | jq .
    
    echo ""
    print_status "=== Testing VN100 Group API ==="
    curl -s http://localhost:8001/ssi-proxy/vn100-group | jq '.success, .api_endpoint, .total_components, .response_time_ms'
    
    echo ""
    print_status "=== Testing Stock Info API ==="
    curl -s "http://localhost:8001/ssi-proxy/stock-info?symbol=ACB&from_date=01/10/2025&to_date=05/10/2025" | jq '.success, .api_endpoint, .symbol, .response_time_ms'
    
    echo ""
    print_status "=== Testing Charts History API ==="
    FROM_TS=$(date -d "1 day ago" +%s)
    TO_TS=$(date +%s)
    curl -s "http://localhost:8001/ssi-proxy/charts-history?symbol=ACB&resolution=1d&from_timestamp=$FROM_TS&to_timestamp=$TO_TS" | jq '.success, .api_endpoint, .symbol, .data.data_points, .response_time_ms'
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up SSI Tracking Data System..."
    docker compose down -v
    docker system prune -f
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    echo "SSI Tracking Data System Manager"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services (Main API + SSI Proxy)"
    echo "  start-main  Start only Main API (with database)"
    echo "  start-proxy Start only SSI Proxy API"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Check status of all services"
    echo "  logs        Show logs for all services"
    echo "  logs-main   Show logs for Main API only"
    echo "  logs-proxy  Show logs for SSI Proxy API only"
    echo "  logs-db     Show logs for Database only"
    echo "  test-proxy  Test SSI Proxy API endpoints"
    echo "  cleanup     Stop and cleanup all containers and volumes"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start all services"
    echo "  $0 start-proxy   # Start only SSI proxy for testing"
    echo "  $0 test-proxy    # Test SSI proxy endpoints"
    echo "  $0 status        # Check service status"
}

# Main script logic
case "${1:-help}" in
    start)
        start_all
        ;;
    start-main)
        start_main
        ;;
    start-proxy)
        start_proxy
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        status_all
        ;;
    logs)
        logs_all
        ;;
    logs-main)
        logs_main
        ;;
    logs-proxy)
        logs_proxy
        ;;
    logs-db)
        logs_db
        ;;
    test-proxy)
        test_proxy
        ;;
    cleanup)
        cleanup
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
