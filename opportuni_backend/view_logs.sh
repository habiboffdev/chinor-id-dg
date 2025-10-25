#!/bin/bash
# Django & Gunicorn Log Viewer Script
# Usage: ./view_logs.sh [option]

BACKEND_DIR="/home/mirzosharif/MVP/chinor_id_new/opportuni_backend"
LOGS_DIR="${BACKEND_DIR}/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_menu() {
    echo -e "${BLUE}=== Opportuni Logs Viewer ===${NC}"
    echo ""
    echo "Django Application Logs:"
    echo "  1) View Django logs (tail -f)"
    echo "  2) View application logs (tail -f)"
    echo "  3) View error logs only (tail -f)"
    echo "  4) View request logs (tail -f)"
    echo ""
    echo "Gunicorn/Supervisor Logs:"
    echo "  5) View Gunicorn stdout (access logs)"
    echo "  6) View Gunicorn stderr (error logs)"
    echo "  7) View supervisor status"
    echo ""
    echo "Search & Filter:"
    echo "  8) Search for errors in last 500 lines"
    echo "  9) Search for 500 errors"
    echo " 10) Search for custom pattern"
    echo ""
    echo "Log Management:"
    echo " 11) Show log file sizes"
    echo " 12) Clear old logs (keep last 100 lines)"
    echo " 13) View all logs side-by-side"
    echo ""
    echo "  0) Exit"
    echo ""
}

case "$1" in
    1)
        echo -e "${GREEN}Following Django logs...${NC}"
        tail -f "${LOGS_DIR}/django.log"
        ;;
    2)
        echo -e "${GREEN}Following application logs...${NC}"
        tail -f "${LOGS_DIR}/application.log"
        ;;
    3)
        echo -e "${RED}Following error logs...${NC}"
        tail -f "${LOGS_DIR}/error.log"
        ;;
    4)
        echo -e "${GREEN}Following request logs...${NC}"
        tail -f "${LOGS_DIR}/requests.log"
        ;;
    5)
        echo -e "${GREEN}Following Gunicorn stdout...${NC}"
        sudo tail -f /var/log/supervisor/opportuni-stdout.log
        ;;
    6)
        echo -e "${RED}Following Gunicorn stderr...${NC}"
        sudo tail -f /var/log/supervisor/opportuni-stderr.log
        ;;
    7)
        echo -e "${BLUE}Supervisor status:${NC}"
        sudo supervisorctl status
        ;;
    8)
        echo -e "${RED}Searching for errors in last 500 lines...${NC}"
        tail -n 500 "${LOGS_DIR}/django.log" | grep -i "error" --color=always
        tail -n 500 "${LOGS_DIR}/application.log" | grep -i "error" --color=always
        ;;
    9)
        echo -e "${RED}Searching for 500 errors...${NC}"
        grep "500" "${LOGS_DIR}/requests.log" --color=always | tail -n 50
        ;;
    10)
        read -p "Enter search pattern: " pattern
        echo -e "${YELLOW}Searching for '${pattern}'...${NC}"
        grep -i "$pattern" "${LOGS_DIR}"/*.log --color=always | tail -n 100
        ;;
    11)
        echo -e "${BLUE}Log file sizes:${NC}"
        du -sh "${LOGS_DIR}"/*.log 2>/dev/null | sort -h
        ;;
    12)
        echo -e "${YELLOW}Clearing old logs (keeping last 100 lines)...${NC}"
        for logfile in "${LOGS_DIR}"/*.log; do
            if [ -f "$logfile" ]; then
                tail -n 100 "$logfile" > "${logfile}.tmp" && mv "${logfile}.tmp" "$logfile"
                echo "Cleared: $logfile"
            fi
        done
        echo -e "${GREEN}Done!${NC}"
        ;;
    13)
        echo -e "${BLUE}Viewing all logs (press Ctrl+C to exit)...${NC}"
        tail -f "${LOGS_DIR}"/*.log
        ;;
    0|"")
        show_menu
        read -p "Enter option: " choice
        $0 $choice
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        show_menu
        ;;
esac
