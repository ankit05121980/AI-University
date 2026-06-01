# AI-University — agent notes

Enterprise AI knowledge publishing platform: Python engine (`engine/`), static portal (`web/`), catalog data (`data/`), demo corpus (`content/`).

## Cursor Cloud specific instructions

### Public portal (production)

- **URL:** https://ankit05121980.github.io/AI-University/web/
- **Source:** GitHub Pages, branch `main`, folder `/docs` (includes `docs/web/` copy of the portal).
- **Data/content in production:** loaded from jsDelivr (`@main` on this repo), not from Pages — same JSON/PDFs as local.
- **`docs/.nojekyll` is required** — without it, `/web/` returns 404 (Jekyll ignores static paths).

After changing `web/`, run `./scripts/sync-portal-to-docs.sh` and commit `docs/web/` before pushing.

### Vercel / Cloudflare (optional `*.vercel.app` / `*.pages.dev`)

- **Vercel:** import the repo at [vercel.com/new](https://vercel.com/new); root `vercel.json` redirects `/` → `/web`. Only the `web/` folder is needed (CDN serves data).
- **Cloudflare Pages:** connect the repo in the dashboard with build output **`web`**, or add repo secrets `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` and run the **Deploy to Cloudflare Pages** workflow manually.

### Full portal (local dev)

The library UI, search, viewer and downloads need the repo-root static server so `/data` and `/content` are served:

```bash
# from repository root (install engine deps once — see update script)
python3 serve.py
# → http://localhost:8000/web/
```

Custom port: `python3 serve.py 9000`.

### Engine (publish / catalog)

```bash
cd engine
python3 -m pip install -r requirements.txt
python3 -m aupub.cli catalog          # rebuild data/*.json (~seconds)
python3 -m aupub.cli publish --demo 12 # export demo books to content/
python3 -m aupub.cli stats
```

Publishing the full 528-book corpus is **many GB**; use `--demo`, `--category`, or `--ids` unless you intend a full run.

### Lint / test / build

| Action | Command | Notes |
|--------|---------|--------|
| Lint | — | No linter configured in-repo |
| Test | — | No test suite configured |
| Build | `python3 -m aupub.cli publish …` | Generates artefacts under `content/` |
| Dev | `python3 serve.py` | Portal + static assets |

### Gotchas

- After `pip install`, if CLI tools are missing from PATH, use `python3 -m aupub.cli` (not bare `aupub`).
- `serve.py` binds `0.0.0.0`; only port **8000** is assumed in docs unless you pass another port.
- Re-running `catalog` overwrites `data/library.json` and search index; committed catalog is already present for portal browsing without republishing.
