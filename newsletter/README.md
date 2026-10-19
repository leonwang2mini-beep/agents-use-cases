# Newsletter drafts

Weekly issue drafts live here. They become Resend broadcasts only after Leon approves send.

## Flow

1. Author a draft under `drafts/YYYY-Www.json` (+ optional `.md` twin for humans).
2. Validate shape against `schema.json` (manual or `npx ajv` if available).
3. Leon reviews subject, preheader, and body.
4. On approval: create/send a Resend broadcast (or `compose-broadcast` → `send-broadcast`). **Never send without explicit Leon approval.**
5. After a successful send: set `status` to `published`, set `publishedAt`, and append a slim entry to `api/newsletter.json` → `issues[]`. Keep the full draft in-repo for history.

## Rules

- **Never send without Leon approval.** Outbound email / broadcasts are gated.
- Resend MCP is connected but unused until approve.
- Site footer signup is waitlist only until a Resend audience/segment is wired.
- Drafts under `newsletter/drafts/` are **not public**. Agents should read `/api/newsletter.json` (published index only).
- Prefer real catalog ids from `data/tools.json` and `data/use-cases.json` in `toolIds` / `useCaseIds`.
- Live URL note: canonical host is `https://agents-use-cases.vercel.app/`. Custom domain `agentsusecases.ai` is planned and not live (NXDOMAIN) until Leon connects DNS.

## Naming

- Issue id: `2026-W42` (ISO week).
- Files: `drafts/2026-W42.json`, `drafts/2026-W42.md`.
