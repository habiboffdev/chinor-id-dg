#!/usr/bin/env bash
# Guard script: detect disallowed raw hex colors in CSS outside token/theme files.
# Allowed files pattern: tokens.*.css, theme.css (temporary), semantic-theme.css (temporary)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

violations=$(grep -RInE "#[0-9a-fA-F]{3,8}" opportuni_frontend/assets/css \
  | grep -v -E "tokens.(base|dark|light).css" \
  | grep -v -E "/theme.css" \
  | grep -v -E "/semantic-theme.css" \
  | grep -v -E "/light-mode-overrides.css" || true)

if [[ -n "$violations" ]]; then
  echo "Raw hex color literals detected (migration needed):" >&2
  echo "$violations" >&2
  exit 1
else
  echo "No disallowed raw hex colors found."
fi
