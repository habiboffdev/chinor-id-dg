# Production Upload Debugging Guide

## Issue: Image uploads work locally but not in production

---

## Quick Diagnostic Commands (Run on Production Server)

```bash
# SSH into your production server first
ssh chinor-id-dg@your-server-ip

# Navigate to project directory
cd /home/chinor-id-dg/chinor_id_new/opportuni_backend
```

---

## 1. Check Media Directory Configuration Mismatch ⚠️

**Problem:** Your production.py uses `mediafiles/` but Nginx expects `mediafiles/`

```bash
# Check what Django settings say
cd /home/chinor-id-dg/chinor_id_new/opportuni_backend
grep -n "MEDIA_ROOT" opportuni/settings/production.py

# Expected output: MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
```

**Current Configuration:**
- **production.py**: `MEDIA_ROOT = 'mediafiles/'`
- **nginx.conf**: `alias /home/chinor-id-dg/opportuni_backend/mediafiles/`

**Check if directory exists:**
```bash
ls -la /home/chinor-id-dg/chinor_id_new/opportuni_backend/ | grep media
```

**Expected directories:**
- `media/` - local development (base.py)
- `mediafiles/` - production (production.py)

---

## 2. Check Directory Exists and Has Correct Permissions

```bash
# Check if mediafiles directory exists
ls -la /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/

# If it doesn't exist, create it
mkdir -p /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/{avatars,org_logos,resumes,opportunity_covers,application_docs}

# Set correct ownership (should be owned by your web server user)
sudo chown -R chinor-id-dg:chinor-id-dg /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/

# Set correct permissions (Django needs to write here)
chmod -R 755 /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/
```

---

## 3. Check Nginx Configuration

```bash
# Test Nginx config
sudo nginx -t

# Check Nginx is serving media files
curl -I http://localhost/media/

# View Nginx error logs for media issues
sudo tail -f /var/log/nginx/error.log
```

**Verify Nginx media block:**
```nginx
location /media/ {
    alias /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/;
    # ^^ This path must exist and match MEDIA_ROOT
}
```

---

## 4. Check Django is Using Production Settings

```bash
# Check what settings module is active
sudo supervisorctl status opportuni

# Should show environment variable: DJANGO_SETTINGS_MODULE="opportuni.settings.production"

# Or check the supervisor config
cat /etc/supervisor/conf.d/opportuni.conf | grep DJANGO_SETTINGS_MODULE
```

---

## 5. Check Application Logs for Upload Errors

```bash
# Check Django application logs
tail -f /home/chinor-id-dg/chinor_id_new/opportuni_backend/logs/django.log

# Check Gunicorn logs
sudo tail -f /var/log/opportuni/gunicorn.log

# Then try uploading from frontend and watch logs in real-time
```

---

## 6. Test Upload Endpoint Directly

```bash
# Test organization logo upload with curl
curl -X POST http://localhost:8000/api/organizations/upload-logo/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "logo=@/path/to/test-image.jpg" \
  -v

# Test student avatar upload
curl -X POST http://localhost:8000/api/students/upload-profile-picture/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "avatar=@/path/to/test-image.jpg" \
  -v
```

---

## 7. Check File Upload Size Limits

```bash
# Check Nginx max upload size
grep "client_max_body_size" /etc/nginx/sites-enabled/opportuni

# Should be at least 10M (currently configured)
```

---

## 8. Check Django Shell for Media Configuration

```bash
# Activate virtual environment
source /home/chinor-id-dg/chinor_id_new/venv/bin/activate

# Enter Django shell with production settings
cd /home/chinor-id-dg/chinor_id_new/opportuni_backend
DJANGO_SETTINGS_MODULE=opportuni.settings.production python manage.py shell

# In Django shell, run:
from django.conf import settings
print("MEDIA_ROOT:", settings.MEDIA_ROOT)
print("MEDIA_URL:", settings.MEDIA_URL)
print("DEBUG:", settings.DEBUG)

import os
print("MEDIA_ROOT exists:", os.path.exists(settings.MEDIA_ROOT))
print("MEDIA_ROOT writable:", os.access(settings.MEDIA_ROOT, os.W_OK))
```

