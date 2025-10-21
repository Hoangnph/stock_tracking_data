#!/bin/bash
# Monitor VN100 export progress

OUTPUT_DIR="/Users/macintoshhd/Project/Project/stock_playing/tracking_data/output/$(date +%F)"

echo "📊 VN100 Export Progress Monitor"
echo "================================"

while true; do
    if [ -d "$OUTPUT_DIR" ]; then
        COUNT=$(ls "$OUTPUT_DIR"/*.csv 2>/dev/null | wc -l)
        echo "$(date '+%H:%M:%S') - Exported: $COUNT symbols"
        
        if [ $COUNT -gt 0 ]; then
            echo "Latest files:"
            ls -lt "$OUTPUT_DIR"/*.csv | head -3
        fi
        
        echo "---"
    else
        echo "$(date '+%H:%M:%S') - Output directory not found yet"
    fi
    
    sleep 10
done

