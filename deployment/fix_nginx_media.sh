#!/bin/bash

# Fix Nginx Media Files Configuration
# This script updates Nginx to serve media files from the correct directory

echo "🔧 Fixing Nginx media files configuration..."
echo ""

# Backup current Nginx config
echo "1. Creating backup of current Nginx config..."
sudo cp /etc/nginx/sites-available/opportuni /etc/nginx/sites-available/opportuni.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"
echo ""

# Copy new config
echo "2. Updating Nginx configuration..."
sudo cp /home/chinor-id-dg/chinor_id_new/deployment/nginx.conf /etc/nginx/sites-available/opportuni
echo "✅ Configuration updated"
echo ""

# Test Nginx configuration
echo "3. Testing Nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors!"
    echo "Restoring backup..."
    sudo cp /etc/nginx/sites-available/opportuni.backup.* /etc/nginx/sites-available/opportuni
    exit 1
fi
echo ""

# Reload Nginx
echo "4. Reloading Nginx..."
sudo systemctl reload nginx
echo "✅ Nginx reloaded"
echo ""

# Verify media directory exists
echo "5. Verifying media directories..."
if [ -d "/home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles" ]; then
    echo "✅ mediafiles directory exists"
    ls -la /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/
else
    echo "⚠️  Creating mediafiles directory..."
    mkdir -p /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/{avatars,org_logos,resumes,opportunity_covers,application_docs}
    sudo chown -R chinor-id-dg:chinor-id-dg /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/
    chmod -R 755 /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/
    echo "✅ mediafiles directory created"
fi
echo ""

# Test media endpoint
echo "6. Testing media endpoint..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/media/)
if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "301" ] || [ "$RESPONSE" = "403" ]; then
    echo "✅ Media endpoint responds (HTTP $RESPONSE)"
else
    echo "⚠️  Media endpoint returned HTTP $RESPONSE"
fi
echo ""

# Check if any files exist
echo "7. Checking for uploaded files..."
FILE_COUNT=$(find /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/ -type f | wc -l)
echo "📊 Found $FILE_COUNT uploaded file(s)"
if [ "$FILE_COUNT" -gt 0 ]; then
    echo "Sample files:"
    find /home/chinor-id-dg/chinor_id_new/opportuni_backend/mediafiles/ -type f | head -5
fi
echo ""

echo "✅ Nginx media configuration fix complete!"
echo ""
echo "🧪 Test by uploading an image from your frontend"
echo "📸 Uploaded files should now be accessible at: http://your-domain.com/media/avatars/filename.jpg"
echo ""
echo "💡 To monitor uploads in real-time:"
echo "   sudo tail -f /var/log/nginx/access.log | grep media"
