# Telegram Bot Channel Administration

This document describes the channel administration functionality for the Opportuni Telegram Bot.

## Features

### Automatic Channel Posting
- Automatically posts new opportunities to a Telegram channel when they are published
- Uses Django signals to detect when opportunities are created or status changes to 'published'
- Posts are formatted with rich information including title, organization, location, deadline, etc.
- Includes inline buttons for applying and viewing organization profile

### Admin Commands
- `/admin` - Access admin panel (requires admin authorization)
- `/channel_post` - Manually post latest opportunities to channel
- Admin panel includes:
  - 📊 Statistics - View bot usage statistics
  - 📢 Broadcast - Send broadcasts (coming soon)
  - 🧪 Test Channel - Send test message to channel

### Management Commands
- `python manage.py run_telegram_bot` - Run the bot from Django
- `python manage.py test_telegram_channel` - Test channel posting functionality

## Configuration

### Environment Variables
Add these to your `.env` files:

```bash
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBAPP_URL=https://yourdomain.com
TELEGRAM_CHANNEL_URL=https://t.me/opportuni_channel
TELEGRAM_CHANNEL_ID=@opportuni_channel  # or -1001234567890
TELEGRAM_ADMIN_IDS=123456789,987654321  # Comma-separated admin user IDs
TELEGRAM_BOT_ENABLED=true
```

### Django Settings
The following settings are automatically loaded from environment variables:
- `TELEGRAM_BOT_ENABLED` - Enable/disable Telegram integration
- `TELEGRAM_CHANNEL_ID` - Channel ID for posting opportunities
- `TELEGRAM_CHANNEL_URL` - Channel URL for user links
- `TELEGRAM_WEBAPP_URL` - Web app URL for buttons
- `TELEGRAM_ADMIN_IDS` - List of admin user IDs

## Setup

### 1. Bot Configuration
1. Create a bot with @BotFather on Telegram
2. Get your bot token and add it to `.env`
3. Create a channel and add your bot as an administrator
4. Get the channel ID (use @userinfobot or check bot logs)

### 2. Admin Setup
1. Get your Telegram user ID (message @userinfobot)
2. Add your user ID to `TELEGRAM_ADMIN_IDS` in `.env`
3. Restart the bot
4. Send `/admin` to access admin panel

### 3. Channel Permissions
Your bot needs these permissions in the channel:
- Post messages
- Edit messages
- Add web page previews

## Channel Post Format

When an opportunity is published, the bot automatically posts a formatted message:

```
🚀 **Software Developer Internship**
🏢 Tech Company Inc

💼 **Type:** Internship
📍 **Location:** San Francisco, CA (Remote)

📋 **Description:**
Join our team for an exciting internship opportunity...

🎓 **Major:** Computer Science
📅 **Graduation Year:** 2024-2026
📊 **Min GPA:** 3.0
💵 **Compensation:** $20/hour

⏰ **Application Deadline:** December 31, 2024
👥 **Applications:** 15/50

🔗 **Apply now on Opportuni!**

[📝 Apply Now] [🏢 View Organization]
```

## Usage

### Automatic Posting
Once configured, opportunities are automatically posted when:
1. A new opportunity is created with status 'published'
2. An existing opportunity's status changes to 'published'

### Manual Posting
Admins can manually post opportunities using:
```bash
# Post latest published opportunities
python manage.py test_telegram_channel --latest

# Post specific opportunity
python manage.py test_telegram_channel --opportunity-id 123
```

Or use the `/channel_post` command in Telegram.

### Admin Panel
Send `/admin` to the bot to access:
- View statistics about users, opportunities, applications
- Test channel connectivity
- Access future broadcast features

## SMM Rules and Best Practices

### Posting Frequency
- Maximum 5 opportunities per day to avoid spam
- Group similar opportunities when possible
- Schedule posts during peak hours (9 AM - 6 PM local time)

### Content Guidelines
- Keep descriptions under 300 characters in channel posts
- Use emojis to make posts more engaging
- Include clear call-to-action buttons
- Ensure all information is accurate and up-to-date

### Channel Management
- Pin important announcements
- Use channel description to explain the purpose
- Monitor engagement and adjust posting strategy
- Respond to comments and questions promptly

## Troubleshooting

### Common Issues

1. **Bot not posting to channel**
   - Check if bot is admin in channel
   - Verify `TELEGRAM_CHANNEL_ID` is correct
   - Ensure `TELEGRAM_BOT_ENABLED=true`

2. **Admin commands not working**
   - Verify your user ID is in `TELEGRAM_ADMIN_IDS`
   - Check if Django is properly configured
   - Restart the bot after configuration changes

3. **Django signals not firing**
   - Ensure `apps.opportunities.signals` is imported
   - Check Django logs for errors
   - Verify `TELEGRAM_BOT_ENABLED=true` in Django settings

### Logs
Check logs for debugging:
```bash
# Django logs
tail -f opportuni_backend/logs/django.log

# Bot logs (if configured)
tail -f telegram_bot/bot.log
```

## Development

### Testing
```bash
# Test channel posting
python manage.py test_telegram_channel --latest

# Run bot in development
python manage.py run_telegram_bot

# Test specific features
python -m pytest tests/test_telegram_channel.py
```

### Adding New Features
1. Follow the modular structure in `telegram_bot/handlers/`
2. Add translations to `telegram_bot/i18n.py`
3. Update admin panel for new functionality
4. Add management commands for testing

## Security

### Admin Authorization
- Only users in `TELEGRAM_ADMIN_IDS` can access admin features
- Admin IDs are stored securely in environment variables
- Commands are validated before execution

### Channel Security
- Bot token should be kept secret
- Use private channels for sensitive content
- Monitor bot permissions regularly
- Implement rate limiting for API calls

## Future Enhancements

### Planned Features
- Broadcast messaging to all bot users
- Scheduled opportunity posting
- Analytics and engagement tracking
- Multi-language channel support
- Custom posting templates
- Integration with organization dashboards

### Webhook Support
For production deployment, consider using webhooks instead of polling:
```python
# In telegram_bot/bot.py
def run_webhook():
    # Implement webhook integration
    pass
```
