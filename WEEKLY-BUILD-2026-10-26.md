# Weekly build — 2026-10-26 (Asia/Shanghai)

## Shipped locally (not pushed)
- `scripts/build.py` (stdlib only): data → api mirrors; regenerates `api/rankings.json` with active Featured + `homepageFeatured` (replaces the manual sync step in FEATURED-OPS).
- **Crawlable SEO pages:** `best/index.html` + 14 `best/<id>.html` — pre-rendered (no JS), canonical, OG, JSON-LD ItemList + BreadcrumbList, editorial Top 3 with why, real X captures only, Analytics script.
- **Agent JSON:** 14 `api/use-cases/<id>.json`; rankings `useCasePattern` now points at `/best/{id}.html`.
- `sitemap.xml` +15 `/best/` URLs (83 total, validated); `llms.txt`, `README.md`, `FEATURED-OPS.md` updated.
- Verified: editorial ranks/why unchanged vs previous rankings.json; HTML parses; local server returns 200.

## Blocker
- This box copy has **no `.git`** — nothing can be pushed from here. Local backlog vs prod: +6 tools (band, fx, humanlayer, cusp, freemilk, rea) + this build. Fix: let a cloud agent sync this folder into `leonwang2mini-beep/agents-use-cases` via PR (needs Leon's OK, same push approval).

## Not done
- No push, deploy, email, spend, Featured activation. Domain / W42 / Featured pricing still deferred.
