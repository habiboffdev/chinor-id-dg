# Time-Based Log Searching - Quick Reference

## Quick Commands for Viewing Logs at Specific Times

### Using the Time Viewer Script (Recommended)

```bash
# Make executable first
chmod +x /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/view_logs_by_time.sh

# View logs from today
./view_logs_by_time.sh -d $(date +%Y-%m-%d)

# View logs from specific date
./view_logs_by_time.sh -d 2025-10-25

# View logs at specific time
./view_logs_by_time.sh -dt "2025-10-25 14:30"

# View logs in time range
./view_logs_by_time.sh -r "2025-10-25 14:00" "2025-10-25 15:00"

# View logs from last 2 hours
./view_logs_by_time.sh -h 2

# View logs from last 30 minutes
./view_logs_by_time.sh -m 30

# Only errors from last hour
./view_logs_by_time.sh -h 1 -e

# Specific log file, last 30 minutes
./view_logs_by_time.sh -m 30 -f application.log
```

### Manual grep Commands

```bash
# Exact date
grep "2025-10-25" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# Specific hour (14:00-14:59)
grep "2025-10-25 14:" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# Specific minute
grep "2025-10-25 14:30:" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# Specific time window (14:30-14:39)
grep "2025-10-25 14:3[0-9]:" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# Multiple specific hours
grep -E "2025-10-25 (14|15|16):" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log
```

### Using awk for Time Ranges

```bash
# Logs between two exact timestamps
awk '/2025-10-25 14:30/,/2025-10-25 15:30/' /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# More precise time range (works with any timestamp format)
awk '$0 >= "2025-10-25 14:30:00" && $0 <= "2025-10-25 15:30:00"' /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# Time range with line numbers
awk '/2025-10-25 14:30/,/2025-10-25 15:30/ {print NR": "$0}' /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log
```

### Using sed for Time Ranges

```bash
# Extract logs between timestamps
sed -n '/2025-10-25 14:30/,/2025-10-25 15:30/p' /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# With line numbers
sed -n '/2025-10-25 14:30/,/2025-10-25 15:30/=' /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log
```

## Real-World Examples

### 1. Debug a Specific Request

```bash
# Find when error occurred
grep "500 Internal Server Error" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/requests.log

# Output might show: [ERROR] 2025-10-25 14:32:15 ...
# Then get context around that time (5 minutes before and after)
./view_logs_by_time.sh -r "2025-10-25 14:27" "2025-10-25 14:37"
```

### 2. Monitor Deployment Impact

```bash
# Before deployment (last hour)
./view_logs_by_time.sh -h 1 > before_deploy.log

# After deployment
./view_logs_by_time.sh -m 10 -e  # Check for errors in last 10 minutes
```

### 3. Find Errors During Specific Time

```bash
# Errors between 2pm and 3pm
awk '/2025-10-25 14:/,/2025-10-25 15:/ {print}' \
  /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log

# Or with the script
./view_logs_by_time.sh -r "2025-10-25 14:00" "2025-10-25 15:00" -f error.log
```

### 4. Track User Activity

```bash
# Find when user logged in today
grep "$(date +%Y-%m-%d)" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log | grep "User.*login"

# Specific user's activity in last hour
./view_logs_by_time.sh -h 1 | grep "user_id=123"
```

### 5. Compare Different Time Periods

```bash
# Morning logs
./view_logs_by_time.sh -r "2025-10-25 09:00" "2025-10-25 12:00" > morning.log

# Afternoon logs
./view_logs_by_time.sh -r "2025-10-25 13:00" "2025-10-25 16:00" > afternoon.log

# Compare
diff morning.log afternoon.log
```

## Advanced Techniques

### 1. Count Events by Hour

```bash
# Count errors by hour
grep "2025-10-25" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log | \
  cut -d' ' -f1-2 | cut -d':' -f1 | sort | uniq -c
```

### 2. Extract Last N Hours

```bash
# Last 3 hours of logs
HOURS_AGO=$(date -d '3 hours ago' '+%Y-%m-%d %H:00')
NOW=$(date '+%Y-%m-%d %H:%M')
awk -v start="$HOURS_AGO" -v end="$NOW" '$0 >= start && $0 <= end' \
  /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log
```

### 3. Today's Logs Only

```bash
# All today's logs
grep "$(date +%Y-%m-%d)" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# Today's errors only
grep "$(date +%Y-%m-%d)" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log
```

### 4. Real-time Following from Specific Time

```bash
# Follow logs starting from 2pm today
sed -n "/$(date +%Y-%m-%d) 14:00/,\$p" \
  /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log | \
  tail -f
```

### 5. Multi-file Time Search

```bash
# Search all logs for specific timestamp
for log in /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/*.log; do
    echo "=== $log ==="
    grep "2025-10-25 14:30" "$log"
done
```

## Using Interactive Menu

```bash
# Run the interactive viewer
cd /home/mirzosharif/MVP/chinor_id_new/opportuni_backend
./view_logs.sh

# Then select option 11 for specific time
# Or option 12 for time range
```

## Pro Tips

### Create Aliases

Add to `~/.bashrc`:

```bash
alias logs-today='grep "$(date +%Y-%m-%d)" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log'
alias logs-hour='grep "$(date +"%Y-%m-%d %H:")" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log'
alias logs-time='/home/mirzosharif/MVP/chinor_id_new/opportuni_backend/view_logs_by_time.sh'
```

### Function for Custom Time Search

Add to `~/.bashrc`:

```bash
logs-at() {
    # Usage: logs-at "2025-10-25 14:30"
    local timestamp="$1"
    grep "$timestamp" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/*.log
}

logs-between() {
    # Usage: logs-between "14:00" "15:00"
    local start="$(date +%Y-%m-%d) $1"
    local end="$(date +%Y-%m-%d) $2"
    /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/view_logs_by_time.sh -r "$start" "$end"
}
```

## Timestamp Format Reference

Your Django logs use this format:
```
[LEVEL] YYYY-MM-DD HH:MM:SS module.function:line - message
```

Examples:
```
[INFO] 2025-10-25 14:30:45 students.views.get:23 - User 123 accessed profile
[ERROR] 2025-10-25 14:31:12 opportunities.signals.post_to_telegram:45 - Failed to post
```

Match patterns:
- Full timestamp: `2025-10-25 14:30:45`
- Date only: `2025-10-25`
- Hour: `2025-10-25 14:`
- Minute: `2025-10-25 14:30:`
- Second: `2025-10-25 14:30:45`

## Summary

**Best tool for each scenario:**

| Scenario | Recommended Tool |
|----------|------------------|
| Exact time | `grep "2025-10-25 14:30"` |
| Time range | `./view_logs_by_time.sh -r START END` |
| Last N hours | `./view_logs_by_time.sh -h N` |
| Last N minutes | `./view_logs_by_time.sh -m N` |
| Interactive | `./view_logs.sh` (option 11/12) |
| Complex queries | `awk` or custom script |
