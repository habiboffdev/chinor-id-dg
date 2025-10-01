from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# Allowed hosts for production
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Database configuration for production (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='opportuni_db'),
        'USER': config('DB_USER', default='opportuni_user'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
    }
}

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Media files configuration for production
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 86400
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL/HTTPS settings (enable when SSL is configured)
if os.environ.get('USE_HTTPS', 'False').lower() == 'true':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://opportuni.app",  # Replace with your domain
    "https://www.opportuni.app",  # Replace with your domain
    "http://localhost:8080",  # For testing
]

# Email backend for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# Logging
# Ensure a file handler exists and is wired without raising on missing keys
log_file = os.environ.get('DJANGO_LOG_FILE', str(BASE_DIR / 'logs' / 'django.log'))

# Handlers
LOGGING.setdefault('handlers', {})
LOGGING['handlers']['file'] = {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'formatter': 'verbose',
    'filename': log_file,
}

# Attach file handler to root and common loggers
LOGGING.setdefault('root', {}).setdefault('handlers', [])
if 'file' not in LOGGING['root']['handlers']:
    LOGGING['root']['handlers'].append('file')

LOGGING.setdefault('loggers', {})
for name in ('django', 'opportuni'):
    LOGGING['loggers'].setdefault(name, {}).setdefault('handlers', [])
    if 'file' not in LOGGING['loggers'][name]['handlers']:
        LOGGING['loggers'][name]['handlers'].append('file')
