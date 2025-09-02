from typing import Optional
from telebot import types
from telegram_bot.i18n import t


def language_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton('English 🇬🇧'), types.KeyboardButton('Русский 🇷🇺'))
    kb.add(types.KeyboardButton('Oʻzbekcha 🇺🇿'))
    return kb


def main_menu(lang: str, webapp_url: Optional[str] = None) -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if webapp_url:
        # Web App open button
        web_btn = types.KeyboardButton(text=t(lang, 'link_webapp'), web_app=types.WebAppInfo(url=webapp_url))
        kb.add(web_btn)
    kb.add(types.KeyboardButton(t(lang, 'student')), types.KeyboardButton(t(lang, 'organization')))
    kb.add(types.KeyboardButton(t(lang, 'help_button')))
    return kb


def inline_language_selector(prefix: str = 'lang_') -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton('EN', callback_data=f'{prefix}en'),
        types.InlineKeyboardButton('RU', callback_data=f'{prefix}ru'),
        types.InlineKeyboardButton('UZ', callback_data=f'{prefix}uz'),
    )
    return kb


def student_home(lang: str, webapp_url: Optional[str] = None, channel_url: Optional[str] = None) -> types.ReplyKeyboardMarkup:
    """Main student menu after onboarding."""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton(t(lang, 'home_discover')), types.KeyboardButton(t(lang, 'home_recommend')))
    kb.add(types.KeyboardButton(t(lang, 'home_my_apps')), types.KeyboardButton(t(lang, 'home_profile')))
    # Note: channel_url/webapp_url can be used with inline keyboard if needed in handlers
    return kb
