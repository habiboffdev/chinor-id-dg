# Theming Migration Guide (Dark/Light Token System)

## Overview
We are migrating from ad-hoc dark-first CSS + light-mode override files to a professional multi-theme token architecture.

### Goals
- Single source of truth for colors via semantic tokens.
- Theme switch = attribute flip (`data-theme="light"|"dark"`).
- Remove `light-mode-overrides.css` by absorbing into semantic layer.
- Forbid raw hex usage outside token files.

### Token Layers
1. `tokens.base.css` – Raw brand & neutral scales, spacing, radii, motion.
2. `tokens.dark.css` / `tokens.light.css` – Map semantic variables (`--color-*`) per theme.
3. Component CSS uses only semantic tokens (never raw or base scale directly).

### Semantic Token Categories
| Purpose        | Token Examples                                   |
|----------------|--------------------------------------------------|
| Backgrounds    | `--color-bg-app`, `--color-bg-surface(-alt)`      |
| Elevation/Inks | `--color-bg-elevated`, `--color-bg-inset`         |
| Text           | `--color-text-primary/secondary/muted/inverted`  |
| Borders        | `--color-border`, `--color-border-strong`        |
| Accents        | `--color-accent-primary/secondary/tertiary/promo`|
| State          | `--color-state-success/warning/danger`           |
| Shadow/Focus   | `--shadow-focus`, `--shadow-elevation-*`         |

### Bridge Aliases (Temporary)
Legacy vars (e.g. `--bg-surface-1`, `--text-primary`) are still assigned in theme mapping for gradual migration. Remove after all CSS references are updated.

## Migration Steps
1. (DONE) Introduce token files & attribute switching.
2. (IN PROGRESS) Add token links to all HTML pages.
3. Refactor core components (buttons, cards) → semantic tokens.
4. Replace hard-coded colors in remaining CSS files:
   - `styles.css`
   - `profile.css`
   - `org.css`, `org-dashboard.css`
   - `opportunity-detail.css`, `opportunity-create.css`, `wizard-create.css`
5. Collapse `light-mode-overrides.css` – remove blocks whose selectors now resolve via tokens.
6. Remove legacy color variables and `.light-mode` class usage.
7. Enforce via `scripts/check_raw_colors.sh` in CI/pre-commit.

## Refactor Pattern
Before:
```css
.card { background: var(--ink-800); border: 1px solid var(--slate-400); color: var(--mist-200); }
```
After:
```css
.card { background: var(--color-bg-surface-alt); border: 1px solid var(--color-border); color: var(--color-text-primary); }
```

### Interactive States
Instead of inline rgba blends:
```css
.btn--ghost:hover { background: rgba(255,255,255,0.03); }
```
Use token or color-mix:
```css
.btn--ghost:hover { background: color-mix(in srgb, var(--color-bg-surface-alt) 60%, transparent); }
```

## Lint Guard
`scripts/check_raw_colors.sh` reports raw hex outside allowed files. Integrate into CI.

## Deleting `light-mode-overrides.css`
- Track remaining selectors still needed.
- For each rule, ensure underlying class uses semantic tokens, then remove override block.
- When file shrinks below ~10% of original, inline remaining transitional rules into components (if still relevant) and delete file.

## Removal of Legacy `.light-mode`
- When no selectors depend on `.light-mode`, search & remove `body.theme-opportuni.light-mode` occurrences.
- Simplify JS: stop toggling the class, rely solely on `data-theme`.

## Future Enhancements
- Introduce cascade layers (`@layer tokens, theme, components` – already partially used in token files).
- Add automated contrast tests (Node script comparing text vs surface tokens for WCAG AA).
- Provide design token export (JSON) for future mobile/web parity.

## Tracking Table (Update as you progress)
| File                     | Raw Colors Remaining? | Migrated % | Notes |
|--------------------------|-----------------------|------------|-------|
| components.css           | Low                   | 90%        | Buttons & cards done |
| styles.css               | High                  | 0%         | Needs full pass |
| profile.css              | High                  | 0%         | Many inline accent variants |
| org.css                  | Medium                | 0%         | |
| org-dashboard.css        | Medium                | 0%         | |
| opportunity-detail.css   | High                  | 0%         | Duplicated palette start |
| opportunity-create.css   | Medium                | 0%         | |
| wizard-create.css        | Medium                | 0%         | |
| light-mode-overrides.css | High                  | 0%         | Will be deleted |

Update this table each commit.

## Quick Commands
Run guard:
```bash
./scripts/check_raw_colors.sh
```

Search for legacy usage:
```bash
grep -R "light-mode" opportuni_frontend/assets/css
```

## Questions
Ping design if a semantic token feels missing—do NOT introduce ad-hoc new variables; extend semantic set intentionally.
