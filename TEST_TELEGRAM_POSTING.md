# Telegram Channel Posting Tests

This directory contains comprehensive tests for the Telegram channel posting functionality.

## Test Files

### 1. `test_telegram_posting.py` (Project Root)
Comprehensive integration test that can be run independently.

```bash
# Run the comprehensive test
cd /path/to/project
python test_telegram_posting.py
```

**Features:**
- Tests opportunity message formatting
- Tests direct channel posting function
- Tests Django signal integration
- Tests automatic posting for new opportunities
- Tests status change posting (draft → published)
- Tests error handling
- Tests inline keyboard generation
- Uses mock bot to avoid spam during testing

### 2. `test_telegram_posting.py` (Management Command)
Django management command for testing within the Django environment.

```bash
# Test with mock bot (recommended for development)
python manage.py test_telegram_posting --mock-bot

# Test with real bot (only if channel is configured)
python manage.py test_telegram_posting

# Test and cleanup data automatically
python manage.py test_telegram_posting --mock-bot --cleanup
```

**Features:**
- Integrates with Django's testing framework
- Can use real or mock Telegram bot
- Tests complete flow from opportunity creation to channel posting
- Verifies Django signals work correctly
- Option to cleanup test data automatically

## What the Tests Verify

### 1. **Message Formatting**
- ✅ Opportunity details are properly formatted
- ✅ All required fields are included (title, organization, type, location, etc.)
- ✅ Emojis and formatting are applied correctly
- ✅ Long descriptions are truncated appropriately

### 2. **Channel Posting Function**
- ✅ `post_opportunity_to_channel()` function works
- ✅ Correct parameters are passed to Telegram API
- ✅ Bot sends message to correct channel ID
- ✅ Inline keyboards are generated properly

### 3. **Django Signal Integration**
- ✅ Signals fire when new opportunities are created
- ✅ Signals fire when opportunity status changes to 'published'
- ✅ Signals don't fire for draft opportunities
- ✅ Background thread processing works

### 4. **Automatic Posting Scenarios**
- ✅ New opportunity created with 'published' status → auto-posted
- ✅ Existing opportunity status changed to 'published' → auto-posted
- ✅ Draft opportunity created → not posted
- ✅ Non-published status changes → not posted

### 5. **Error Handling**
- ✅ Network errors don't crash the system
- ✅ Invalid opportunities are handled gracefully
- ✅ Missing configuration is detected
- ✅ Fallback behavior works correctly

### 6. **UI Components**
- ✅ Inline keyboards with "Apply Now" button
- ✅ "View Organization" button links correctly
- ✅ Buttons use correct URLs from configuration

## Test Outputs

### Success Example
```
🤖 Starting Telegram Channel Posting Tests
============================================================
✅ Create Test Organization: Created/found org ID 1
✅ Opportunity Formatting: All required elements present
✅ Channel Posting Function: Posted to @test_channel
✅ Signal Integration - Draft: No posting for draft status
✅ Signal Integration - Published: Signal triggered posting
✅ New Opportunity Creation: New published opportunity triggered posting
✅ Error Handling: Properly handled posting error
✅ Keyboard Generation: Generated keyboard with 2 rows

============================================================
📊 TEST SUMMARY:
✅ PASS Create Test Organization: Created/found org ID 1
✅ PASS Opportunity Formatting: All required elements present
✅ PASS Channel Posting Function: Posted to @test_channel
✅ PASS Signal Integration - Draft: No posting for draft status
✅ PASS Signal Integration - Published: Signal triggered posting
✅ PASS New Opportunity Creation: New published opportunity triggered posting
✅ PASS Error Handling: Properly handled posting error
✅ PASS Keyboard Generation: Generated keyboard with 2 rows

🎯 Results: 8/8 tests passed
🎉 ALL TESTS PASSED! Telegram posting is working correctly.
📈 Success Rate: 100.0%
```

### Failure Example
```
❌ FAIL Channel Posting Function: send_message not called
❌ FAIL Signal Integration - Published: Signal did not trigger posting
⚠️  Some tests failed. Check the output above for details.
📈 Success Rate: 75.0%
```

## Running Tests

### Prerequisites
1. Django environment set up and working
2. Telegram bot token configured (for real tests)
3. Virtual environment activated

### Mock Testing (Recommended)
```bash
# Use mock bot to avoid actual Telegram API calls
python manage.py test_telegram_posting --mock-bot
```

### Real Bot Testing
```bash
# Make sure your .env is configured with:
# BOT_TOKEN=your_real_bot_token
# TELEGRAM_CHANNEL_ID=@your_test_channel
# TELEGRAM_BOT_ENABLED=true

python manage.py test_telegram_posting
```

### Configuration Check
```bash
# The command will check your configuration first:
python manage.py test_telegram_posting --mock-bot

# Output will show:
# ✅ Bot token configured
# ✅ Telegram bot enabled  
# ✅ Channel ID: @your_channel
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   ModuleNotFoundError: No module named 'apps.opportunities'
   ```
   - Make sure you're running from the correct directory
   - Ensure Django environment is properly set up

2. **Configuration Errors**
   ```bash
   ❌ TELEGRAM_BOT_TOKEN not configured
   ```
   - Copy `.env.example` to `.env`
   - Set your bot token and channel configuration

3. **Signal Not Firing**
   ```bash
   ❌ Signal did not trigger posting
   ```
   - Check if `TELEGRAM_BOT_ENABLED=true` in settings
   - Verify signals are imported in `apps.py`
   - Make sure opportunity status is 'published'

4. **Channel Posting Fails**
   ```bash
   ❌ Posted to @channel returned False
   ```
   - Verify bot is admin in the channel
   - Check channel ID format (@username or -1001234567890)
   - Ensure bot has posting permissions

### Debug Mode
Add debugging to see what's happening:
```python
# In your .env
DEBUG=True

# Check Django logs
tail -f opportuni_backend/logs/django.log
```

## Integration with CI/CD

You can integrate these tests into your CI/CD pipeline:

```yaml
# In your GitHub Actions or similar
- name: Test Telegram Posting
  run: |
    cd opportuni_backend
    python manage.py test_telegram_posting --mock-bot
  env:
    TELEGRAM_BOT_ENABLED: true
    BOT_TOKEN: "fake_token_for_testing"
```

The tests are designed to work in both development and CI environments.
