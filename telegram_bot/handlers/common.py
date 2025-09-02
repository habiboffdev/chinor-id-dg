from telebot import TeleBot, types
from .state import get_lang, set_lang
from telegram_bot.i18n import t
from telegram_bot import markups


def wire_common_handlers(bot: TeleBot, webapp_url: str | None = None):
    @bot.message_handler(commands=['start', 'help'])
    def start(message: types.Message):
        # If language is known (cache or DB), skip asking
        lang = get_lang(message.from_user.id)
        user = None
        if not lang:
            # Try DB via Django ORM
            try:
                from telegram_bot.config import setup_django
                setup_django()
                import importlib
                User = importlib.import_module('apps.accounts.models').User  # type: ignore
                user = User.objects.filter(telegram_id=message.from_user.id).first()
                if user and user.language:
                    lang = user.language
                    set_lang(message.from_user.id, lang)
            except Exception:
                pass

        if not lang:
            lang = 'en'
            bot.send_message(
                message.chat.id,
                t(lang, 'choose_language'),
                reply_markup=markups.inline_language_selector(prefix='lang_'),
            )
            return

        # Check if user is registered and show appropriate menu
        if not user:
            try:
                from telegram_bot.config import setup_django
                setup_django()
                import importlib
                User = importlib.import_module('apps.accounts.models').User  # type: ignore
                user = User.objects.filter(telegram_id=message.from_user.id).first()
            except Exception:
                pass

        if user and user.user_type == 'student':
            # Show student home menu for registered students
            try:
                StudentProfile = importlib.import_module('apps.students.models').StudentProfile  # type: ignore
                student_profile = StudentProfile.objects.filter(user=user).first()
                if student_profile and student_profile.profile_completed:
                    bot.send_message(
                        message.chat.id,
                        t(lang, 'home_title'),
                        reply_markup=markups.student_home(lang, webapp_url=webapp_url),
                    )
                    return
            except Exception:
                pass

        # Default: show welcome and main menu
        bot.send_message(
            message.chat.id,
            t(lang, 'start_welcome'),
            reply_markup=markups.main_menu(lang, webapp_url),
        )

    @bot.message_handler(func=lambda m: m.text and m.text.lower() == 'help')
    def help_cmd(message: types.Message):
        lang = get_lang(message.from_user.id) or 'en'
        bot.send_message(message.chat.id, t(lang, 'help'))

    # Student text is handled inside student handlers to keep flow self-contained

    @bot.callback_query_handler(func=lambda c: c.data and c.data.startswith('lang_'))
    def set_language(call: types.CallbackQuery):
        code = call.data.split('_', 1)[1]
        set_lang(call.from_user.id, code)
        bot.answer_callback_query(call.id, f"Language set: {code.upper()}")
        # Persist language to DB if possible
        try:
            from telegram_bot.config import setup_django
            setup_django()
            import importlib
            User = importlib.import_module('apps.accounts.models').User  # type: ignore
            u = User.objects.filter(telegram_id=call.from_user.id).first()
            if u:
                u.language = code
                u.save(update_fields=['language'])
        except Exception:
            pass
        # After language selection, check if user is registered and show appropriate menu
        try:
            from telegram_bot.config import setup_django
            setup_django()
            import importlib
            User = importlib.import_module('apps.accounts.models').User  # type: ignore
            user = User.objects.filter(telegram_id=call.from_user.id).first()
            
            if user and user.user_type == 'student':
                # Show student home menu for registered students
                StudentProfile = importlib.import_module('apps.students.models').StudentProfile  # type: ignore
                student_profile = StudentProfile.objects.filter(user=user).first()
                if student_profile and student_profile.profile_completed:
                    bot.send_message(
                        call.message.chat.id,
                        t(code, 'home_title'),
                        reply_markup=markups.student_home(code, webapp_url=webapp_url),
                    )
                    return
        except Exception:
            pass
            
        # Default: show welcome and main menu
        bot.send_message(
            call.message.chat.id,
            t(code, 'start_welcome'),
            reply_markup=markups.main_menu(code, webapp_url),
        )

    @bot.message_handler(func=lambda m: True)
    def fallback(message: types.Message):
        lang = get_lang(message.from_user.id) or 'en'
        bot.send_message(message.chat.id, t(lang, 'unknown'))
