"""
Django signals for Opportuni opportunities app
Handles automatic channel posting when opportunities are published
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
import threading
import logging
import sys
from pathlib import Path

from .models import Opportunity

# Add telegram_bot module to Python path
project_root = Path(__file__).resolve().parents[3]  # Go up to project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


def async_post_to_telegram_channel(opportunity_id: int):
    """
    Asynchronously post opportunity to Telegram channel
    Runs in a separate thread to avoid blocking Django requests
    """
    try:
        # Import here to avoid circular imports and ensure Django is set up
        from telegram_bot.handlers.admin import auto_post_new_opportunity
        from .models import Opportunity
        
        opportunity = Opportunity.objects.get(id=opportunity_id)
        auto_post_new_opportunity(opportunity)
        
    except Exception as e:
        logger.error(f"Failed to post opportunity {opportunity_id} to Telegram: {e}")


# Remove the duplicate handler - we'll use only one consolidated handler below


# Track opportunity status changes to detect when status changes to 'published'
_opportunity_status_tracker = {}
_tracker_lock = threading.Lock()


@receiver(pre_save, sender=Opportunity)
def track_opportunity_status_change(sender, instance: Opportunity, **kwargs):
    """
    Track opportunity status changes before saving
    """
    if not instance.pk:
        # New opportunity, no need to track
        return
    
    try:
        old_instance = Opportunity.objects.get(pk=instance.pk)
        with _tracker_lock:
            _opportunity_status_tracker[instance.pk] = {
                'old_status': old_instance.status,
                'new_status': instance.status
            }
    except Opportunity.DoesNotExist:
        # New opportunity
        pass


@receiver(post_save, sender=Opportunity)
def opportunity_telegram_posting_handler(sender, instance: Opportunity, created: bool, **kwargs):
    """
    Single consolidated handler for posting opportunities to Telegram channel
    Handles both new published opportunities and status changes to published
    """
    # Only proceed if Telegram integration is enabled
    telegram_enabled = getattr(settings, 'TELEGRAM_BOT_ENABLED', False)
    if not telegram_enabled:
        return
    
    should_post = False
    log_message = ""
    
    if created:
        # Handle new opportunities
        if instance.status == 'published':
            should_post = True
            log_message = f"New published opportunity created: {instance.title} (ID: {instance.id})"
    else:
        # Handle status changes for existing opportunities
        with _tracker_lock:
            change_info = _opportunity_status_tracker.get(instance.pk)
            if change_info:
                # Clean up the tracker
                del _opportunity_status_tracker[instance.pk]
        
        if change_info:
            old_status = change_info['old_status']
            new_status = change_info['new_status']
            
            # If status changed to 'published' from any other status
            if old_status != 'published' and new_status == 'published':
                should_post = True
                log_message = f"Opportunity status changed to published: {instance.title} (ID: {instance.id})"
    
    # Post to Telegram if needed
    if should_post:
        logger.info(log_message)
        thread = threading.Thread(
            target=async_post_to_telegram_channel,
            args=(instance.id,),
            daemon=True
        )
        thread.start()


# Clean up tracker periodically to prevent memory leaks
def cleanup_status_tracker():
    """Clean up old entries in status tracker"""
    with _tracker_lock:
        # In a production environment, you might want to add timestamps
        # and clean up entries older than a certain time
        # For now, this is a placeholder
        pass
