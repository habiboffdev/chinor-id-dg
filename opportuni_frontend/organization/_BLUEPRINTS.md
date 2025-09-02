# Organization Frontend Blueprints (Brand-first, no Tailwind)

Purpose: define page structure, UX rules, data contracts, and brand usage to implement reliably without regressions.

## Brand & System
- Dark-first: add `class="theme-opportuni"` on `<body>` and include `../assets/css/theme.css` and `../assets/css/styles.css`.
- Typography: Space Grotesk for headings, Inter for text (configured in theme.css).
- Colors: use CSS variables only (no hex in markup). Primary accents: `--accent-2` (violet), CTA: `--accent-1` (lime) when appropriate; cards use `--ink-800` with `--slate-400` borders.
- Buttons: use `.btn-primary` (defined in theme.css) or add `.btn` variants in an org CSS if needed.
- Motion: 120–220ms, subtle; focus ring via `--focus-ring`. Avoid large gradients.

## Universal Org Navbar (shared across pages)
Slots:
- Brand wordmark (left) linking to `/organization/dashboard.html`.
- Primary nav: Dashboard, Opportunities, Applications, Students, Communications, Profile.
- Right-side: Notifications bell (unread badge), user menu (org name, dropdown: Profile, Settings, Sign out).

Behavior:
- Sticky top, backdrop blur on scroll (via `navbar--scrolled` class toggled by JS).
- Accessible: role="navigation", current page indicated with `aria-current="page"` on active link.
- Keyboard: Tab focus visible; dropdown toggles with Enter/Space/Escape.

Implementation: HTML rendered by `navbar.js` into a placeholder `<div id="org-navbar"></div>`. No Tailwind; plain semantic HTML + brand classes.

## Page Blueprints

### 1) Dashboard (`organization/dashboard.html`)
- Sections: Quick actions (Create Opportunity, Review Applications, Find Students, Send Message), Stats (Applications total/pending/accepted, Active opportunities), Recent Applications list, Sidebar (Active Opportunities), Chart placeholder.
- Data: 
  - GET /api/organizations/dashboard/ (or compose from: applications/stats, opportunities/stats)
  - GET /api/applications/?limit=5&ordering=-created_at
  - GET /api/opportunities/?owner=me&status=active&limit=5
- Interactions: open Create Opportunity modal; defer heavy creation flow until Opportunities page exists.

### 2) Opportunities (org) (`organization/opportunities.html`)
- List of org-owned opportunities with filters (status, type), search, create button.
- Data:
  - GET /api/opportunities/?owner=me&search=&status=&type=&page=
  - POST /api/opportunities/ (create)
  - PUT /api/opportunities/{id}/ (update)
  - POST /api/opportunities/{id}/publish|close/

### 3) Applications (`organization/applications.html`)
- Filters (search, status, opportunity, date range), table with applicant, opportunity, applied date, status, actions; pagination; export CSV.
- Data:
  - GET /api/applications/?search=&status=&opportunity=&date_from=&date_to=&page=
  - GET /api/applications/stats/
  - POST /api/applications/bulk-update/ { ids:[], status }
  - PUT /api/applications/{id}/ (status updates)

### 4) Students (`organization/students.html`)
- Directory with filters (major, year, status), stats, modal view, invite flow.
- Data: 
  - GET /api/students/?search=&major=&year=&status=&page= (verify backend; otherwise expose org-filtered list endpoint)
  - POST /api/organizations/invite-member/ or dedicated invite-students endpoint (TBD)
  - Stats endpoint TBD or derive from list.

### 5) Communications (`organization/communications.html`)
- Conversation list + chat pane, compose modal.
- Data (current backend provides email templates and messages list):
  - GET /api/communications/messages/?participant=student_id
  - POST /api/communications/messages/ { to: student_id, subject?, content }
  - Consider grouping messages into conversations on frontend until server supports conversations.

### 6) Profile (`organization/profile.html`)
- Form sections: Organization Info, Contact, Web/Social, Address, Description, Logo upload, Notification settings.
- Data:
  - GET/PUT /api/organizations/profile/
  - POST /api/organizations/upload-logo/

## UX Guardrails (God-level rules)
- Escape or sanitize all dynamic text via Utils.escapeHTML or Utils.sanitizeHTML.
- Optimistic UI only with visible fallback; always show loading states and empty states with next-step guidance.
- Keyboard support: focus trap for modals; Esc to close; restore focus; ARIA roles.
- Pagination resilience: if count/page-size missing, still render sane navigation.
- Network errors: show actionable toasts; never fail silently.
- No inline styles for colors; use CSS variables; avoid per-page color overrides.

## Frontend–Backend Contract Summary
- Organizations: `/organizations/profile/`, `/organizations/dashboard/`, `/organizations/members/`, `/organizations/upload-logo/`, `/organizations/invite-member/`.
- Applications: `/applications/`, `/applications/stats/`, `/applications/bulk-update/`, `/applications/{id}/`.
- Opportunities: `/opportunities/`, `/opportunities/search/`, `/opportunities/featured/`, `/opportunities/stats/`, `/opportunities/{id}/publish|close/`.
- Communications: `/communications/messages/` (+ templates). Conversations abstraction is frontend for now unless backend adds it.
