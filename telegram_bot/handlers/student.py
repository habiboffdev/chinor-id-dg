from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Optional

from telebot import TeleBot, types
import re

from telegram_bot.i18n import t
from telegram_bot import markups
from .state import get_lang as get_global_lang, set_lang as set_global_lang
from telegram_bot.config import Settings


# Thread-safe in-memory state for MVP; replace with Redis later
@dataclass
class StudentState:
    lang: str = 'en'
    active: bool = False
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_current_student: Optional[bool] = None
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    scores: list[str] = field(default_factory=list)  # raw inputs like "SAT 1450", "IELTS 7"
    preferences: Optional[str] = None
    pref_tags: set[str] = field(default_factory=set)


# Thread-safe state management
_student_state: dict[int, StudentState] = {}
_state_lock = threading.Lock()


def get_state(user_id: int) -> StudentState:
    """Thread-safe state retrieval"""
    with _state_lock:
        if user_id not in _student_state:
            _student_state[user_id] = StudentState()
        return _student_state[user_id]


def clear_state(user_id: int) -> None:
    """Clear user state after completion to prevent memory leaks"""
    with _state_lock:
        _student_state.pop(user_id, None)


_NON_WORD_RE = re.compile(r"[^\w]+", flags=re.UNICODE)


def _normalize_text(s: str) -> str:
    # Lowercase, remove non-word characters (emojis, punctuation, symbols), collapse spaces
    s = s.lower().strip()
    s = _NON_WORD_RE.sub("", s)
    return s


