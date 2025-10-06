#!/bin/bash
# VN100 Automation Service Manager
# Manages the daily automation service and timer

SERVICE_NAME="vn100-automation"
SERVICE_FILE="/Users/macintoshhd/Project/Project/stock_playing/tracking_data/scripts/vn100-automation.service"
TIMER_FILE="/Users/macintoshhd/Project/Project/stock_playing/tracking_data/scripts/vn100-automation.timer"
SYSTEMD_DIR="$HOME/Library/LaunchAgents"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%H:%M:%S')] $message${NC}"
}

# Function to check if service exists
check_service_exists() {
    if [ -f "$SYSTEMD_DIR/${SERVICE_NAME}.plist" ]; then
        return 0
    else
        return 1
    fi
}

# Function to install service
install_service() {
    print_status $BLUE "Installing VN100 Automation Service..."
    
    # Create LaunchAgent plist file
    cat > "$SYSTEMD_DIR/${SERVICE_NAME}.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vn100.automation</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/macintoshhd/Project/Project/stock_playing/tracking_data/scripts/daily_automation.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>17</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>/Users/macintoshhd/Project/Project/stock_playing/tracking_data</string>
    <key>StandardOutPath</key>
    <string>/Users/macintoshhd/Project/Project/stock_playing/tracking_data/logs/automation_service.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/macintoshhd/Project/Project/stock_playing/tracking_data/logs/automation_service_error.log</string>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF
    
    # Load the service
    launchctl load "$SYSTEMD_DIR/${SERVICE_NAME}.plist"
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "Service installed successfully!"
        print_status $GREEN "Automation will run daily at 17:00"
    else
        print_status $RED "Failed to install service"
        return 1
    fi
}

# Function to uninstall service
uninstall_service() {
    print_status $BLUE "Uninstalling VN100 Automation Service..."
    
    if check_service_exists; then
        # Unload the service
        launchctl unload "$SYSTEMD_DIR/${SERVICE_NAME}.plist"
        
        # Remove the plist file
        rm -f "$SYSTEMD_DIR/${SERVICE_NAME}.plist"
        
        print_status $GREEN "Service uninstalled successfully!"
    else
        print_status $YELLOW "Service not found"
    fi
}

# Function to start service
start_service() {
    print_status $BLUE "Starting VN100 Automation Service..."
    
    if check_service_exists; then
        launchctl start "com.vn100.automation"
        print_status $GREEN "Service started!"
    else
        print_status $RED "Service not installed. Run 'install' first."
        return 1
    fi
}

# Function to stop service
stop_service() {
    print_status $BLUE "Stopping VN100 Automation Service..."
    
    if check_service_exists; then
        launchctl stop "com.vn100.automation"
        print_status $GREEN "Service stopped!"
    else
        print_status $YELLOW "Service not found"
    fi
}

# Function to check service status
check_status() {
    print_status $BLUE "Checking VN100 Automation Service status..."
    
    if check_service_exists; then
        print_status $GREEN "Service is installed"
        
        # Check if service is loaded
        if launchctl list | grep -q "com.vn100.automation"; then
            print_status $GREEN "Service is loaded and active"
        else
            print_status $YELLOW "Service is installed but not loaded"
        fi
        
        # Show next run time (approximate)
        print_status $BLUE "Next scheduled run: Daily at 17:00"
        
    else
        print_status $RED "Service is not installed"
    fi
}

# Function to run automation manually
run_now() {
    print_status $BLUE "Running VN100 Automation manually..."
    
    /Users/macintoshhd/Project/Project/stock_playing/tracking_data/scripts/daily_automation.sh
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "Manual run completed successfully!"
    else
        print_status $RED "Manual run failed!"
    fi
}

# Function to show logs
show_logs() {
    print_status $BLUE "Showing recent automation logs..."
    
    local log_file="/Users/macintoshhd/Project/Project/stock_playing/tracking_data/logs/daily_automation_$(date +%Y%m%d).log"
    
    if [ -f "$log_file" ]; then
        echo "=== Recent Logs ==="
        tail -50 "$log_file"
    else
        print_status $YELLOW "No logs found for today"
    fi
}

# Function to show help
show_help() {
    echo "VN100 Automation Service Manager"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install     Install the daily automation service"
    echo "  uninstall   Uninstall the service"
    echo "  start       Start the service"
    echo "  stop        Stop the service"
    echo "  status      Check service status"
    echo "  run-now     Run automation manually"
    echo "  logs        Show recent logs"
    echo "  help        Show this help message"
    echo ""
    echo "The service will run daily at 17:00 (5:00 PM) to update VN100 data."
}

# Main script logic
case "$1" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    status)
        check_status
        ;;
    run-now)
        run_now
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_status $RED "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
