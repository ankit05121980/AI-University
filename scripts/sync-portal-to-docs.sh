#!/usr/bin/env bash
# Publish the portal UI to docs/ for GitHub Pages (site root = /AI-University/).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="$ROOT/docs"
mkdir -p "$DOCS"
# Keep only static portal assets at docs root (not docs/web/).
find "$DOCS" -mindepth 1 -maxdepth 1 ! -name '.gitkeep' -exec rm -rf {} +
cp -a "$ROOT/web/." "$DOCS/"
touch "$DOCS/.nojekyll"
echo "Synced web/ -> docs/ (GitHub Pages root)"
