# Weekly build — 2026-11-09 (Asia/Shanghai)

## Shipped locally (not pushed)
- New `scripts/build_tools.py` (stdlib, auto-run at the end of `scripts/build.py`):
  - 60 crawlable `tools/<id>.html` pages (no JS): tagline, pricing, official link, every use case with editorial rank + why, real X signals only, canonical/OG, JSON-LD SoftwareApplication + BreadcrumbList.
  - `tools/index.html` A–Z index.
  - 60 `api/tools/<id>.json` per-tool resolved JSON for agents.
  - sitemap: the query-string `tool.html?id=` entries replaced by `/tools/<id>.html` + index (100 URLs, XML valid). Idempotent, so the daily routine's additions get normalized on each build.
- `/best/*` pages now link to the static tool pages; nav gains "Tools".
- `llms.txt` points tool links at `/tools/<id>.html` and documents `/api/tools/{id}.json`; README updated.
- Checked: 0 broken relative links across best/ + tools/, every sitemap URL maps to a file.
- Backup of pre-build folder: /workspace/_scratch/auc-backup-2026-11-09-weekly

## Still blocked
- Box copy has no `.git`; push needs Leon's approval (cloud agent PR to leonwang2mini-beep/agents-use-cases). Local backlog vs prod: catalog 60 vs 50 + this build.
- No email, spend, or Featured activation.
