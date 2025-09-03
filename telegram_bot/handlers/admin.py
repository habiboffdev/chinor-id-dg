"""
Admin handlers for Opportuni Telegram Bot
Handles channel administration, opportunity broadcasting, and bot management
"""
import threading
from typing import Optional
from datetime import datetime

import telebot
from telebot import types
from django.utils import timezone

from telegram_bot.i18n import t
from telegram_bot.config import Settings
from telegram_bot.handlers.state import get_lang as get_global_lang


# Thread-safe storage for admin state
_admin_lock = threading.Lock()
_admin_users = set()  # Store admin telegram user IDs


def is_admin(user_id: int) -> bool:
    """Check if user is authorized admin"""
    with _admin_lock:
        return user_id in _admin_users


def add_admin(user_id: int) -> None:
    """Add user to admin list"""
    with _admin_lock:
        _admin_users.add(user_id)


def remove_admin(user_id: int) -> None:
    """Remove user from admin list"""
    with _admin_lock:
        _admin_users.discard(user_id)


def load_admins_from_config() -> None:
    """Load admin user IDs from environment/config"""
    import os
    admin_ids = os.getenv('TELEGRAM_ADMIN_IDS', '')
    if admin_ids:
        try:
            ids = [int(uid.strip()) for uid in admin_ids.split(',') if uid.strip()]
            with _admin_lock:
                _admin_users.update(ids)
        except ValueError:
            print("[admin] Invalid TELEGRAM_ADMIN_IDS format. Use comma-separated integers.")


def format_opportunity_for_channel(opportunity) -> str:
    """Format opportunity for channel posting"""
    # Import here to avoid circular imports
    try:
        from apps.opportunities.models import Opportunity
    except ImportError:
        return "Error: Cannot access Django models"
    
    if not isinstance(opportunity, Opportunity):
        return "Error: Invalid opportunity object"
    
    # Format opportunity info
    lines = []
    
    # Title and organization
    lines.append(f"🚀 <b>{opportunity.title}</b>")
    lines.append(f"🏢 {opportunity.organization.name}")
    lines.append("")
    
    # Type and location
    type_emoji = {
        'internship': '💼',
        'volunteer': '🤝',
        'competition': '🏆',
        'scholarship': '💰',
        'job': '👔',
        'workshop': '🛠️',
        'conference': '📢'
    }
    emoji = type_emoji.get(opportunity.opportunity_type, '📝')
    lines.append(f"{emoji} <b>Type:</b> {opportunity.get_opportunity_type_display()}")
    
    if opportunity.location:
        location_icon = "🌐" if opportunity.is_remote else "📍"
        location_text = f"{opportunity.location}"
        if opportunity.is_remote:
            location_text += " (Remote)"
        lines.append(f"{location_icon} <b>Location:</b> {location_text}")
    if opportunity.age_min or opportunity.age_max:
        age_text = "Age: "
        if opportunity.age_min and opportunity.age_max:
            age_text += f"{opportunity.age_min}-{opportunity.age_max}"
        elif opportunity.age_min:
            age_text += f"{opportunity.age_min}+"
        elif opportunity.age_max:
            age_text += f"up to {opportunity.age_max}"
        lines.append(f"🎂 <b>{age_text}</b>")
    lines.append("")
    
    # Description (truncated if too long)
    description = opportunity.description.strip()
    if len(description) > 300:
        description = description[:300] + "..."
    lines.append(f"📋 <b>Description:</b>\n{description}")
    lines.append("")
    
    # Requirements
    if opportunity.required_major:
        lines.append(f"🎓 <b>Recommended major:</b> {opportunity.required_major}")
    
    if opportunity.graduation_year_min or opportunity.graduation_year_max:
        year_text = "Graduation Year: "
        if opportunity.graduation_year_min and opportunity.graduation_year_max:
            year_text += f"{opportunity.graduation_year_min}-{opportunity.graduation_year_max}"
        elif opportunity.graduation_year_min:
            year_text += f"{opportunity.graduation_year_min}+"
        elif opportunity.graduation_year_max:
            year_text += f"up to {opportunity.graduation_year_max}"
        lines.append(f"📅 <b>{year_text}</b>")
    
    if opportunity.min_gpa:
        lines.append(f"📊 <b>Min GPA:</b> {opportunity.min_gpa}")
    
    if opportunity.compensation:
        lines.append(f"💵 <b>Compensation:</b> {opportunity.compensation}")
    
    lines.append("")
    
    # Deadline
    deadline_str = opportunity.application_deadline.strftime("%B %d, %Y")
    lines.append(f"⏰ <b>Application Deadline:</b> {deadline_str}")
    
    # Application count
    if opportunity.max_applications:
        lines.append(f"👥 <b>Applications:</b> {opportunity.application_count}/{opportunity.max_applications}")
    else:
        lines.append(f"👥 <b>Applications:</b> {opportunity.application_count}")
    
    lines.append("")
    lines.append("🔗 <b>Apply now on <a href=\"https://opportuni.app\">Opportuni!</a></b>")

    return "\n".join(lines)


