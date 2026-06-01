#!/usr/bin/env bash
# Deploy the portal UI to Cloudflare Pages (data/content load from jsDelivr in production).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

: "${CLOUDFLARE_API_TOKEN:?Set CLOUDFLARE_API_TOKEN (Pages Edit permission)}"
: "${CLOUDFLARE_ACCOUNT_ID:?Set CLOUDFLARE_ACCOUNT_ID (Cloudflare dashboard sidebar)}"

export CLOUDFLARE_API_TOKEN
export CLOUDFLARE_ACCOUNT_ID

PROJECT="${CLOUDFLARE_PAGES_PROJECT:-ai-university}"

echo "Ensuring Pages project: ${PROJECT}"
npx wrangler@4 pages project create "${PROJECT}" --production-branch=main 2>/dev/null || true

echo "Deploying ./web ..."
npx wrangler@4 pages deploy web \
  --project-name="${PROJECT}" \
  --branch=main \
  --commit-dirty=true

echo ""
echo "Portal URL (may take ~1 min to propagate):"
echo "  https://${PROJECT}.pages.dev"