def wire_student_handlers(bot: TeleBot):
    from telegram_bot.config import setup_django
    try:
        setup_django()
        import importlib
        User = importlib.import_module('apps.accounts.models').User  # type: ignore[attr-defined]
        StudentProfile = importlib.import_module('apps.students.models').StudentProfile  # type: ignore[attr-defined]
    except Exception:
        User = None  # type: ignore
        StudentProfile = None  # type: ignore

    @bot.message_handler(commands=['student'])
    def student_entry(message: types.Message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        st = get_state(user_id)
        st.active = True

        # 1) Find or create User by telegram_id with database-level locking
        if User is not None:
            from django.db import transaction
            
            try:
                # Use atomic transaction with select_for_update to prevent race conditions
                with transaction.atomic():
                    user = User.objects.filter(telegram_id=user_id).select_for_update().first()
                    if not user:
                        # Double-check pattern to prevent duplicate creation
                        user = User.objects.filter(telegram_id=user_id).first()
                        if not user:
                            # Create a minimal user with email placeholder; will be updated later
                            email = f"tg_{user_id}@placeholder.local"
                            username = message.from_user.username or str(user_id)
                            first_name = message.from_user.first_name or ''
                            last_name = message.from_user.last_name or ''
                            user = User.objects.create(
                                telegram_id=user_id,
                                email=email,
                                username=username,
                                first_name=first_name,
                                last_name=last_name,
                                user_type='student',
                            )
                            if StudentProfile is not None:
                                StudentProfile.objects.get_or_create(user=user)
            except Exception as e:
                print(f"[telegram_bot] Error creating user {user_id}: {e}")
                # Try to find existing user as fallback
                user = User.objects.filter(telegram_id=user_id).first()

        # 2) Prefer persistent language from DB
        global_lang = get_global_lang(user_id)
        if not global_lang and User is not None:
            try:
                u = User.objects.filter(telegram_id=user_id).only('language').first()
                if u and u.language:
                    global_lang = u.language
                    set_global_lang(user_id, global_lang)
            except Exception:
                pass
        if not global_lang:
            bot.send_message(
                chat_id,
                t(st.lang, 'choose_language'),
                reply_markup=markups.inline_language_selector(prefix='lang_'),
            )
            return
        st.lang = global_lang
        bot.send_message(chat_id, t(st.lang, 'ask_full_name'))

    @bot.message_handler(func=lambda m: isinstance(m.text, str) and _normalize_text(m.text) in {'student', 'студент', 'talaba'})
    def student_shortcut(message: types.Message):
        # Start student flow via text button
        student_entry(message)
    @bot.message_handler(func=lambda m: isinstance(m.text, str) and _normalize_text(m.text) in {'organization', 'tashkilot', 'организация'})
    def organization_shortcut(message: types.Message):
        # Start organization flow via text button
        bot.send_message(message.chat.id, "🏢 " + t(get_global_lang(message.from_user.id) or 'en', 'org_coming_soon'))

    @bot.message_handler(func=lambda m: _awaiting(m.from_user.id, 'full_name'))
    def collect_full_name(message: types.Message):
        st = get_state(message.from_user.id)
        st.full_name = (message.text or '').strip()
        # Ask phone - allow contact share
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton(t(st.lang, 'share_phone'), request_contact=True))
        bot.send_message(message.chat.id, t(st.lang, 'ask_phone'), reply_markup=kb)

    @bot.message_handler(content_types=['contact'])
    def collect_phone_contact(message: types.Message):
        st = get_state(message.from_user.id)
        if message.contact and message.contact.phone_number:
            st.phone = message.contact.phone_number
        else:
            st.phone = None
        bot.send_message(message.chat.id, t(st.lang, 'ask_email'), reply_markup=types.ReplyKeyboardRemove())

    @bot.message_handler(func=lambda m: _awaiting(m.from_user.id, 'phone_text'))
    def collect_phone_text(message: types.Message):
        st = get_state(message.from_user.id)
        st.phone = (message.text or '').strip()
        bot.send_message(message.chat.id, t(st.lang, 'ask_email'))

    @bot.message_handler(func=lambda m: _awaiting(m.from_user.id, 'email'))
    def collect_email(message: types.Message):
        st = get_state(message.from_user.id)
        st.email = (message.text or '').strip()
        # Ask if currently studying
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton(t(st.lang, 'yes')), types.KeyboardButton(t(st.lang, 'no')))
        bot.send_message(message.chat.id, t(st.lang, 'ask_current_student'), reply_markup=kb)

    @bot.message_handler(func=lambda m: _awaiting(m.from_user.id, 'is_current_student'))
    def collect_is_current_student(message: types.Message):
        st = get_state(message.from_user.id)
        ans = (message.text or '').lower()
        st.is_current_student = ans.startswith(t(st.lang, 'yes').lower()[0])
        bot.send_message(message.chat.id, t(st.lang, 'ask_university'), reply_markup=types.ReplyKeyboardRemove())

    @bot.message_handler(func=lambda m: _awaiting(m.from_user.id, 'university'))
    def collect_university(message: types.Message):
        st = get_state(message.from_user.id)
        st.university = (message.text or '').strip()
        if st.is_current_student:
            bot.send_message(message.chat.id, t(st.lang, 'ask_major'))
        else:
            _ask_scores(message)

    @bot.message_handler(func=lambda m: _awaiting(m.from_user.id, 'major'))
    def collect_major(message: types.Message):
        st = get_state(message.from_user.id)
        st.major = (message.text or '').strip()
        bot.send_message(message.chat.id, t(st.lang, 'ask_grad_year'))

    @bot.message_handler(func=lambda m: _awaiting(m.from_user.id, 'grad_year'))
    def collect_grad_year(message: types.Message):
        st = get_state(message.from_user.id)
        try:
            st.graduation_year = int((message.text or '').strip())
        except ValueError:
            bot.send_message(message.chat.id, t(st.lang, 'invalid_year'))
            return
        _ask_scores(message)

    def _ask_scores(message: types.Message):
        st = get_state(message.from_user.id)
        bot.send_message(message.chat.id, t(st.lang, 'ask_scores'))

    @bot.message_handler(func=lambda m: _awaiting(m.from_user.id, 'scores'))
    def collect_scores(message: types.Message):
        st = get_state(message.from_user.id)
        raw = (message.text or '').strip()
        if raw and raw != '-':
            st.scores = [s.strip() for s in raw.split(',') if s.strip()]
        # Show interactive preferences
        _show_preferences(message.chat.id, st)

    def _show_preferences(chat_id: int, st: StudentState):
        # Build inline keyboard with toggles
        options = [
            ('volunteer', 'pref_volunteer'),
            ('conference', 'pref_conference'),
            ('international_events', 'pref_international_events'),
            ('camp', 'pref_camp'),
            ('grant', 'pref_grant'),
            ('mentoring', 'pref_mentoring'),
            ('academic_program', 'pref_academic_program'),
            ('scholarships', 'pref_scholarships'),
        ]
        kb = types.InlineKeyboardMarkup()
        row: list[types.InlineKeyboardButton] = []
        for key, i18n_key in options:
            checked = ' ✅' if key in st.pref_tags else ''

            label = t(st.lang, i18n_key) + checked
            row.append(types.InlineKeyboardButton(label, callback_data=f'pref_{key}'))
            if len(row) == 2:
                kb.row(*row)
                row = []
        if row:
            kb.row(*row)
        kb.row(types.InlineKeyboardButton(t(st.lang, 'pref_done'), callback_data='pref_done'))
        bot.send_message(chat_id, t(st.lang, 'pref_title'), reply_markup=kb)

    @bot.callback_query_handler(func=lambda c: c.data and c.data.startswith('pref_'))
    def toggle_preference(call: types.CallbackQuery):
        user_id = call.from_user.id
        st = get_state(user_id)
        action = call.data.split('_', 1)[1]
        if action == 'done':
            st.preferences = ', '.join(sorted(st.pref_tags)) if st.pref_tags else ''
            bot.answer_callback_query(call.id, 'Saved ✅', show_alert=False)
            # Persist and summarize
            _finish_and_persist(user_id, call.message.chat.id, st)
            return
        # Toggle
        if action in st.pref_tags:
            st.pref_tags.remove(action)
        else:
            st.pref_tags.add(action)
        bot.answer_callback_query(call.id, 'Updated')
        # Refresh markup
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        _show_preferences(call.message.chat.id, st)

    def _finish_and_persist(user_id: int, chat_id: int, st: StudentState):
        # Persist to DB if ORM available
        if User is not None:
            try:
                user = User.objects.filter(telegram_id=user_id).first()
                if user:
                    # Update core user info
                    if st.full_name and ' ' in st.full_name:
                        user.first_name = st.full_name.split(' ', 1)[0]
                        user.last_name = st.full_name.split(' ', 1)[1]
                    elif st.full_name:
                        user.first_name = st.full_name
                    if st.phone:
                        user.phone = st.phone
                    if st.email and '@' in st.email:
                        user.email = st.email
                    user.user_type = 'student'
                    user.telegram_id = user_id
                    # Persist chosen language if present
                    try:
                        if st.lang and hasattr(user, 'language'):
                            user.language = st.lang
                    except Exception:
                        pass
                    user.save()

                    if StudentProfile is not None:
                        # Import models inside to avoid module-level dependency
                        import importlib
                        _mod = importlib.import_module('apps.students.models')
                        Preference = getattr(_mod, 'Preference')
                        StudentPreference = getattr(_mod, 'StudentPreference')
                        AcademicExam = getattr(_mod, 'AcademicExam')
                        AcademicExamSection = getattr(_mod, 'AcademicExamSection')
                        StudentExamScore = getattr(_mod, 'StudentExamScore')

                        sp, _ = StudentProfile.objects.get_or_create(user=user)
                        sp.phone = st.phone or ''
                        sp.university = st.university or ''
                        sp.major = st.major or ''
                        sp.graduation_year = st.graduation_year
                        sp.profile_completed = True
                        sp.save()

                        # Persist preferences to structured tables
                        for key in sorted(st.pref_tags):
                            pref, _ = Preference.objects.get_or_create(key=key, defaults={'name': key.replace('_', ' ').title()})
                            StudentPreference.objects.get_or_create(student=sp, preference=pref)

                        # Persist academic scores with minimal defaults
                        # Expected formats e.g. "SAT 1450", "IELTS 7"
                        for entry in st.scores:
                            parts = entry.split()
                            if not parts:
                                continue
                            exam_name = parts[0].strip().upper()
                            try:
                                score_val = float(parts[1]) if len(parts) > 1 else None
                            except Exception:
                                score_val = None

                            if not score_val:
                                continue

                            exam_slug = exam_name.lower()
                            exam, _ = AcademicExam.objects.get_or_create(slug=exam_slug, defaults={'name': exam_name})
                            # Create a default single section if none is present
                            section, _ = AcademicExamSection.objects.get_or_create(
                                exam=exam,
                                name='Total',
                                defaults={'max_score': 100, 'min_score': 0, 'step': 1, 'sort_order': 0},
                            )
                            # Upsert by unique (student, section)
                            StudentExamScore.objects.update_or_create(
                                student=sp,
                                section=section,
                                defaults={'exam': exam, 'score': score_val},
                            )
            except Exception:
                # Silently continue to summary; persistence is best-effort in MVP
                pass

        # Summary and end of flow
        summary = _summary_text(st)
        bot.send_message(chat_id, summary, parse_mode='HTML')
        # Show student home
        settings = Settings.load()
        bot.send_message(
            chat_id,
            t(st.lang, 'home_title'),
            reply_markup=markups.student_home(st.lang, webapp_url=settings.webapp_url, channel_url=settings.channel_url),
        )
        st.active = False
        
        # Clean up state after successful registration
        clear_state(chat_id)

    # We won't reach here anymore since Finish happens via inline button
    pass

    # Student home actions
    @bot.message_handler(func=lambda m: _is_student_home(m.from_user.id) and m.text == t(get_global_lang(m.from_user.id) or 'en', 'home_discover'))
    def home_discover(message: types.Message):
        lang = get_global_lang(message.from_user.id) or 'en'
        settings = Settings.load()
        kb = types.InlineKeyboardMarkup()
        if settings.channel_url:
            kb.add(types.InlineKeyboardButton(t(lang, 'open_channel'), url=settings.channel_url))
        if settings.webapp_url:
            kb.add(types.InlineKeyboardButton(t(lang, 'open_webapp'), web_app=types.WebAppInfo(url=settings.webapp_url)))
        bot.send_message(message.chat.id, t(lang, 'discover_hint'), reply_markup=kb)

    @bot.message_handler(func=lambda m: _is_student_home(m.from_user.id) and m.text == t(get_global_lang(m.from_user.id) or 'en', 'home_recommend'))
    def home_recommend(message: types.Message):
        lang = get_global_lang(message.from_user.id) or 'en'
        bot.send_message(message.chat.id, t(lang, 'recommend_coming'))

    @bot.message_handler(func=lambda m: _is_student_home(m.from_user.id) and m.text == t(get_global_lang(m.from_user.id) or 'en', 'home_my_apps'))
    def home_my_apps(message: types.Message):
        lang = get_global_lang(message.from_user.id) or 'en'
        # Placeholder: later fetch applications via API
        bot.send_message(message.chat.id, t(lang, 'no_apps'))

    @bot.message_handler(func=lambda m: _is_student_home(m.from_user.id) and m.text == t(get_global_lang(m.from_user.id) or 'en', 'home_profile'))
    def home_profile(message: types.Message):
        lang = get_global_lang(message.from_user.id) or 'en'
        # Fetch actual profile data from database
        try:
            user = User.objects.filter(telegram_id=message.from_user.id).first()
            if user and user.user_type == 'student':
                import importlib
                _mod = importlib.import_module('apps.students.models')
                StudentProfile = getattr(_mod, 'StudentProfile')
                StudentPreference = getattr(_mod, 'StudentPreference')
                StudentExamScore = getattr(_mod, 'StudentExamScore')
                
                sp = StudentProfile.objects.filter(user=user).first()
                if sp:
                    # Build beautiful profile summary
                    profile_text = _build_profile_summary(user, sp, lang)
                    bot.send_message(message.chat.id, profile_text, parse_mode='HTML')
                    return
        except Exception:
            pass
        
        # Fallback to basic message
        bot.send_message(message.chat.id, "❌ Profile not found", parse_mode='HTML')

    @bot.message_handler(func=lambda m: m.text and m.text in [
        t('en', 'help_button'), t('ru', 'help_button'), t('uz', 'help_button')
    ])
    def help_button_handler(message: types.Message):
        """Handle help button from keyboard in any language"""
        lang = get_global_lang(message.from_user.id) or 'en'
        
        # Check if user is registered and show appropriate help
        user = None
        try:
            user = User.objects.filter(telegram_id=message.from_user.id).first()
            
            if user and user.user_type == 'student':
                # Check if profile is completed
                import importlib
                _mod = importlib.import_module('apps.students.models')
                StudentProfile = getattr(_mod, 'StudentProfile')
                student_profile = StudentProfile.objects.filter(user=user).first()
                if student_profile and student_profile.profile_completed:
                    # Show registered user help
                    bot.send_message(message.chat.id, t(lang, 'help_registered'), parse_mode='HTML')
                    return
        except Exception:
            pass
        
        # Show registration help for unregistered users
        bot.send_message(message.chat.id, t(lang, 'help_registration'), parse_mode='HTML')


