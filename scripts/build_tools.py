#!/usr/bin/env python3
"""Crawlable per-tool pages + per-tool agent JSON (no deps). Called from build.py.

Generates:
  - tools/<id>.html   pre-rendered tool page (no JS): tagline, pricing, use cases with editorial rank/why, real X signals
  - tools/index.html  A-Z index of every tool
  - api/tools/<id>.json resolved per-tool JSON for agents
  - sitemap.xml: replaces tool.html?id=<id> entries with /tools/<id>.html (idempotent)
"""
import json, html, os, re, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://agents-use-cases.vercel.app"
TODAY = datetime.date.today().isoformat()
P = lambda *a: os.path.join(ROOT, *a)
load = lambda p: json.load(open(P(p), encoding="utf-8"))
E = html.escape

def clip(text, n):
    """Trim to <= n chars at a word boundary (SERP-friendly meta description), keep rank/pricing tail intact."""
    text = " ".join(text.split())
    if len(text) <= n:
        return text
    cut = text[:n - 1].rsplit(" ", 1)[0].rstrip(" ,;:—-(")
    return cut + "…"
def dump(p, obj):
    os.makedirs(os.path.dirname(P(p)), exist_ok=True)
    with open(P(p), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2); f.write("\n")

tools = load("data/tools.json")["tools"]
ucs = {u["id"]: u for u in load("data/use-cases.json")["useCases"]}
sig = load("data/x-signals.json"); sig_items = sig.get("signals", sig.get("items", []))
feat = load("data/featured.json")
def active(p): return p.get("active") and p.get("starts", "") <= TODAY <= p.get("ends", "9999")
act = [p for p in feat.get("placements", []) if active(p)]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="{url}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Agents Use Cases" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:url" content="{url}" />
  <meta name="twitter:card" content="summary" />
  <link rel="icon" href="../favicon.svg" type="image/svg+xml" />
  {alt}
  <link rel="stylesheet" href="../css/styles.css" />
  <script defer src="/_vercel/insights/script.js"></script>
  <script type="application/ld+json">{ld}</script>
</head>
<body>
  <header class="site-header"><div class="wrap nav">
    <a class="logo" href="../index.html"><span class="logo-mark">A</span> Agents Use Cases</a>
    <ul class="nav-links"><li><a href="index.html">All tools</a></li><li><a href="../best/index.html">Use cases</a></li><li><a href="../about.html">About</a></li>
    <li><a class="btn btn-primary" href="../submit.html">Feature your tool</a></li></ul>
  </div></header>
  <main class="wrap">
"""
FOOT = """  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div>Agents Use Cases · <a href="../about.html">About rankings</a> · <a href="../llms.txt">llms.txt</a> · <a href="../api/tools.json">api/tools.json</a></div>
    <div>Updated {d}</div></div></footer>
