#!/bin/bash
# Daily VN100 Automation Service Script
# This script runs the VN100 automation daily at 17:00

# Configuration
SCRIPT_DIR="/Users/macintoshhd/Project/Project/stock_playing/tracking_data"
AUTOMATION_SCRIPT="$SCRIPT_DIR/automation/automation_vn100_direct.py"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/daily_automation_$(date +%Y%m%d).log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if system is running
check_system() {
    log "Checking system status..."
    
    # Check if Docker containers are running
    if ! docker ps | grep -q "tracking_data"; then
        log "ERROR: Docker containers not running. Starting system..."
        cd "$SCRIPT_DIR"
        ./ssi_system_manager.sh start
        sleep 30
    fi
    
    # Check API health
    if ! curl -s http://localhost:8000/health > /dev/null; then
        log "ERROR: API not responding. Restarting system..."
        cd "$SCRIPT_DIR"
        ./ssi_system_manager.sh restart
        sleep 30
    fi
    
    log "System check completed"
}

# Function to run automation
run_automation() {
    log "Starting daily VN100 automation..."
    
    cd "$SCRIPT_DIR"
    
    # Run automation with production settings
    python3 "$AUTOMATION_SCRIPT" \
        --max-symbols 100 \
        --log-level INFO 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log "Automation completed successfully"
    else
        log "ERROR: Automation failed with exit code $exit_code"
    fi
    
    return $exit_code
}

# Function to send notification (optional)
send_notification() {
    local status=$1
    local message=$2
    
    # You can add notification logic here
    # For example, send email, Slack message, etc.
    log "Notification: $status - $message"
}

# Main execution
main() {
    log "=== Daily VN100 Automation Started ==="
    
    # Check system status
    check_system
    
    # Run automation
    if run_automation; then
        log "=== Daily VN100 Automation Completed Successfully ==="
        send_notification "SUCCESS" "Daily VN100 automation completed successfully"
    else
        log "=== Daily VN100 Automation Failed ==="
        send_notification "ERROR" "Daily VN100 automation failed"
        exit 1
    fi
    
    log "=== Daily VN100 Automation Finished ==="
}

# Run main function
main "$@"