def _awaiting(user_id: int, field: str) -> bool:
    st = get_state(user_id)
    if not st.active:
        return False
    # Determine expected field based on what’s missing
    if st.full_name is None:
        return field == 'full_name'
    if st.phone is None:
        # Accept either contact or text handler
        return field in ('phone_text',)
    if st.email is None:
        return field == 'email'
    if st.is_current_student is None:
        return field == 'is_current_student'
    if st.university is None:
        return field == 'university'
    if st.is_current_student:
        if st.major is None:
            return field == 'major'
        if st.graduation_year is None:
            return field == 'grad_year'
    if not st.scores:
        return field == 'scores'
    if st.preferences is None:
        return field == 'preferences'
    return False


def _build_profile_summary(user, student_profile, lang: str) -> str:
    """Build a beautiful, emoji-rich profile summary from database data."""
    lines = [
        f"👤 <b>{t(lang, 'profile_title')}</b>",
        "",
    ]
    
    # Personal Info
    full_name = f"{user.first_name} {user.last_name}".strip() or t(lang, 'not_set')
    lines.append(f"📝 <b>{t(lang, 'profile_name')}</b> {full_name}")
    
    if user.phone or student_profile.phone:
        phone = user.phone or student_profile.phone
        lines.append(f"📞 <b>{t(lang, 'profile_phone')}</b> {phone}")
    
    lines.append(f"📧 <b>{t(lang, 'profile_email')}</b> {user.email}")
    
    # Academic Info
    if student_profile.university:
        lines.append(f"🏫 <b>{t(lang, 'profile_university')}</b> {student_profile.university}")
    
    if student_profile.major:
        lines.append(f"📚 <b>{t(lang, 'profile_major')}</b> {student_profile.major}")
    
    if student_profile.graduation_year:
        lines.append(f"🎓 <b>{t(lang, 'profile_graduation')}</b> {student_profile.graduation_year}")
    
    if student_profile.gpa:
        lines.append(f"📊 <b>{t(lang, 'profile_gpa')}</b> {student_profile.gpa}")
    
    # Academic Scores
    try:
        import importlib
        _mod = importlib.import_module('apps.students.models')
        StudentExamScore = getattr(_mod, 'StudentExamScore')
        
        scores = StudentExamScore.objects.filter(student=student_profile).select_related('exam', 'section')
        if scores.exists():
            lines.append("")
            lines.append(f"🧪 <b>{t(lang, 'profile_scores')}</b>")
            for score in scores:
                lines.append(f"   • {score.exam.name}: {score.score}")
    except Exception:
        pass
    
    # Preferences
    try:
        import importlib
        _mod = importlib.import_module('apps.students.models')
        StudentPreference = getattr(_mod, 'StudentPreference')
        
        prefs = StudentPreference.objects.filter(student=student_profile).select_related('preference')
        if prefs.exists():
            lines.append("")
            lines.append(f"⭐ <b>{t(lang, 'profile_interests')}</b>")
            pref_names = [p.preference.name for p in prefs]
            lines.append(f"   {', '.join(pref_names)}")
    except Exception:
        pass
    
    # Status
    lines.append("")
    status_key = 'status_completed' if student_profile.profile_completed else 'status_incomplete'
    status = "✅" if student_profile.profile_completed else "⏳"
    lines.append(f"📋 <b>{t(lang, 'profile_status')}</b> {status} {t(lang, status_key)}")
    
    return '\n'.join(lines)


def _summary_text(st: StudentState) -> str:
    lines = [
        '<b>Profile Summary</b>',
        f"Name: {st.full_name or '-'}",
        f"Phone: {st.phone or '-'}",
        f"Email: {st.email or '-'}",
        f"University: {st.university or '-'}",
        f"Major: {st.major or '-'}",
        f"Graduation Year: {st.graduation_year or '-'}",
        f"Scores: {', '.join(st.scores) if st.scores else '-'}",
        f"Preferences: {st.preferences or '-'}",
    ]
    return '\n'.join(lines)


def _is_student_home(user_id: int) -> bool:
    # Consider user on home if they have finished onboarding once (active False) and have a lang set
    st = get_state(user_id)
    return (not st.active) and bool(get_global_lang(user_id))