def create_opportunity_keyboard(opportunity, webapp_url: Optional[str] = None) -> types.InlineKeyboardMarkup:
    """Create inline keyboard for opportunity post"""
    keyboard = types.InlineKeyboardMarkup()
    
    # Apply button (to web app or direct link)
    if webapp_url:
        apply_url = f"{webapp_url}/opportunity-details.html?id={opportunity.id}"
        keyboard.add(types.InlineKeyboardButton("📝 Apply Now", url=apply_url))
    
    # Organization profile button
    if webapp_url:
        org_url = f"{webapp_url}/organization/profile.html?id={opportunity.organization.id}"
        keyboard.add(types.InlineKeyboardButton("🏢 View Organization", url=org_url))
    
    return keyboard


def post_opportunity_to_channel(bot: telebot.TeleBot, opportunity, channel_id: str, webapp_url: Optional[str] = None) -> bool:
    """Post new opportunity to channel"""
    try:
        # Format message
        message_text = format_opportunity_for_channel(opportunity)
        
        # Create keyboard
        keyboard = create_opportunity_keyboard(opportunity, webapp_url)
        image = None    
        if opportunity.cover_image:
            image = opportunity.cover_image.url
        # Send to channel
        if image is None:
            bot.send_message(
                chat_id=channel_id,
                text=message_text,
                parse_mode='HTML',
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        else:
            bot.send_photo(
                chat_id=channel_id,
                photo=image,
                caption=message_text,
                parse_mode='HTML',
                reply_markup=keyboard,

            )
        return True
    except Exception as e:
        print(f"[admin] Failed to post opportunity {opportunity.id} to channel: {e}")
        return False


def wire_admin_handlers(bot: telebot.TeleBot):
    """Wire admin handlers to bot"""
    
    # Load admins on startup
    load_admins_from_config()
    
    @bot.message_handler(commands=['admin'])
    def admin_command(message: types.Message):
        """Admin panel access"""
        user_id = message.from_user.id
        lang = get_global_lang(user_id) or 'en'
        
        if not is_admin(user_id):
            bot.send_message(message.chat.id, t(lang, 'access_denied'))
            return
        
        # Show admin menu
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(t(lang, 'admin_stats'), callback_data='admin_stats'))
        keyboard.add(types.InlineKeyboardButton(t(lang, 'admin_broadcast'), callback_data='admin_broadcast'))
        keyboard.add(types.InlineKeyboardButton(t(lang, 'admin_channel_test'), callback_data='admin_channel_test'))
        
        bot.send_message(
            message.chat.id,
            t(lang, 'admin_welcome'),
            reply_markup=keyboard
        )
    
    @bot.callback_query_handler(func=lambda c: c.data and c.data.startswith('admin_'))
    def admin_callback(call: types.CallbackQuery):
        """Handle admin callbacks"""
        user_id = call.from_user.id
        lang = get_global_lang(user_id) or 'en'
        
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, t(lang, 'access_denied'))
            return
        
        action = call.data
        
        if action == 'admin_stats':
            # Show bot statistics
            try:
                from django.contrib.auth.models import User
                from apps.students.models import StudentProfile
                from apps.organizations.models import Organization
                from apps.opportunities.models import Opportunity
                from apps.applications.models import Application
                
                user_count = User.objects.count()
                student_count = StudentProfile.objects.count()
                org_count = Organization.objects.count()
                opportunity_count = Opportunity.objects.filter(status='published').count()
                application_count = Application.objects.count()
                
                stats_text = f"""📊 <b>Bot Statistics</b>
                
👥 Total Users: {user_count}
🎓 Students: {student_count}
🏢 Organizations: {org_count}
🚀 Published Opportunities: {opportunity_count}
📝 Applications: {application_count}

Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                
                bot.edit_message_text(
                    stats_text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='HTML'
                )
            except Exception as e:
                bot.answer_callback_query(call.id, f"Error fetching stats: {e}")
        
        elif action == 'admin_broadcast':
            bot.answer_callback_query(call.id, "Broadcast feature coming soon!")
        
        elif action == 'admin_channel_test':
            # Test channel posting
            settings = Settings.load()
            channel_id = getattr(settings, 'channel_id', None)
            
            if not channel_id:
                bot.answer_callback_query(call.id, "No channel configured!")
                return
            
            try:
                test_message = f"""🧪 <b>Channel Test</b>

