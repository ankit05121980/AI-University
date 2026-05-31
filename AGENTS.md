# AI-University

Repository for the **AI-University** project. As of the initial commit, the repo contains only a root `README.md` — no application source, dependency manifests, or service definitions yet.

## Cursor Cloud specific instructions

### Repository state

This is a **placeholder / greenfield** repository. There are currently:

- No `package.json`, `pyproject.toml`, `requirements.txt`, or lockfiles
- No `docker-compose`, Dockerfile, or `.devcontainer` configuration
- No lint, test, build, or dev-server scripts
- No runnable services (frontend, API, database, etc.)

When application code and manifests are added, re-run environment discovery and extend this section with service startup commands and gotchas.

### VM update script behavior

The startup update script is intentionally a no-op (`true`) because there are no project dependencies to refresh. After manifests land (e.g. `package.json`), change the update script to the appropriate install command (`npm ci`, `pnpm install`, `uv sync`, etc.) via the Cloud Agent environment settings.

### Development toolchain (pre-installed on Cloud VMs)

These tools are available for future work; nothing in-repo consumes them yet:

| Tool | Notes |
|------|--------|
| **Git** | Repo root is `/workspace`; default branch `main` |
| **Node.js** | Via nvm (v22.x on current images); use when `package.json` appears |
| **Python** | System `python3` when Python manifests appear |
| **Docker** | May require extra setup in nested VM environments; not used by this repo yet |

### Lint / test / build / run

Not applicable until the project adds scripts and services. Typical commands to add later:

- **Lint:** e.g. `npm run lint` or `ruff check .`
- **Test:** e.g. `npm test` or `pytest`
- **Dev:** e.g. `npm run dev` or `docker compose up`

Do **not** add service startup, migrations, or test runs to the VM update script — only dependency refresh belongs there.

### Getting started (when code is added)

1. Add dependency manifests and a `README` with setup steps.
2. Install dependencies using the repo’s package manager.
3. Start required services per `docker-compose` or README (database, API, web).
4. Update this file’s **Cursor Cloud specific instructions** with non-obvious startup caveats (ports, env vars, hot-reload quirks).
