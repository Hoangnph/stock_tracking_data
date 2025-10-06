#!/bin/bash

# Database management script for tracking_data
# This script provides commands to manage the database

set -e

# Database connection parameters
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="tracking_data"
DB_USER="postgres"
DB_PASSWORD="postgres123"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Function to check if database is running
check_db() {
    print_status "Checking database connection..."
    if docker exec tracking_data pg_isready -U postgres -d tracking_data > /dev/null 2>&1; then
        print_status "Database is running and ready"
        return 0
    else
        print_error "Database is not running or not ready"
        return 1
    fi
}

# Function to start database
start_db() {
    print_status "Starting tracking_data database..."
    cd "$(dirname "$0")/.."
    docker-compose up -d
    sleep 5
    check_db
}

# Function to stop database
stop_db() {
    print_status "Stopping tracking_data database..."
    cd "$(dirname "$0")/.."
    docker-compose down
}

# Function to restart database
restart_db() {
    print_status "Restarting tracking_data database..."
    stop_db
    sleep 2
    start_db
}

# Function to show database status
status_db() {
    print_status "Database status:"
    cd "$(dirname "$0")/.."
    docker-compose ps
}

# Function to show database logs
logs_db() {
    print_status "Showing database logs..."
    cd "$(dirname "$0")/.."
    docker-compose logs -f tracking_data_db
}

# Function to connect to database
connect_db() {
    print_status "Connecting to database..."
    docker exec -it tracking_data psql -U postgres -d tracking_data
}

# Function to backup database
backup_db() {
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    print_status "Creating database backup: $backup_file"
    docker exec tracking_data pg_dump -U postgres -d tracking_data > "../backups/$backup_file"
    print_status "Backup created: ../backups/$backup_file"
}

# Function to restore database
restore_db() {
    local backup_file="$1"
    if [ -z "$backup_file" ]; then
        print_error "Please provide backup file path"
        return 1
    fi
    
    print_warning "This will replace all data in the database. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Restoring database from: $backup_file"
        docker exec -i tracking_data psql -U postgres -d tracking_data < "$backup_file"
        print_status "Database restored successfully"
    else
        print_status "Restore cancelled"
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the database"
    echo "  stop      Stop the database"
    echo "  restart   Restart the database"
    echo "  status    Show database status"
    echo "  logs      Show database logs"
    echo "  connect   Connect to database"
    echo "  backup    Create database backup"
    echo "  restore   Restore database from backup"
    echo "  check     Check database connection"
    echo "  help      Show this help message"
}

# Main script logic
case "$1" in
    start)
        start_db
        ;;
    stop)
        stop_db
        ;;
    restart)
        restart_db
        ;;
    status)
        status_db
        ;;
    logs)
        logs_db
        ;;
    connect)
        connect_db
        ;;
    backup)
        backup_db
        ;;
    restore)
        restore_db "$2"
        ;;
    check)
        check_db
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