This is a test message from Opportuni Bot.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Admin: {call.from_user.first_name or 'Admin'}"""
                
                bot.send_message(
                    chat_id=channel_id,
                    text=test_message,
                    parse_mode='HTML'
                )
                bot.answer_callback_query(call.id, "✅ Test message sent to channel!")
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ Channel test failed: {e}")
        
        else:
            bot.answer_callback_query(call.id, "Unknown action")
    
    @bot.message_handler(commands=['channel_post'])
    def manual_channel_post(message: types.Message):
        """Manually post latest opportunities to channel"""
        user_id = message.from_user.id
        lang = get_global_lang(user_id) or 'en'
        
        if not is_admin(user_id):
            bot.send_message(message.chat.id, t(lang, 'access_denied'))
            return
        
        try:
            from apps.opportunities.models import Opportunity
            
            # Get latest published opportunities (last 5)
            opportunities = Opportunity.objects.filter(
                status='published'
            ).order_by('-created_at')[:5]
            
            if not opportunities:
                bot.send_message(message.chat.id, "No published opportunities found.")
                return
            
            settings = Settings.load()
            channel_id = getattr(settings, 'channel_id', None)
            
            if not channel_id:
                bot.send_message(message.chat.id, "No channel configured!")
                return
            
            posted_count = 0
            for opp in opportunities:
                if post_opportunity_to_channel(bot, opp, channel_id, settings.webapp_url):
                    posted_count += 1
            
            bot.send_message(
                message.chat.id,
                f"✅ Posted {posted_count}/{len(opportunities)} opportunities to channel."
            )
            
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error posting to channel: {e}")


def auto_post_new_opportunity(opportunity) -> None:
    """
    Auto-post new opportunity to channel when created.
    This should be called from Django signals or webhooks.
    """
    try:
        from telegram_bot.config import create_bot, Settings
        
        settings = Settings.load()
        channel_id = getattr(settings, 'channel_id', None)
        
        if not channel_id:
            print("[admin] No channel configured for auto-posting")
            return
        
        # Only post published opportunities
        if opportunity.status != 'published':
            return
        
        bot = create_bot()
        success = post_opportunity_to_channel(bot, opportunity, channel_id, settings.webapp_url)
        
        if success:
            print(f"[admin] Auto-posted opportunity {opportunity.id} to channel")
        else:
            print(f"[admin] Failed to auto-post opportunity {opportunity.id}")
            
    except Exception as e:
        print(f"[admin] Error in auto_post_new_opportunity: {e}")
