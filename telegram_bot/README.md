# Opportuni Telegram Bot

This folder contains a modular Telegram Bot built on pyTelegramBotAPI (TeleBot). It runs alongside the existing Django backend and includes channel administration features for automatic opportunity posting.

Key features:
- Student registration and profile management
- **Channel administration and automatic opportunity posting**
- Admin panel with statistics and channel testing
- Separate Python virtual environment for the bot (isolated from Django app env)
- Environment-based config (no hardcoded secrets)
- Modular structure: config, i18n, markups, handlers
- Polling for local/dev; webhook skeleton for production

## Setup (dedicated env)
```bash
# from repo root
python3 -m venv .venv_bot
source .venv_bot/bin/activate
pip install --upgrade pip
pip install -r telegram_bot/requirements.txt

cp telegram_bot/.env.example telegram_bot/.env
# Edit telegram_bot/.env and set required variables:
# - BOT_TOKEN (from @BotFather)
# - TELEGRAM_CHANNEL_ID (your channel ID)
# - TELEGRAM_ADMIN_IDS (your Telegram user ID)
# - DJANGO_SETTINGS_MODULE=opportuni.settings.development

# Optional: verify Django import wiring if you plan to use ORM from bot
python - <<'PY'
import telegram_bot.config as c
c.setup_django()
from apps.accounts.models import User
print('Django OK • Users count (if DB configured):', User.objects.count())
PY
```

## Channel Administration Setup

1. **Create Telegram Channel:**
   - Create a public or private channel
   - Add your bot as administrator with posting permissions
   - Get channel ID (use @userinfobot or check bot logs)

2. **Configure Environment:**
   ```bash
   # In telegram_bot/.env
   TELEGRAM_CHANNEL_ID=@your_channel_username  # or -1001234567890
   TELEGRAM_CHANNEL_URL=https://t.me/your_channel
   TELEGRAM_ADMIN_IDS=123456789,987654321
   TELEGRAM_BOT_ENABLED=true
   ```

3. **Test Channel Posting:**
   ```bash
   # Test from Django
   cd opportuni_backend
   python manage.py test_telegram_channel --latest
   
   # Or use admin command in Telegram
   # Send /admin to your bot, then click "Test Channel"
   ```

## Run (manual)
- **Polling (development):**
```bash
source .venv_bot/bin/activate
python -c "from telegram_bot.bot import run_polling; run_polling()"

# Or from Django (recommended for channel features):
cd opportuni_backend
python manage.py run_telegram_bot
```

- **Webhook (production skeleton):** configure Nginx -> webhook endpoint -> telebot webhook. See `bot.py` notes.

## Channel Administration Features

### Automatic Posting
- Automatically posts opportunities to channel when published
- Rich formatting with emojis, deadlines, and application info
- Inline buttons for applying and viewing organization

### Admin Commands
- `/admin` - Access admin panel (requires authorization)
- `/channel_post` - Manually post latest opportunities
- Admin panel includes statistics, channel testing, and broadcast features

### Django Integration
- Uses Django signals to detect new/published opportunities
- Management commands for testing and running the bot
- Configurable through Django settings

See [CHANNEL_ADMIN.md](CHANNEL_ADMIN.md) for detailed documentation.

## Files
- **config.py**: env loading, TeleBot instance, optional Django setup
- **i18n.py**: translations for en/ru/uz
- **markups.py**: keyboards and web app buttons
- **handlers/**: command and message handlers
  - **student.py**: student registration flow
  - **admin.py**: channel administration and admin panel
  - **common.py**: common commands and fallbacks
- **bot.py**: wires everything and exposes run_polling()/run_webhook()
- **STRATEGY.md**: implementation plan for Student/Organization/Admin
- **CHANNEL_ADMIN.md**: detailed channel administration documentation

## Testing
```bash
# Run comprehensive tests
python test_channel_admin.py

# Test specific features
cd opportuni_backend
python manage.py test_telegram_channel --opportunity-id 123
python manage.py run_telegram_bot --interval 1
```

Notes:
- Per project doc: Context7 used for latest pyTelegramBotAPI references
- No server is started automatically by this code
- Channel posting respects SMM rules and best practices
- Thread-safe state management for concurrent users
- Start simple; persist state later (DB/Redis) as needed

## Setup (dedicated env)
```bash
# from repo root
python3 -m venv .venv_bot
source .venv_bot/bin/activate
pip install --upgrade pip
pip install -r telegram_bot/requirements.txt

cp telegram_bot/.env.example telegram_bot/.env
# Edit telegram_bot/.env and set BOT_TOKEN and DJANGO_SETTINGS_MODULE
# For this repository, the backend defaults to:
# DJANGO_SETTINGS_MODULE=opportuni.settings.development

# Optional: verify Django import wiring if you plan to use ORM from bot
python - <<'PY'
import telegram_bot.config as c
c.setup_django()
from apps.accounts.models import User
print('Django OK • Users count (if DB configured):', User.objects.count())
PY
```

## Run (manual)
- Polling (development):
```bash
source .venv_bot/bin/activate
python -c "from telegram_bot.bot import run_polling; run_polling()"
```

- Webhook (production skeleton): configure Nginx -> webhook endpoint -> telebot webhook. See `bot.py` notes.

## Files
- config.py: env loading, TeleBot instance, optional Django setup.
- i18n.py: translations for en/ru/uz.
- markups.py: keyboards and web app buttons.
- handlers/: command and message handlers.
- bot.py: wires everything and exposes run_polling()/run_webhook().
- STRATEGY.md: implementation plan for Student/Organization/Admin.

Notes
- Per project doc: Context7 used for latest pyTelegramBotAPI references.
- No server is started automatically by this code.
- Start simple; persist state later (DB/Redis) as needed.
