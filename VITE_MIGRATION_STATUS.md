# Vite Migration Status

We are in the process of migrating the frontend to use the Vite build system.

## Completed Steps:

1.  **Vite Installed:** `vite` has been added as a dev dependency to the root `package.json`.
2.  **Vite Configured:** A `vite.config.js` file has been created in the project root, configured for a multi-page application.
3.  **API Refactoring:** `assets/js/api.js` has been updated with centralized error handling.
4.  **State Management Refactoring:** `assets/js/opportunity-detail.js` was refactored to use a more robust state-driven pattern.
5.  **HTML Files Updated (Partial):**
    - `index.html`, `dashboard.html`, `opportunity-detail.html`, and `applications.html` have been updated.
    - The inline script from `applications.html` was moved to `assets/js/applications.js`.
    - The inline script from `profile.html` was moved to `assets/js/profile.js`.

## Current Task:

- **File:** `opportuni_frontend/profile.html`
- **Action:** The inline JavaScript has been successfully extracted to `assets/js/profile.js`. The immediate next step is to remove the old `<script>` blocks from `profile.html` and replace them with a single `<script type="module" src="/assets/js/profile.js"></script>`.

## Next Steps:

1.  Complete the modification of `profile.html`.
2.  Continue the same refactoring process for all remaining HTML files.
3.  Update the root `.gitignore` file to exclude `/node_modules` and `/dist`.
4.  Add `dev` and `build` scripts to the root `package.json` for running Vite.
5.  Provide final instructions on how to use the new Vite development server.