---

## 🔧 Most Likely Solutions

### Solution 1: Create Missing mediafiles Directory

```bash
cd /home/chinor-id-dg/chinor_id_new/opportuni_backend
mkdir -p mediafiles/{avatars,org_logos,resumes,opportunity_covers,application_docs}
sudo chown -R chinor-id-dg:chinor-id-dg mediafiles/
chmod -R 755 mediafiles/
```

### Solution 2: Fix Nginx Path Mismatch

If Nginx points to wrong directory, update `/etc/nginx/sites-enabled/opportuni`:

```bash
sudo nano /etc/nginx/sites-enabled/opportuni

# Change the media location block to match actual path:
location /media/ {
    alias /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/;
    # Make sure this path exists!
}

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Solution 3: Fix Permissions

```bash
# If Django can't write to directory
sudo chown -R chinor-id-dg:www-data /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/
chmod -R 775 /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/
```

### Solution 4: Restart Services After Changes

```bash
sudo supervisorctl restart opportuni
sudo systemctl reload nginx
```

---

## 🐛 Common Error Patterns

### Error: "Permission denied"
**Cause:** Django/Gunicorn can't write to media directory
**Fix:** Run Solution 3 (fix permissions)

### Error: "No such file or directory"
**Cause:** `mediafiles/` directory doesn't exist
**Fix:** Run Solution 1 (create directory)

### Error: Upload succeeds but 404 on image URL
**Cause:** Nginx not serving files correctly
**Fix:** Run Solution 2 (fix Nginx path)

### Error: "Request Entity Too Large"
**Cause:** File size exceeds Nginx limit
**Fix:** Increase `client_max_body_size` in Nginx config

---

## 📝 Quick Verification Script

Save this as `test_uploads.sh` and run on production:

```bash
#!/bin/bash
echo "=== Upload Configuration Check ==="
echo ""

echo "1. Checking MEDIA_ROOT directory:"
if [ -d "/home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles" ]; then
    echo "✅ mediafiles/ exists"
    ls -la /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/
else
    echo "❌ mediafiles/ DOES NOT EXIST"
fi

echo ""
echo "2. Checking subdirectories:"
for dir in avatars org_logos resumes opportunity_covers application_docs; do
    if [ -d "/home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing"
    fi
done

echo ""
echo "3. Checking permissions:"
ls -ld /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/

echo ""
echo "4. Checking Nginx config:"
sudo nginx -t

echo ""
echo "5. Checking if Nginx serves media:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost/media/ | grep -q "200\|301\|403"; then
    echo "✅ Nginx media endpoint responds"
else
    echo "❌ Nginx media endpoint not responding"
fi

echo ""
echo "6. Checking Django settings:"
cd /home/chinor-id-dg/chinor_id_new/opportuni_backend
source /home/chinor-id-dg/chinor_id_new/venv/bin/activate
python manage.py shell -c "from django.conf import settings; print('MEDIA_ROOT:', settings.MEDIA_ROOT); print('MEDIA_URL:', settings.MEDIA_URL)"

echo ""
echo "=== Check complete ==="
```

---

## 🎯 Next Steps

1. **SSH into production server**
2. **Run the verification script** or commands above
3. **Check the most likely issue:** Missing `mediafiles/` directory
4. **Apply the appropriate solution**
5. **Test upload from your React frontend**
6. **Monitor logs** while testing

---

## 📞 Still Not Working?

If none of these work, provide:
1. Output of the verification script
2. Last 50 lines of `/var/log/opportuni/gunicorn.log`
3. Last 50 lines of `/home/chinor-id-dg/chinor_id_new/opportuni_backend/logs/django.log`
4. Output of `ls -la /home/chinor-id-dg/chinor_id_new/opportuni_backend/`
