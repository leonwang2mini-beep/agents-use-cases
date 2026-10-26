/**
 * Agents Use Cases — client app
 * Loads JSON from /data (or ../data from nested pages) and renders UI.
 * X signals are demo data; structure matches planned API ingest.
 */
(function () {
  "use strict";

  const DATA_BASE = document.body.dataset.dataBase || "data";

  const state = {
    tools: null,
    useCases: null,
    featured: null,
    xSignals: null,
    toolMap: {},
    useCaseMap: {},
  };

  async function loadJSON(name) {
    const res = await fetch(`${DATA_BASE}/${name}`);
    if (!res.ok) throw new Error(`Failed to load ${name}: ${res.status}`);
    return res.json();
  }

  async function loadAll() {
    const [tools, useCases, featured, xSignals] = await Promise.all([
      loadJSON("tools.json"),
      loadJSON("use-cases.json"),
      loadJSON("featured.json"),
      loadJSON("x-signals.json"),
    ]);
    state.tools = tools.tools;
    state.useCases = useCases.useCases;
    state.featured = (featured.placements || []).filter((p) => p.active);
    state.xSignals = xSignals.signals || [];
    state.toolMap = Object.fromEntries(state.tools.map((t) => [t.id, t]));
    state.useCaseMap = Object.fromEntries(state.useCases.map((u) => [u.id, u]));
    return state;
  }

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }
  function qsa(sel, root) {
    return Array.from((root || document).querySelectorAll(sel));
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function param(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  function badgePricing(p) {
    return `<span class="badge badge-pricing">${escapeHtml(p || "—")}</span>`;
  }
  function badgeNew() {
    return `<span class="badge badge-new">New</span>`;
  }
  function badgeFeatured(label) {
    return `<span class="badge badge-featured">${escapeHtml(label || "Featured")}</span>`;
  }
  function badgeEditorial() {
    return `<span class="badge badge-editorial">Editorial</span>`;
  }
  function badgeRank(n) {
    return `<span class="badge badge-rank">#${n}</span>`;
  }

  function toolUrl(id) {
    return `tool.html?id=${encodeURIComponent(id)}`;
  }
  function useCaseUrl(id) {
    return `use-case.html?id=${encodeURIComponent(id)}`;
  }

  function renderUseCaseCards(container) {
    if (!container) return;
    container.innerHTML = state.useCases
      .map(
        (uc) => `
      <a class="card card-link uc-card" href="${useCaseUrl(uc.id)}">
        <div class="uc-icon">${uc.icon || "▸"}</div>
        <h3>${escapeHtml(uc.title)}</h3>
        <p>${escapeHtml(uc.summary)}</p>
        <div class="uc-meta">${uc.editorial.length} editorial picks</div>
      </a>`
      )
      .join("");
  }

  function renderNewTools(container) {
    if (!container) return;
    const news = state.tools
      .filter((t) => t.isNew)
      .sort((a, b) => (a.added < b.added ? 1 : -1));
    if (!news.length) {
      container.innerHTML = `<p class="empty">No new tools this week.</p>`;
      return;
    }
    container.innerHTML = news
      .map(
        (t) => `
      <a class="card card-link tool-card" href="${toolUrl(t.id)}">
        <h3>${escapeHtml(t.name)} ${badgeNew()}</h3>
        <p class="tagline">${escapeHtml(t.tagline)}</p>
        <div class="tool-meta">
          ${badgePricing(t.pricing)}
          <span class="badge badge-pricing">Added ${escapeHtml(t.added)}</span>
        </div>
      </a>`
      )
      .join("");
  }

  function renderHomepageFeatured(container) {
    if (!container) return;
    const placements = state.featured.filter((p) => p.slot === "homepage");
    if (!placements.length) {
      container.innerHTML = `<p class="empty">No featured placements right now. <a href="submit.html">Apply</a></p>`;
      return;
    }
    container.innerHTML = placements
      .map((p) => {
        const t = state.toolMap[p.toolId];
        if (!t) return "";
        return `
        <a class="card card-link tool-card card-featured" href="${toolUrl(t.id)}">
          <h3>${escapeHtml(t.name)} ${badgeFeatured(p.label)}</h3>
          <p class="tagline">${escapeHtml(t.tagline)}</p>
          <p class="why">${escapeHtml(p.why)}</p>
          <div class="tool-meta">
            ${badgePricing(t.pricing)}
            <span class="badge badge-featured">Paid placement</span>
          </div>
        </a>`;
      })
      .join("");
  }

  function renderSignals(container, filterUseCaseId) {
    if (!container) return;
    let signals = state.xSignals;
    if (filterUseCaseId) {
      signals = signals.filter((s) => (s.useCaseIds || []).includes(filterUseCaseId));
    }
    signals = signals.slice(0, filterUseCaseId ? 6 : 5);
    if (!signals.length) {
      container.innerHTML = `<p class="empty">No X signals for this use case yet. (Demo scanner placeholder.)</p>`;
      return;
    }
    container.innerHTML = signals
      .map((s) => {
        const ucTags = (s.useCaseIds || [])
          .map((id) => {
            const uc = state.useCaseMap[id];
            return uc
              ? `<a href="${useCaseUrl(id)}" class="badge badge-pricing">${escapeHtml(uc.title.replace(/^Best /, ""))}</a>`
              : "";
          })
          .join("");
        return `
        <article class="card signal-card">
          <div>
            <span class="handle">${escapeHtml(s.handle)}</span>
            <span class="display">${escapeHtml(s.displayName || "")}</span>
          </div>
          <p class="text">${escapeHtml(s.text)}</p>
          <div class="sig-meta">
            <span>♥ ${s.engagement?.likes ?? 0}</span>
            <span>↻ ${s.engagement?.reposts ?? 0}</span>
            ${ucTags}
            <a href="${escapeHtml(s.url)}" target="_blank" rel="noopener">View on X ↗</a>
          </div>
        </article>`;
      })
      .join("");
  }


  const SITE_ORIGIN = "https://agents-use-cases.vercel.app";

  function setMeta(nameOrProp, content, isProp) {
    if (!content) return;
    const sel = isProp
      ? `meta[property="${nameOrProp}"]`
      : nameOrProp === "description"
        ? 'meta[name="description"], #meta-desc'
        : `meta[name="${nameOrProp}"]`;
    const el = document.querySelector(sel) || document.getElementById(nameOrProp === "description" ? "meta-desc" : "");
    if (el) el.setAttribute("content", content);
  }

  function setCanonical(url) {
    const el = document.getElementById("canonical") || document.querySelector('link[rel="canonical"]');
    if (el) el.setAttribute("href", url);
  }

  function setJsonLd(scriptId, obj) {
    const el = document.getElementById(scriptId);
    if (el) el.textContent = JSON.stringify(obj);
  }

  function initNewsletter() {
    const form = qs("#newsletter-form");
    if (!form) return;
    const note = qs("#newsletter-note");
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const email = (qs("#newsletter-email")?.value || "").trim();
      if (note) {
        note.hidden = false;
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          note.textContent = "Enter a valid email. Nothing was submitted.";
          return;
        }
        note.innerHTML =
          "<strong>Not connected yet.</strong> Newsletter will use Resend once wired. " +
          "Your email was <em>not</em> stored or sent. Come back after we connect the Resend domain.";
      }
    });
  }

  function renderUseCasePage() {
    const id = param("id");
    const root = qs("#use-case-root");
    if (!root) return;
    const uc = state.useCaseMap[id];
    if (!uc) {
      root.innerHTML = `<p class="empty">Use case not found. <a href="index.html">Back home</a></p>`;
      return;
    }
    qs("#uc-title") && (qs("#uc-title").textContent = uc.title);
    qs("#uc-summary") && (qs("#uc-summary").textContent = uc.summary);
    qs("#uc-audience") && (qs("#uc-audience").textContent = uc.audience || "");
    document.title = `${uc.title} · Agents Use Cases`;
    const pageUrl = `${SITE_ORIGIN}/use-case.html?id=${encodeURIComponent(uc.id)}`;
    setCanonical(pageUrl);
    setMeta("description", `${uc.title}: ${uc.summary} Editorial Top picks with a one-line why. Featured placements are paid and labeled separately.`);
    setMeta("og:title", `${uc.title} · Agents Use Cases`, true);
    setMeta("og:description", uc.summary, true);
    setMeta("og:url", pageUrl, true);
    const ogTitle = document.getElementById("og-title");
    if (ogTitle) ogTitle.setAttribute("content", `${uc.title} · Agents Use Cases`);
    const ogDesc = document.getElementById("og-desc");
    if (ogDesc) ogDesc.setAttribute("content", uc.summary);
    const ogUrl = document.getElementById("og-url");
    if (ogUrl) ogUrl.setAttribute("content", pageUrl);
    if (qs("#uc-crumb")) qs("#uc-crumb").textContent = uc.title.replace(/^Best /, "");

    const editorialSorted = uc.editorial.slice().sort((a, b) => a.rank - b.rank);
    setJsonLd("jsonld-usecase", {
      "@context": "https://schema.org",
      "@type": "ItemList",
      "name": uc.title,
      "description": uc.summary,
      "url": pageUrl,
      "numberOfItems": editorialSorted.length,
      "itemListElement": editorialSorted.map((e, i) => {
        const t = state.toolMap[e.toolId];
        return {
          "@type": "ListItem",
          "position": e.rank || i + 1,
          "name": t ? t.name : e.toolId,
          "url": t ? t.url : undefined,
          "description": e.why,
        };
      }),
    });

    const featEl = qs("#uc-featured");
    const editEl = qs("#uc-editorial");
    const sigEl = qs("#uc-signals");

    const placements = state.featured.filter(
      (p) => p.useCaseId === uc.id && p.slot === "use-case"
    );
    if (featEl) {
      if (!placements.length) {
        featEl.innerHTML = `<p class="empty">No sponsored placement on this page. <a href="submit.html">Feature your tool</a></p>`;
      } else {
        featEl.innerHTML = placements
          .map((p) => {
            const t = state.toolMap[p.toolId];
            if (!t) return "";
            return `
            <article class="card rank-item card-featured">
              <div class="rank-num">★</div>
              <div>
                <h3><a href="${toolUrl(t.id)}">${escapeHtml(t.name)}</a> ${badgeFeatured(p.label)}</h3>
                <p class="tagline">${escapeHtml(t.tagline)}</p>
                <p class="why"><strong>Why this pick:</strong> ${escapeHtml(p.why)}</p>
                <div class="tool-meta" style="margin-top:0.75rem">
                  ${badgePricing(t.pricing)}
                  <span class="badge badge-featured">Paid · not editorial</span>
                </div>
              </div>
              <div class="rank-actions">
                <a class="btn btn-primary" href="${escapeHtml(t.url)}" target="_blank" rel="noopener sponsored">Visit ↗</a>
              </div>
            </article>`;
          })
          .join("");
      }
    }

    if (editEl) {
      editEl.innerHTML = uc.editorial
        .slice()
        .sort((a, b) => a.rank - b.rank)
        .map((e) => {
          const t = state.toolMap[e.toolId];
          if (!t) return "";
          return `
          <article class="card rank-item">
            <div class="rank-num">${e.rank}</div>
            <div>
              <h3><a href="${toolUrl(t.id)}">${escapeHtml(t.name)}</a> ${badgeEditorial()} ${t.isNew ? badgeNew() : ""}</h3>
              <p class="tagline">${escapeHtml(t.tagline)}</p>
              <p class="why"><strong>Why this pick:</strong> ${escapeHtml(e.why)}</p>
              <div class="tool-meta" style="margin-top:0.75rem">${badgePricing(t.pricing)}</div>
            </div>
            <div class="rank-actions">
              <a class="btn" href="${escapeHtml(t.url)}" target="_blank" rel="noopener">Visit ↗</a>
            </div>
          </article>`;
        })
        .join("");
    }

    renderSignals(sigEl, uc.id);

    const more = qs("#uc-more-links");
    if (more) {
      more.innerHTML = state.useCases
        .filter((u) => u.id !== uc.id)
        .map((u) => `<a href="${useCaseUrl(u.id)}">${escapeHtml(u.title)}</a>`)
        .join("");
    }
  }

  function renderToolPage() {
    const id = param("id");
    const root = qs("#tool-root");
    if (!root) return;
    const t = state.toolMap[id];
    if (!t) {
      root.innerHTML = `<p class="empty">Tool not found. <a href="index.html">Back home</a></p>`;
      return;
    }
    document.title = `${t.name} · Agents Use Cases`;
    const toolPageUrl = `${SITE_ORIGIN}/tool.html?id=${encodeURIComponent(t.id)}`;
    setCanonical(toolPageUrl);
    setMeta("description", `${t.name} — ${t.tagline}. See linked use cases and why it appears on Agents Use Cases.`);
    setMeta("og:title", `${t.name} · Agents Use Cases`, true);
    setMeta("og:description", t.tagline, true);
    setMeta("og:url", toolPageUrl, true);
    const togTitle = document.getElementById("og-title");
    if (togTitle) togTitle.setAttribute("content", `${t.name} · Agents Use Cases`);
    const togDesc = document.getElementById("og-desc");
    if (togDesc) togDesc.setAttribute("content", t.tagline);
    const togUrl = document.getElementById("og-url");
    if (togUrl) togUrl.setAttribute("content", toolPageUrl);
    setJsonLd("jsonld-tool", {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": t.name,
      "description": t.tagline,
      "url": t.url,
      "applicationCategory": "DeveloperApplication",
      "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD", "description": t.pricing },
    });

    const relatedUc = state.useCases.filter((uc) =>
      (t.useCases || []).includes(uc.id)
    );
    const whys = [];
    relatedUc.forEach((uc) => {
      const e = uc.editorial.find((x) => x.toolId === t.id);
      if (e) whys.push({ useCase: uc, why: e.why, source: "editorial", rank: e.rank });
    });
    state.featured
      .filter((p) => p.toolId === t.id)
      .forEach((p) => {
        whys.push({
          useCase: p.useCaseId ? state.useCaseMap[p.useCaseId] : null,
          why: p.why,
          source: "featured",
          label: p.label,
        });
      });

    root.innerHTML = `
      <div class="page-hero" style="border:none;margin:0;padding-top:0">
        <div class="breadcrumb"><a href="index.html">Home</a> / Tool</div>
        <h1>${escapeHtml(t.name)} ${t.isNew ? badgeNew() : ""} ${
      t.source === "featured" ? badgeFeatured("Featured") : ""
    }</h1>
        <p>${escapeHtml(t.tagline)}</p>
        <div class="tool-meta" style="margin-top:1rem">
          ${badgePricing(t.pricing)}
          <span class="badge badge-pricing">Added ${escapeHtml(t.added)}</span>
          <span class="badge badge-pricing">Source: ${escapeHtml(t.source)}</span>
        </div>
        <div style="margin-top:1.25rem;display:flex;gap:0.75rem;flex-wrap:wrap">
          <a class="btn btn-primary" href="${escapeHtml(t.url)}" target="_blank" rel="noopener">Open website ↗</a>
          <a class="btn" href="submit.html">Feature a tool</a>
        </div>
      </div>

      <section class="section" style="padding-top:0.5rem">
        <h2 class="section-label">Fits these use cases</h2>
        <div class="grid-use-cases" style="margin-top:0.75rem">
          ${
            relatedUc.length
              ? relatedUc
                  .map(
                    (uc) => `
            <a class="card card-link uc-card" href="${useCaseUrl(uc.id)}">
              <div class="uc-icon">${uc.icon || ""}</div>
              <h3>${escapeHtml(uc.title)}</h3>
              <p>${escapeHtml(uc.summary)}</p>
            </a>`
                  )
                  .join("")
              : `<p class="empty">No use cases linked.</p>`
          }
        </div>
      </section>

      <section class="section">
        <h2 class="section-label">Why it appears here</h2>
        <div class="rank-list" style="margin-top:0.75rem">
          ${
            whys.length
              ? whys
                  .map((w) => {
                    if (w.source === "featured") {
                      return `<article class="card card-featured">
                        <div class="tool-meta">${badgeFeatured(w.label || "Featured")}
                          ${w.useCase ? `<a href="${useCaseUrl(w.useCase.id)}" class="badge badge-pricing">${escapeHtml(w.useCase.title)}</a>` : `<span class="badge badge-pricing">Homepage</span>`}
                        </div>
                        <p class="why" style="margin-top:0.75rem">${escapeHtml(w.why)}</p>
                        <p style="margin:0.5rem 0 0;font-size:0.8rem;color:var(--text-dim)">Paid placement — separate from editorial rankings.</p>
                      </article>`;
                    }
                    return `<article class="card">
                      <div class="tool-meta">${badgeEditorial()} ${badgeRank(w.rank)}
                        <a href="${useCaseUrl(w.useCase.id)}" class="badge badge-pricing">${escapeHtml(w.useCase.title)}</a>
                      </div>
                      <p class="why" style="margin-top:0.75rem">${escapeHtml(w.why)}</p>
                    </article>`;
                  })
                  .join("")
              : `<p class="empty">Listed in catalog; no ranked pick yet.</p>`
          }
        </div>
      </section>
    `;
  }

  function initSubmitForm() {
    const form = qs("#submit-form");
    if (!form) return;
    const notice = qs("#submit-notice");

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      qsa(".form-error").forEach((el) => el.classList.remove("show"));

      const name = qs("#tool-name").value.trim();
      const url = qs("#tool-url").value.trim();
      const email = qs("#contact-email").value.trim();
      const type = qs("#submit-type").value;
      const useCase = qs("#use-case-select").value;
      const pitch = qs("#pitch").value.trim();
      const agree = qs("#agree").checked;

      let ok = true;
      function fail(id, msg) {
        const el = qs(`#err-${id}`);
        if (el) {
          el.textContent = msg;
          el.classList.add("show");
        }
        ok = false;
      }

      if (name.length < 2) fail("tool-name", "Tool name is required.");
      try {
        const u = new URL(url);
        if (!/^https?:$/.test(u.protocol)) throw new Error();
      } catch {
        fail("tool-url", "Enter a valid http(s) URL.");
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) fail("contact-email", "Valid email required.");
      if (!type) fail("submit-type", "Choose a submission type.");
      if (!useCase) fail("use-case-select", "Pick a primary use case.");
      if (pitch.length < 20) fail("pitch", "Tell us a bit more (20+ chars).");
      if (!agree) fail("agree", "Please confirm you understand Featured is paid.");

      if (!ok) return;

      const subject = encodeURIComponent(`[Agents Use Cases] ${type}: ${name}`);
      const body = encodeURIComponent(
        [
          `Submission type: ${type}`,
          `Tool: ${name}`,
          `URL: ${url}`,
          `Contact: ${email}`,
          `Primary use case: ${useCase}`,
          ``,
          `Pitch:`,
          pitch,
          ``,
          `---`,
          `Sent from Agents Use Cases submit form (no backend yet).`,
        ].join("\n")
      );

      // Honest path: mailto + coming soon notice — do NOT fake success
      notice.innerHTML = `
        <strong>Form validated.</strong> Backend is not wired yet.<br>
        Option A: open a mail draft to <code>hello@agents-use-cases.vercel.app</code>
        (<strong>mailbox not live yet</strong> — may bounce until DNS/email is ready) —
        <a href="mailto:hello@agents-use-cases.vercel.app?subject=${subject}&body=${body}">mailto draft</a>.<br>
        Option B: wait for <code>POST /api/submissions</code> (coming soon).
        Nothing was submitted to a server.`;
      notice.classList.add("show");

      // Attempt mailto (user may cancel)
      window.location.href = `mailto:hello@agents-use-cases.vercel.app?subject=${subject}&body=${body}`;
    });
  }

  function fillUseCaseSelect() {
    const sel = qs("#use-case-select");
    if (!sel || !state.useCases) return;
    state.useCases.forEach((uc) => {
      const opt = document.createElement("option");
      opt.value = uc.id;
      opt.textContent = uc.title;
      sel.appendChild(opt);
    });
  }

  async function boot() {
    const page = document.body.dataset.page || "home";
    try {
      await loadAll();
    } catch (err) {
      console.error(err);
      const main = qs("main") || document.body;
      const msg = document.createElement("p");
      msg.className = "empty";
      msg.style.padding = "2rem";
      msg.textContent =
        "Could not load data JSON. Serve this folder over HTTP (e.g. python3 -m http.server), not as a raw file:// page.";
      main.prepend(msg);
      return;
    }

    if (page === "home") {
      renderUseCaseCards(qs("#use-cases-grid"));
      renderNewTools(qs("#new-tools-grid"));
      renderHomepageFeatured(qs("#featured-grid"));
      renderSignals(qs("#signals-grid"));
    } else if (page === "use-case") {
      renderUseCasePage();
    } else if (page === "tool") {
      renderToolPage();
    } else if (page === "submit") {
      fillUseCaseSelect();
      initSubmitForm();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
