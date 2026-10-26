#!/usr/bin/env python3
"""Static build for Agents Use Cases (no deps).

Generates, from data/*.json:
  - api/{tools,use-cases,featured,x-signals}.json mirrors (copied from data/)
  - api/rankings.json  (editorial + active featured, incl. meta.homepageFeatured)
  - api/use-cases/<id>.json  per-use-case resolved JSON for agents
  - best/<id>.html          crawlable pre-rendered use-case pages (no JS needed)
  - best/index.html         crawlable index of all use cases
  - adds best/* URLs to sitemap.xml (idempotent)
Run: python3 scripts/build.py   (from repo root)
"""
import json, html, os, re, shutil, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://agents-use-cases.vercel.app"
TODAY = datetime.date.today().isoformat()
P = lambda *a: os.path.join(ROOT, *a)
load = lambda p: json.load(open(P(p), encoding="utf-8"))
def dump(p, obj):
    os.makedirs(os.path.dirname(P(p)), exist_ok=True)
    with open(P(p), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2); f.write("\n")
E = html.escape

tools = {t["id"]: t for t in load("data/tools.json")["tools"]}
ucs = load("data/use-cases.json")["useCases"]
feat = load("data/featured.json")
sig = load("data/x-signals.json")

for name in ["tools", "use-cases", "featured", "x-signals"]:
    shutil.copyfile(P("data", name + ".json"), P("api", name + ".json"))

def active(p):
    return p.get("active") and p.get("starts", "") <= TODAY <= p.get("ends", "9999")
act = [p for p in feat.get("placements", []) if active(p)]

def tool_row(tid, extra):
    t = tools.get(tid, {})
    return {"toolId": tid, "name": t.get("name", tid), "url": t.get("url"),
            "pricing": t.get("pricing"), **extra}

rank_old = load("api/rankings.json")
rankings = []
for u in ucs:
    ed = [tool_row(e["toolId"], {"rank": e["rank"], "why": e["why"], "source": "editorial"})
          for e in sorted(u.get("editorial", []), key=lambda e: e["rank"])]
    fe = [tool_row(p["toolId"], {"label": p["label"], "why": p["why"], "source": "featured",
                                 "placementId": p["id"], "ends": p.get("ends")})
          for p in act if p.get("slot") == "use-case" and p.get("useCaseId") == u["id"]]
    rankings.append({"useCaseId": u["id"], "title": u["title"], "editorial": ed, "featured": fe,
                     "page": f"/best/{u['id']}.html",
                     "canonicalHint": f"{BASE}/best/{u['id']}.html",
                     "json": f"/api/use-cases/{u['id']}.json"})
meta = rank_old["meta"]
meta.update({"updated": TODAY, "generatedBy": "scripts/build.py",
             "homepageFeatured": [tool_row(p["toolId"], {"label": p["label"], "why": p["why"],
                                  "placementId": p["id"], "ends": p.get("ends")})
                                  for p in act if p.get("slot") == "homepage"]})
meta.setdefault("pages", {})["useCasePattern"] = BASE + "/best/{useCaseId}.html"
meta["pages"]["useCaseJsonPattern"] = BASE + "/api/use-cases/{useCaseId}.json"
dump("api/rankings.json", {"meta": meta, "rankings": rankings})

sig_items = sig.get("signals", sig.get("items", []))
HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="{url}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="article" />
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
    <ul class="nav-links"><li><a href="index.html">All use cases</a></li><li><a href="../about.html">About</a></li>
    <li><a class="btn btn-primary" href="../submit.html">Feature your tool</a></li></ul>
  </div></header>
  <main class="wrap">
"""
FOOT = """  </main>
  <footer class="site-footer"><div class="wrap footer-grid">
    <div>Agents Use Cases · <a href="../about.html">About rankings</a> · <a href="../llms.txt">llms.txt</a> · <a href="../api/rankings.json">api/rankings.json</a></div>
    <div>Updated {d}</div></div></footer>
