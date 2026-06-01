#!/usr/bin/env bash
# Copy the portal UI into docs/web for GitHub Pages (data/content served via jsDelivr in production).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -rf "$ROOT/docs/web"
cp -a "$ROOT/web" "$ROOT/docs/web"
echo "Synced web/ -> docs/web/"
