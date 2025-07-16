# 🚀 Opportuni MVP - Production Deployment Guide

## 📋 Quick Deployment Checklist

### Prerequisites
- ✅ DigitalOcean Droplet (Ubuntu 22.04, 2GB RAM minimum)
- ✅ Domain name (optional but recommended)
- ✅ Git repository with your code

## 🔧 Deployment Steps

### 1. Initial Server Setup (Run as root)
```bash
# Upload server_setup.sh to your droplet and run:
sudo bash server_setup.sh
```
**Important**: Save the database password that gets generated!

### 2. Clone Your Repository
```bash
# Switch to opportuni user
su - opportuni

# Clone your repository
git clone https://github.com/yourusername/opportuni.git
cd opportuni
```

### 3. Configure Environment
```bash
# Copy environment template
cp opportuni_backend/.env.example opportuni_backend/.env

# Edit with your settings
nano opportuni_backend/.env
```

**Required .env values:**
- `SECRET_KEY` - Generate a new one: `python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DB_PASSWORD` - Use the password from server setup
- `DOMAIN_NAME` - Your domain (if you have one)
- `DROPLET_IP` - Your droplet's IP address

### 4. Deploy Application
```bash
# Run deployment script
bash deployment/deploy.sh
```

### 5. Configure Nginx (Run as root)
```bash
# Copy nginx configuration
sudo cp /home/opportuni/opportuni/deployment/nginx.conf /etc/nginx/sites-available/opportuni

# Update the configuration with your domain/IP
sudo nano /etc/nginx/sites-available/opportuni

# Enable the site
sudo ln -s /etc/nginx/sites-available/opportuni /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 6. Configure Supervisor (Run as root)
```bash
# Copy supervisor configuration
sudo cp /home/opportuni/opportuni/deployment/supervisor.conf /etc/supervisor/conf.d/opportuni.conf

# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start opportuni
```

### 7. Setup SSL (Optional but recommended)
```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Update environment for HTTPS
echo "USE_HTTPS=True" >> /home/opportuni/opportuni/opportuni_backend/.env

# Restart application
sudo supervisorctl restart opportuni
```

## 🧪 Testing Your Deployment

### Check Services
```bash
# Check if Django is running
sudo supervisorctl status opportuni

# Check nginx
sudo systemctl status nginx

# Check logs
sudo tail -f /var/log/opportuni/gunicorn.log
```

### Test Endpoints
```bash
# Test API
curl http://yourdomain.com/api/accounts/

# Test frontend
curl http://yourdomain.com/
```

## 🔄 Updating Your Application

### Deploy Updates
```bash
# Switch to opportuni user
su - opportuni
cd opportuni

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies (if changed)
pip install -r deployment/requirements-production.txt

# Run migrations (if any)
cd opportuni_backend
python manage.py migrate --settings=opportuni.settings.production

# Collect static files
python manage.py collectstatic --noinput --settings=opportuni.settings.production

# Restart application
sudo supervisorctl restart opportuni
```

## 📊 Monitoring and Maintenance

### Log Files
- Django: `/var/log/opportuni/gunicorn.log`
- Nginx: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### Regular Maintenance
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep python

# Database backup
pg_dump -U opportuni_user opportuni_db > backup_$(date +%Y%m%d).sql
```

## 🚨 Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if Django is running: `sudo supervisorctl status opportuni`
   - Check Django logs: `sudo tail -f /var/log/opportuni/gunicorn.log`

2. **Static files not loading**
   - Run: `python manage.py collectstatic --settings=opportuni.settings.production`
   - Check nginx configuration for `/static/` location

3. **Database connection errors**
   - Verify database credentials in `.env`
   - Check if PostgreSQL is running: `sudo systemctl status postgresql`

4. **File upload issues**
   - Check file permissions: `ls -la /home/opportuni/opportuni/opportuni_backend/mediafiles/`
   - Ensure nginx has correct `client_max_body_size`

### Quick Fixes
```bash
# Restart all services
sudo supervisorctl restart opportuni
sudo systemctl restart nginx

# Check all logs
sudo tail -f /var/log/opportuni/gunicorn.log /var/log/nginx/error.log
```

## 💰 Cost Optimization

### Current Setup Cost: ~$13/month
- Droplet: $12/month
- Domain: $1/month

### Future Optimizations
- Use DigitalOcean Spaces for file storage
- Add Redis for caching
- Setup automated backups
- Add monitoring (Sentry)

## 🔐 Security Checklist

- ✅ Firewall enabled (UFW)
- ✅ SSH key authentication
- ✅ SSL certificate
- ✅ Debug mode disabled
- ✅ Secret key in environment variables
- ✅ Database user with limited privileges
- ✅ Nginx security headers
- ✅ File upload restrictions

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review log files for specific errors
3. Ensure all configuration files are correct
4. Test each component individually

Your Opportuni MVP is now ready for production! 🎉
