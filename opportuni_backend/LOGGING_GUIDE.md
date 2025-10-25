# Django Production Logging Guide

## Log Files Structure

After the updated configuration, your logs are organized as follows:

```
opportuni_backend/logs/
├── django.log        # General Django framework logs
├── application.log   # Your app-specific logs (DEBUG level)
├── error.log        # All ERROR and CRITICAL logs
└── requests.log     # HTTP request/response logs
```

**Features:**
- **Rotating logs**: Each file max 10MB, keeps 5 backup files
- **Automatic cleanup**: Old logs automatically archived
- **Separate error tracking**: Errors in dedicated file

## Quick Commands

### 1. Real-time Log Viewing

```bash
# Application logs (most useful for debugging)
tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# Error logs only
tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log

# HTTP requests
tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/requests.log

# All logs together
tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/*.log
```

### 2. Gunicorn Logs (via Supervisor)

```bash
# Check service status
sudo supervisorctl status opportuni

# View access logs (stdout)
sudo supervisorctl tail opportuni stdout

# View error logs (stderr)
sudo supervisorctl tail opportuni stderr

# Follow logs in real-time
sudo supervisorctl tail -f opportuni stdout
sudo supervisorctl tail -f opportuni stderr
```

### 3. Search and Filter

```bash
# Find all errors in last hour (approximately last 1000 lines)
tail -n 1000 /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log

# Search for specific error
grep "DoesNotExist" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log

# Find 500 errors
grep "500" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/requests.log | tail -n 20

# Search with context (shows 3 lines before and after)
grep -A 3 -B 3 "ERROR" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log | tail -n 50

# Case-insensitive search
grep -i "timeout" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/*.log
```

### 4. Using the Log Viewer Script

```bash
# Make executable
chmod +x /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/view_logs.sh

# Run interactive menu
cd /home/mirzosharif/MVP/chinor_id_new/opportuni_backend
./view_logs.sh

# Or use directly with options
./view_logs.sh 1   # View Django logs
./view_logs.sh 3   # View error logs
./view_logs.sh 8   # Search for errors
```

## Logging in Your Code

### In Views

```python
import logging

logger = logging.getLogger('apps.students')

class StudentProfileView(APIView):
    def get(self, request):
        logger.info(f"User {request.user.id} accessed student profile")
        
        try:
            profile = StudentProfile.objects.get(user=request.user)
            logger.debug(f"Profile retrieved: {profile.id}")
            return Response(StudentProfileSerializer(profile).data)
        except StudentProfile.DoesNotExist:
            logger.warning(f"No profile found for user {request.user.id}")
            # Auto-create logic
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}", exc_info=True)
            raise
```

### In Models/Utilities

```python
import logging

logger = logging.getLogger('apps.opportunities')

def post_to_telegram(opportunity):
    logger.info(f"Posting opportunity {opportunity.id} to Telegram")
    
    try:
        # Telegram posting logic
        logger.debug(f"Channel ID: {channel_id}")
        result = bot.send_message(...)
        logger.info(f"Posted successfully: message_id={result.message_id}")
    except Exception as e:
        logger.error(f"Failed to post to Telegram: {str(e)}", exc_info=True)
```

### Log Levels

- **DEBUG**: Detailed diagnostic information (only in application.log)
- **INFO**: General informational messages
- **WARNING**: Something unexpected but not critical
- **ERROR**: Serious problem, operation failed
- **CRITICAL**: System-wide failure

## Monitoring Best Practices

### 1. Regular Checks

```bash
# Check error log daily
tail -n 100 /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log

# Monitor disk usage
du -sh /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/
```

### 2. Set Up Log Rotation (Automatic)

The rotating file handler is already configured (10MB per file, 5 backups).

### 3. Create Monitoring Aliases

Add to your `~/.bashrc`:

```bash
# Opportuni log aliases
alias logs-django='tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/django.log'
alias logs-app='tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log'
alias logs-error='tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log'
alias logs-req='tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/requests.log'
alias logs-all='tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/*.log'

# Gunicorn/Supervisor
alias opportuni-status='sudo supervisorctl status opportuni'
alias opportuni-restart='sudo supervisorctl restart opportuni'
alias opportuni-logs='sudo supervisorctl tail -f opportuni'
```

Then reload: `source ~/.bashrc`

## Troubleshooting Common Issues

### Issue: Logs not appearing

```bash
# Check file permissions
ls -la /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/

# Ensure logs directory exists
mkdir -p /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/
chmod 755 /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/

# Restart Gunicorn
sudo supervisorctl restart opportuni
```

### Issue: Log files too large

```bash
# Check sizes
du -sh /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/*.log

# Manual cleanup (keeps last 1000 lines)
cd /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/
for log in *.log; do tail -n 1000 "$log" > "$log.tmp" && mv "$log.tmp" "$log"; done
```

### Issue: Can't find specific error

```bash
# Search all logs with timestamp
grep -h "ERROR" /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/*.log | sort

# Find recent errors (last 30 minutes approximately)
find /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/ -name "*.log" -mmin -30 -exec grep -h "ERROR" {} \;
```

## Advanced: Centralized Logging (Optional)

For production monitoring, consider:

1. **Sentry** - Error tracking and monitoring
2. **Logrotate** - System-level log rotation
3. **ELK Stack** - Elasticsearch, Logstash, Kibana
4. **Papertrail** - Cloud log management

### Quick Sentry Setup

```bash
pip install sentry-sdk
```

In `settings/production.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    environment="production",
    traces_sample_rate=0.1,
)
```

## Summary

**Most useful commands for daily use:**

```bash
# Quick error check
tail -n 50 /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/error.log

# Monitor application in real-time
tail -f /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/application.log

# Check Gunicorn status
sudo supervisorctl status opportuni

# View recent requests
tail -n 100 /home/mirzosharif/MVP/chinor_id_new/opportuni_backend/logs/requests.log
```

Use the interactive script for convenience:
```bash
cd /home/mirzosharif/MVP/chinor_id_new/opportuni_backend
./view_logs.sh
```
