import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import telebot

# Load .env
ENV_PATH = Path(__file__).with_name('.env')
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


@dataclass
class Settings:
    bot_token: str
    django_settings_module: Optional[str] = None
    webapp_url: Optional[str] = None
    channel_url: Optional[str] = None
    channel_id: Optional[str] = None  # Channel ID for posting (e.g., @opportuni_channel or -1001234567890)
    default_lang: str = os.getenv('DEFAULT_LANG', 'en')

    @staticmethod
    def load() -> "Settings":
        token = os.getenv('BOT_TOKEN')
        if not token:
            raise RuntimeError('BOT_TOKEN is not set in telegram_bot/.env')
        return Settings(
            bot_token=token,
            django_settings_module=os.getenv('DJANGO_SETTINGS_MODULE'),
            webapp_url=os.getenv('TELEGRAM_WEBAPP_URL'),
            channel_url=os.getenv('TELEGRAM_CHANNEL_URL'),
            channel_id=os.getenv('TELEGRAM_CHANNEL_ID'),
            default_lang=os.getenv('DEFAULT_LANG', 'en'),
        )


def setup_django():
    """Optionally add backend to sys.path and configure Django settings.
    Call this before importing Django models if you want ORM access here.
    """
    # Ensure repo root on sys.path (…/chinor_id_new)
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    # Also add the backend folder explicitly for safety
    backend_dir = repo_root / 'opportuni_backend'
    if backend_dir.exists() and str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    # Determine DJANGO_SETTINGS_MODULE
    settings_module = os.getenv('DJANGO_SETTINGS_MODULE')
    if not settings_module:
        # Default to the backend development settings (manage.py uses this)
        settings_module = 'opportuni.settings.development'
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

    try:
        import django  # noqa: F401
    except ImportError as e:
        raise RuntimeError(
            "Django is not installed in this environment. Activate your bot venv and\n"
            "pip install -r telegram_bot/requirements.txt. Original error: " + str(e)
        )

    try:
        # Allow ORM usage in non-request threads if needed
        os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')
        import django
        django.setup()
    except Exception as e:
        raise RuntimeError(
            f"Failed to setup Django with settings '{settings_module}'.\n"
            f"PYTHONPATH includes: {sys.path[:3]} ...\n"
            f"Error: {e}"
        )


def create_bot(parse_mode: Optional[str] = None) -> telebot.TeleBot:
    settings = Settings.load()
    bot = telebot.TeleBot(settings.bot_token, parse_mode=parse_mode)
    return bot
