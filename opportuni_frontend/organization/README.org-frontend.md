# Organization Frontend Refactor Notes

- Universal navbar: include `theme.css`, `org.css`, `layout-shim.css`, and `org-navbar.js`, then place `<div id="org-navbar"></div>` at the top of `<body>`. The navbar mounts automatically on DOMContentLoaded or via `OrgNavbar.mount()`.
- No Tailwind: Tailwind CDN has been removed. A tiny `layout-shim.css` preserves a few utility classes used in pages. Replace remaining utility classes gradually with semantic CSS.
- Brand: Wrap pages with `body.theme-opportuni` to enable brand tokens and dark-first palette.

Local serve
- If 8080 is busy, run on 8082.

```bash
cd opportuni_frontend
python3 -m http.server 8082
```

Pages updated
- dashboard.html, applications.html, students.html, communications.html, profile.html now use the universal navbar and brand styles.
- opportunities.html added as a stub to avoid 404s from navbar links.

Known follow-ups
- Replace remaining utility classes with semantic classes and consolidate duplicated inline styles.
- Align API method names to backend (e.g., organizations.getStudents()) or add wrappers in `api.js`.