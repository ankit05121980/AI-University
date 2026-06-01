# AI-University — agent notes

Enterprise AI knowledge publishing platform: Python engine (`engine/`), static portal (`web/`), catalog data (`data/`), demo corpus (`content/`).

## Cursor Cloud specific instructions

### Public portal (production)

- **Primary (GitHub Pages):** https://ankit05121980.github.io/AI-University/ — run `./scripts/sync-portal-to-docs.sh` then push `docs/` (legacy Pages: `main` + `/docs`).
- **Cloudflare Pages:** https://ai-university.pages.dev — `./scripts/deploy-cloudflare.sh` or **Deploy to Cloudflare Pages** workflow (requires `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` repo secrets).
- **Data/content on Cloudflare/GitHub hosts:** jsDelivr (`@main`), not bundled in the Pages artifact — same JSON/PDFs as local.

After changing `web/`, run `./scripts/sync-portal-to-docs.sh` if you also publish to GitHub Pages.

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