</body>
</html>
"""
ldj = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
os.makedirs(P("tools"), exist_ok=True)
for t in tools:
    tid = t["id"]; url = f"{BASE}/tools/{tid}.html"
    rows = []
    for ucid in t.get("useCases", []):
        u = ucs.get(ucid)
        if not u: continue
        ed = next((e for e in u.get("editorial", []) if e["toolId"] == tid), None)
        rows.append({"useCaseId": ucid, "title": u["title"], "page": f"/best/{ucid}.html",
                     "editorialRank": ed["rank"] if ed else None, "why": ed["why"] if ed else None})
    fe = [{"placementId": p["id"], "slot": p.get("slot"), "useCaseId": p.get("useCaseId"),
           "label": p["label"], "why": p["why"], "ends": p.get("ends")} for p in act if p.get("toolId") == tid]
    sigs = [s for s in sig_items if tid in (s.get("toolIds") or []) and str(s.get("id", "")).startswith("x-real")][:6]
    ranked = [r for r in rows if r["editorialRank"]]
    lead = f"{t['name']}: {t.get('tagline','')}".strip()
    tail = ((f" Ranked #{ranked[0]['editorialRank']} in {ranked[0]['title']}." if ranked else "") +
            f" Pricing: {t.get('pricing') or 'n/a'}.")
    body = clip(lead, 158 - len(tail))
    if body and body[-1] not in ".!?…":
        body += "."
    desc = body + tail
    app = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": t["name"],
           "url": t.get("url"), "description": t.get("tagline", ""), "applicationCategory": "DeveloperApplication"}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Tools", "item": BASE + "/tools/index.html"},
        {"@type": "ListItem", "position": 3, "name": t["name"], "item": url}]}
    out = [HEAD.format(title=E(f"{t['name']} · use cases, pricing & why · Agents Use Cases"), desc=E(desc), url=url,
                       alt=f'<link rel="alternate" type="application/json" href="../api/tools/{tid}.json" title="{E(t["name"])} JSON" />',
                       ld=ldj([app, crumbs]))]
    out.append(f'''    <div class="page-hero">
      <div class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Tools</a> / {E(t["name"])}</div>
      <h1>{E(t["name"])}{' <span class="badge">New</span>' if t.get("isNew") else ""}</h1>
      <p class="uc-why-lead">{E(t.get("tagline",""))}</p>
      <p>Pricing: {E(t.get("pricing") or "n/a")} · <a href="{E(t.get("url") or "#")}" rel="noopener">Official site</a>{f" · Added {E(t['added'])}" if t.get("added") else ""}</p>
    </div>
''')
    if fe:
        out.append('    <section class="section"><div class="panel-label"><span class="section-label">Sponsored</span><span class="badge badge-featured">Featured</span></div><ul>\n')
        for f in fe: out.append(f'      <li><span class="badge badge-featured">{E(f["label"])}</span> {E(f["why"])}</li>\n')
        out.append('    </ul></section>\n')
    out.append('    <section class="section"><div class="panel-label"><span class="section-label">Use cases</span><span class="badge badge-editorial">Editorial</span></div><ul class="rank-list">\n')
    for r in rows:
        rk = f'Editorial #{r["editorialRank"]} — {E(r["why"])}' if r["editorialRank"] else "Listed (not in the editorial Top picks)"
        out.append(f'      <li><a href="../best/{r["useCaseId"]}.html"><strong>{E(r["title"])}</strong></a><br />{rk}</li>\n')
    out.append('    </ul></section>\n')
    if sigs:
        out.append('    <section class="section"><div class="section-label">Signals</div><h2>From X</h2><ul>\n')
        for s in sigs:
            link = s.get("url")
            out.append(f'      <li>{E(s.get("handle",""))} — {E((s.get("text") or "")[:240])}' + (f' (<a href="{E(link)}" rel="nofollow noopener">post</a>)' if link else "") + '</li>\n')
        out.append('    </ul></section>\n')
    out.append(f'    <p class="section" style="font-size:0.85rem">Interactive view: <a href="../tool.html?id={E(tid)}">tool.html?id={E(tid)}</a> · JSON: <a href="../api/tools/{E(tid)}.json">/api/tools/{E(tid)}.json</a></p>\n')
    out.append(FOOT.format(d=TODAY))
    open(P("tools", tid + ".html"), "w", encoding="utf-8").write("".join(out))
    dump(f"api/tools/{tid}.json", {"meta": {"updated": TODAY, "baseUrl": BASE, "page": url,
          "note": "useCases[].editorialRank is unpaid opinion; featured[] is paid and labeled."},
          **{k: t.get(k) for k in ["id", "name", "tagline", "url", "pricing", "categories", "added", "isNew"]},
          "useCases": rows, "featured": fe,
          "xSignals": [{k: s.get(k) for k in ["handle", "text", "url", "capturedAt"]} for s in sigs]})

srt = sorted(tools, key=lambda t: t["name"].lower())
idx = [HEAD.format(title="All AI tools A–Z · Agents Use Cases", desc=f"{len(tools)} AI tools for builders and agents, each with use cases, pricing and editorial why.",
                   url=BASE + "/tools/index.html", alt='<link rel="alternate" type="application/json" href="../api/tools.json" title="Tools JSON" />',
                   ld=ldj([{"@context": "https://schema.org", "@type": "CollectionPage", "name": "All AI tools A–Z", "url": BASE + "/tools/index.html",
                            "description": f"{len(tools)} AI tools for builders and agents, each with use cases, pricing and editorial why.",
                            "isPartOf": {"@type": "WebSite", "name": "Agents Use Cases", "url": BASE + "/"},
                            "mainEntity": {"@type": "ItemList", "numberOfItems": len(srt), "itemListOrder": "https://schema.org/ItemListOrderAscending",
                                           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": t["name"], "url": f"{BASE}/tools/{t['id']}.html"} for i, t in enumerate(srt)]}},
                           {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
                            {"@type": "ListItem", "position": 2, "name": "Tools", "item": BASE + "/tools/index.html"}]}]))]
idx.append(f'    <div class="page-hero"><h1>All tools</h1><p class="uc-why-lead">{len(tools)} tools, A–Z. Each page lists its use cases and editorial rank.</p></div>\n    <section class="section"><ul>\n')
for t in srt:
    idx.append(f'      <li><a href="{t["id"]}.html"><strong>{E(t["name"])}</strong></a> — {E(t.get("tagline",""))}</li>\n')
idx.append('    </ul></section>\n' + FOOT.format(d=TODAY))
open(P("tools", "index.html"), "w", encoding="utf-8").write("".join(idx))

# Inactive demo seed (example.com). The page and JSON still build; it stays out of the sitemap
# (removed 2026-10-27). Do not list it just because it is in data/tools.json.
SITEMAP_SKIP = {"sponsor-demo-tool"}
sm = open(P("sitemap.xml"), encoding="utf-8").read()
sm = re.sub(r"\s*<url>\s*<loc>[^<]*(?:/tool\.html\?id=|/tools/)[^<]*</loc>.*?</url>", "", sm, flags=re.S)
add = "".join(f"\n  <url>\n    <loc>{BASE}/tools/{p}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>"
              for p, pr in [("index.html", "0.7")] + [(t["id"] + ".html", "0.6") for t in tools if t["id"] not in SITEMAP_SKIP])
sm = sm.replace("\n</urlset>", add + "\n</urlset>")
open(P("sitemap.xml"), "w", encoding="utf-8").write(sm)
print(f"built {len(tools)} tool pages + tools/index.html")
