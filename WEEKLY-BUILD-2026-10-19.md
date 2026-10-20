# Weekly build — 2026-10-19 (Asia/Shanghai)

## Shipped locally (not pushed)

### Newsletter draft structure
- `newsletter/README.md` — draft → Resend flow; **never send without Leon approval**
- `newsletter/schema.json` — weekly issue JSON Schema
- `newsletter/drafts/2026-W42.json` + `.md` — concrete W42 draft (coding-agents refresh, soft launch, Featured closed)
- `api/newsletter.json` — public index (`issues: []`); drafts pointer private
- `llms.txt`, `sitemap.xml`, `about.html` — mention `/api/newsletter.json`; footer signup = waitlist

### Featured ops (no live ads)
- `data/featured-rate-card.json` — **PROPOSAL** USD monthly starter pricing (not live)
- `FEATURED-OPS.md` — mailto → `data/featured.json` active → `cp` to `api/featured.json` → manual `api/rankings.json` homepageFeatured sync (no rebuild script exists)
- Demo placements in `data/featured.json` left inactive

### Left alone (daily ops already touched)
- Catalog: openai-codex, opencode, coding-agents Top3, analytics script sync — unchanged this slice

## Connectors status
| Connector | Status |
|-----------|--------|
| GitHub | Connected (`leonwang2mini-beep/agents-use-cases`) |
| Vercel | Project live; team MCP for `wanglis-projects-7cd320e8` previously **403** |
| Resend | Connected; **unused until Leon approves** send / segment |
| Stripe | Connected |
| Buffer | Connected (X outbound still needs Leon) |
| Finance | needsAuth (prior note) |

## Still needs Leon
1. **Domain** `agentsusecases.ai` — still NXDOMAIN and not purchased. Live SEO is temporarily on `https://agents-use-cases.vercel.app` (option B). Buy/attach later if the custom domain should become canonical again.
2. **Approve push** of local changes (today’s daily catalog + this weekly newsletter/Featured work)
3. **Approve first newsletter send** when W42 (or later) is ready — do not broadcast yet
4. **Approve rate card** before any external Featured quote
5. Domain mailbox / Resend segment when ready for real signup + Featured mailto

## Next week (suggestions)
- Wire Resend audience + footer waitlist → contact create (still gate broadcasts)
- After domain: update DNS, mailbox `hello@…`, then optional SEO canonical cutover
- If first sponsor closes: activate placement per FEATURED-OPS; sync rankings manually
- Optional: tiny `scripts/sync-featured-rankings.py` only if manual sync becomes error-prone
- Continue catalog/X-signal quality; keep demo Featured closed until real $

## Not done this run
- No git init/push, no deploy, no email/broadcast, no spend, no demo Featured activation
