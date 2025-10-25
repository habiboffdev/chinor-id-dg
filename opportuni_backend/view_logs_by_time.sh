#!/bin/bash
# Time-Based Log Viewer for Django/Gunicorn
# Usage: ./view_logs_by_time.sh [options]

LOGS_DIR="/home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}Time-Based Log Viewer${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d DATE           View logs for specific date (YYYY-MM-DD)"
    echo "  -t TIME           View logs for specific time (HH:MM)"
    echo "  -dt DATETIME      View logs for date and time (YYYY-MM-DD HH:MM)"
    echo "  -r START END      View logs in time range"
    echo "  -h HOURS          View logs from last N hours"
    echo "  -m MINUTES        View logs from last N minutes"
    echo "  -f FILE           Specific log file to search (default: all)"
    echo "  -e                Show only errors"
    echo "  --help            Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 -d 2025-10-25                    # All logs from Oct 25"
    echo "  $0 -dt \"2025-10-25 14:30\"           # Logs at 14:30"
    echo "  $0 -r \"2025-10-25 14:00\" \"2025-10-25 15:00\"  # Range"
    echo "  $0 -h 2                             # Last 2 hours"
    echo "  $0 -m 30                            # Last 30 minutes"
    echo "  $0 -d 2025-10-25 -e                 # Only errors from Oct 25"
    echo "  $0 -f application.log -h 1          # Last hour in application.log"
}

search_by_pattern() {
    local pattern="$1"
    local file_filter="$2"
    local errors_only="$3"
    
    if [ -z "$file_filter" ]; then
        files="${LOGS_DIR}/*.log"
    else
        files="${LOGS_DIR}/${file_filter}"
    fi
    
    echo -e "${CYAN}Searching for pattern: ${pattern}${NC}"
    echo ""
    
    for logfile in $files; do
        if [ -f "$logfile" ]; then
            if [ "$errors_only" = "true" ]; then
                results=$(grep "$pattern" "$logfile" | grep -i "ERROR\|CRITICAL" --color=always)
            else
                results=$(grep "$pattern" "$logfile" --color=always)
            fi
            
            if [ -n "$results" ]; then
                echo -e "${GREEN}=== $(basename $logfile) ===${NC}"
                echo "$results"
                echo ""
            fi
        fi
    done
}

search_by_range() {
    local start="$1"
    local end="$2"
    local file_filter="$3"
    local errors_only="$4"
    
    if [ -z "$file_filter" ]; then
        files="${LOGS_DIR}/*.log"
    else
        files="${LOGS_DIR}/${file_filter}"
    fi
    
    echo -e "${CYAN}Searching from ${start} to ${end}${NC}"
    echo ""
    
    for logfile in $files; do
        if [ -f "$logfile" ]; then
            if [ "$errors_only" = "true" ]; then
                results=$(awk -v start="$start" -v end="$end" '$0 >= start && $0 <= end' "$logfile" | grep -i "ERROR\|CRITICAL" --color=always)
            else
                results=$(awk -v start="$start" -v end="$end" '$0 >= start && $0 <= end' "$logfile")
            fi
            
            if [ -n "$results" ]; then
                echo -e "${GREEN}=== $(basename $logfile) ===${NC}"
                echo "$results"
                echo ""
            fi
        fi
    done
}

get_relative_time() {
    local hours="$1"
    local minutes="$2"
    
    if [ -n "$hours" ]; then
        # Calculate time N hours ago
        date -d "$hours hours ago" "+%Y-%m-%d %H:%M"
    elif [ -n "$minutes" ]; then
        # Calculate time N minutes ago
        date -d "$minutes minutes ago" "+%Y-%m-%d %H:%M"
    fi
}

# Parse arguments
FILE_FILTER=""
ERRORS_ONLY="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -d)
            DATE="$2"
            search_by_pattern "$DATE" "$FILE_FILTER" "$ERRORS_ONLY"
            exit 0
            ;;
        -t)
            TIME="$2"
            search_by_pattern "$TIME" "$FILE_FILTER" "$ERRORS_ONLY"
            exit 0
            ;;
        -dt)
            DATETIME="$2"
            search_by_pattern "$DATETIME" "$FILE_FILTER" "$ERRORS_ONLY"
            exit 0
            ;;
        -r)
            START="$2"
            END="$3"
            search_by_range "$START" "$END" "$FILE_FILTER" "$ERRORS_ONLY"
            exit 0
            ;;
        -h)
            HOURS="$2"
            NOW=$(date "+%Y-%m-%d %H:%M")
            START=$(get_relative_time "$HOURS" "")
            search_by_range "$START" "$NOW" "$FILE_FILTER" "$ERRORS_ONLY"
            exit 0
            ;;
        -m)
            MINUTES="$2"
            NOW=$(date "+%Y-%m-%d %H:%M")
            START=$(get_relative_time "" "$MINUTES")
            search_by_range "$START" "$NOW" "$FILE_FILTER" "$ERRORS_ONLY"
            exit 0
            ;;
        -f)
            FILE_FILTER="$2"
            shift 2
            ;;
        -e)
            ERRORS_ONLY="true"
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# If no arguments, show help
show_help
