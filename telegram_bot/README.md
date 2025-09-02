# Opportuni Telegram Bot

This folder contains a modular Telegram Bot built on pyTelegramBotAPI (TeleBot). It runs alongside the existing Django backend. Nothing auto-starts; you run it manually.

Key points
- Separate Python virtual environment for the bot (isolated from Django app env).
- Environment-based config (no hardcoded secrets).
- Modular structure: config, i18n, markups, handlers.
- Polling for local/dev; webhook skeleton for production.

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
