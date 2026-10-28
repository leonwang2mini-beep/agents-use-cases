# Agents Use Cases

Static v1 site: AI tools ranked by use case for vibe coders, builders, and agents.

## Preview

```bash
cd /workspace/agents-use-cases
python3 -m http.server 8765
# open http://127.0.0.1:8765/
```

Do not open `index.html` via `file://` — fetch() needs HTTP.

## SEO & agents

| File | Purpose |
|------|---------|
| `robots.txt` | Allow crawl; points at sitemap |
| `sitemap.xml` | Home, about, submit, use cases, tools, API, llms.txt |
| `llms.txt` | LLM / agent entry map |
| `favicon.svg` | Site icon |
| `api/*.json` | Stable agent JSON (prefer `/api/rankings.json`) |

Canonical host: `https://agents-use-cases.vercel.app`

**Deploy:** replace domain in canonical/OG/sitemap/llms/`api` meta if using `*.vercel.app` until DNS is ready.

## Data

| File | Purpose |
|------|---------|
| `data/tools.json` | Tool catalog (UI source) |
| `data/use-cases.json` | Use cases + editorial rankings + why |
| `data/featured.json` | Paid Featured/Sponsored placements |
| `data/x-signals.json` | Demo X discussion cards |
| `api/*.json` | Agent-facing mirrors (+ schema meta) |

## Featured config

Edit `data/featured.json`, set `active: true`, then keep api in sync:

```bash
cp data/featured.json api/featured.json
```

## Pages

- `index.html` — home
- `use-case.html?id=research` — use case detail
- `tool.html?id=cursor` — tool detail
- `submit.html` — Featured / new tool form (mailto + coming soon)
- `about.html` — methodology + agent docs


## Deploy (Vercel)

Static site. `vercel.json` sets JSON CORS/cache for `/api/*.json`.
`404.html` is the custom not-found page.

```bash
# from this directory, after GitHub push
vercel --prod
# or connect the repo in the Vercel dashboard
```

Demo Featured placements are `active: false` until a real sponsor is live.

## Build (static pages + agent JSON)

```bash
python3 scripts/build.py
```

Regenerates `api/*` mirrors from `data/`, `api/rankings.json` (incl. `homepageFeatured` from active placements),
`api/use-cases/<id>.json`, crawlable `best/<id>.html` + `best/index.html`, and the `/best/` sitemap entries.
Run it after any data edit, before pushing.