</body>
</html>
"""
os.makedirs(P("best"), exist_ok=True)
for u, r in zip(ucs, rankings):
    uid = u["id"]; url = f"{BASE}/best/{uid}.html"
    top = ", ".join(e["name"] for e in r["editorial"][:3])
    desc = f"{u['title']} for builders and agents: {top}. One-line why for each pick; paid placements labeled separately."
    uc_sigs = [s for s in sig_items if uid in (s.get("useCaseIds") or []) and str(s.get("id","")).startswith("x-real")][:6]  # real captures only
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": u["title"], "url": url,
          "description": u.get("summary", ""),
          "itemListElement": [{"@type": "ListItem", "position": e["rank"], "name": e["name"],
                               "url": e["url"], "description": e["why"]} for e in r["editorial"]]}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Use cases", "item": BASE + "/best/"},
        {"@type": "ListItem", "position": 3, "name": u["title"], "item": url}]}
    out = [HEAD.format(title=E(f"{u['title']} ({TODAY[:4]}) · Agents Use Cases"), desc=E(desc), url=url,
                       alt=f'<link rel="alternate" type="application/json" href="../api/use-cases/{uid}.json" title="{E(u["title"])} JSON" />',
                       ld=json.dumps([ld, crumbs], ensure_ascii=False).replace("</", "<\\/"))]
    out.append(f'''    <div class="page-hero">
      <div class="breadcrumb"><a href="../index.html">Home</a> / <a href="index.html">Use cases</a> / {E(u["title"])}</div>
      <h1>{E(u.get("icon",""))} {E(u["title"])}</h1>
      <p class="uc-why-lead">{E(u.get("summary",""))}</p>
      <p style="margin-top:0.5rem;font-size:0.9rem">{E(u.get("audience",""))}</p>
      <p class="uc-why-box"><strong>How to read this:</strong> Editorial ranks are unpaid picks with a one-line why. Featured blocks are paid, labeled, and never change Top 1/2/3.</p>
    </div>
''')
    if r["featured"]:
        out.append('    <section class="section"><div class="panel-label"><span class="section-label">Sponsored</span><span class="badge badge-featured">Featured</span></div><ol class="rank-list">\n')
        for f in r["featured"]:
            out.append(f'      <li><a href="{E(f["url"] or "#")}" rel="sponsored noopener">{E(f["name"])}</a> <span class="badge badge-featured">{E(f["label"])}</span> — {E(f["why"])}</li>\n')
        out.append('    </ol></section>\n')
    out.append('    <section class="section"><div class="panel-label"><span class="section-label">Editorial ranking</span><span class="badge badge-editorial">Not for sale</span></div>\n    <ol class="rank-list">\n')
    for e in r["editorial"]:
        out.append(f'      <li><strong>#{e["rank"]} <a href="../tool.html?id={E(e["toolId"])}">{E(e["name"])}</a></strong> · {E(e["pricing"] or "")} · <a href="{E(e["url"] or "#")}" rel="noopener">site</a><br />{E(e["why"])}</li>\n')
    out.append('    </ol></section>\n')
    if uc_sigs:
        out.append('    <section class="section"><div class="section-label">Signals</div><h2>From X</h2><ul>\n')
        for s in uc_sigs:
            txt = s.get("text") or s.get("summary") or ""
            link = s.get("url") or s.get("link")
            who = s.get("handle") or s.get("displayName") or ""
            out.append(f'      <li>{E(who)} — {E(txt[:240])}' + (f' (<a href="{E(link)}" rel="nofollow noopener">post</a>)' if link else "") + '</li>\n')
        out.append('    </ul></section>\n')
    out.append('    <nav class="section uc-more" aria-label="More use cases"><div class="section-label">More use cases</div><p>' +
               " · ".join(f'<a href="{x["id"]}.html">{E(x["title"])}</a>' for x in ucs if x["id"] != uid) +
               f'</p><p style="font-size:0.85rem">Interactive view: <a href="../use-case.html?id={uid}">use-case.html?id={uid}</a> · JSON: <a href="../api/use-cases/{uid}.json">/api/use-cases/{uid}.json</a></p></nav>\n')
    out.append(FOOT.format(d=TODAY))
    open(P("best", uid + ".html"), "w", encoding="utf-8").write("".join(out))
    dump(f"api/use-cases/{uid}.json", {"meta": {"updated": TODAY, "baseUrl": BASE, "page": url,
          "note": "editorial[] is unpaid opinion; featured[] is paid and labeled."},
          **{k: u.get(k) for k in ["id", "title", "summary", "audience"]},
          "editorial": r["editorial"], "featured": r["featured"]})

idx = [HEAD.format(title="All AI use cases · Agents Use Cases", desc="Every use case on Agents Use Cases with its editorial Top 3 and one-line why.",
                   url=BASE + "/best/", alt='<link rel="alternate" type="application/json" href="../api/rankings.json" title="Rankings JSON" />',
                   ld=json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "All use cases", "url": BASE + "/best/"}))]
idx.append('    <div class="page-hero"><h1>All use cases</h1><p class="uc-why-lead">Editorial Top 3 per use case. Paid placements are labeled separately.</p></div>\n    <section class="section"><ul>\n')
for u, r in zip(ucs, rankings):
    idx.append(f'      <li><a href="{u["id"]}.html"><strong>{E(u["title"])}</strong></a> — ' + ", ".join(E(e["name"]) for e in r["editorial"][:3]) + '</li>\n')
idx.append('    </ul></section>\n' + FOOT.format(d=TODAY))
open(P("best", "index.html"), "w", encoding="utf-8").write("".join(idx))

sm = open(P("sitemap.xml"), encoding="utf-8").read()
sm = re.sub(r"\s*<url>\s*<loc>[^<]*/best/[^<]*</loc>.*?</url>", "", sm, flags=re.S)
add = "".join(f"\n  <url>\n    <loc>{BASE}/best/{p}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>"
              for p, pr in [("", "0.8")] + [(u["id"] + ".html", "0.8") for u in ucs])
sm = sm.replace("</urlset>", add.lstrip("\n").join(["", ""]) + "\n</urlset>") if False else sm.replace("\n</urlset>", add + "\n</urlset>")
open(P("sitemap.xml"), "w", encoding="utf-8").write(sm)
print(f"built {len(ucs)} use-case pages, {len(tools)} tools, {len(act)} active featured")
