# Featured placements — ops playbook

**Scope:** activate a real paid placement. Demo seed rows stay `active: false` until replaced or Leon says otherwise. Rate card: `data/featured-rate-card.json` (PROPOSAL — not live).

## 1. Receive application

- Primary: mailto from `/submit.html` → intended `hello@agentsusecases.ai` (mailbox **not live** until domain email is provisioned).
- Confirm: tool exists in `data/tools.json` (or add via catalog review first), slot (`homepage` | `use-case`), dates, paid label copy, and Leon-approved price.

## 2. Configure placement

Edit `data/featured.json`:

- Prefer a new placement id (do not reuse demo `sponsor-demo-tool` for a real sponsor).
- Set `toolId`, optional `useCaseId` (required when `slot` is `use-case`), `slot`, `label` (`Featured` or `Sponsored`), `why`, `starts` / `ends`.
- Set **`active: true`** only when payment + Leon OK are confirmed.

## 3. Sync agent mirror

Run `python3 scripts/build.py` (mirrors data → api, rebuilds rankings incl. homepageFeatured, and the static /best pages). Manual fallback:

```bash
cp data/featured.json api/featured.json
```

## 4. Sync rankings homepageFeatured

`python3 scripts/build.py` rebuilds `api/rankings.json` from active placements (`meta.homepageFeatured` and each use case’s `featured[]`) and writes the crawlable `/best/` pages. Editorial ranks stay in `data/use-cases.json`. Site UI still loads `data/featured.json` via `js/app.js` and filters `active`.

Manual fallback if you are not running the script:

1. Open `api/rankings.json`.
2. Set `meta.homepageFeatured` to an array of active homepage placements (or `[]` if none). Keep `editorial[]` and `featured[]` **separate** per use case.
3. For each use-case block: put active `slot: use-case` placements for that `useCaseId` into that block’s `featured[]` (empty array if none).
4. Bump `meta.updated` to today’s date.

## 5. Ship

- Commit + push `main` only after Leon approves the push (auto-deploys on Vercel when GitHub is connected).
- Do not activate demo placements to “look busy.”
- Do not quote rates externally until Leon approves `data/featured-rate-card.json`.

## Related

- `data/featured.json` / `api/featured.json`
- `data/featured-rate-card.json` (proposal)
- `README.md` → Featured config
- `about.html` → Featured vs editorial
