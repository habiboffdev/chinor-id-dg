# Telegram Bot Strategy (MVP)

Goals
- Make MVP accessible where users already are (Telegram).
- Minimal friction: sign-up/login via Telegram and web app button fallback.
- Keep scope tight: Student, Organization, Admin flows as thin wrappers over existing backend.

Principles
- Modular code: config, markups, i18n, handlers; no monolithic bot.py.
- Reuse Django via REST first; ORM only where trivial and safe.
- i18n upfront (en/ru/uz) per project brief; store user language in memory initially.
- Keep long-running state outside process later (Redis/DB), but start simple.

Roadmap
1) Student
   - /start -> language choice -> main menu.
   - Commands: Browse Opportunities (open web app), My Applications (link), Profile (link).
   - Quick apply via inline steps (collect name/email/attachment) for MVP.
   - Link Telegram user to backend user: save telegram_id in accounts (add field + endpoint) or use login widget.

2) Organization
   - Post Opportunity: guide through few-step dialog; publish to org channel via bot if permitted.
   - Web App button for full create form.
   - Minimal moderation checks.

3) Admin
   - Broadcast new opportunities to channel (SMM rules).
   - Basic sanity commands: /stats, /ping.

Backend touchpoints
- accounts: add optional fields for telegram_id, language.
- opportunities: list/search endpoints for simple browsing.
- applications: create application endpoint that accepts telegram-sourced submissions.

Tech choices
- pyTelegramBotAPI (TeleBot) for simplicity.
- Polling during development; webhook after deploy under Nginx.
- JWT auth via existing endpoints for REST path; or direct ORM with setup_django() for simple reads.

Next steps
- Add accounts fields + DRF endpoints to link Telegram IDs.
- Implement REST client helpers in bot to call backend.
- Replace in-memory state with Redis if needed.
