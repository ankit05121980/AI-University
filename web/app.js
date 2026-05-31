/* AI-University portal — framework-free SPA (read-only).
 * Every book is fully readable online; nothing is downloadable.
 * Talks to the serve.py API for full content + Ask Anything, with a graceful
 * fallback to the committed demo content + static search index. */
(() => {
  "use strict";

  const DATA = "../data";
  const CONTENT = "../content";
  const API = "/api";

  const state = {
    apiUp: false,
    library: null, categories: null, stats: null, search: null,
    published: null, publishedMap: {}, outlineCache: {}, contentCache: {},
  };

  // ---- storage ----
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  };
  const favs = {
    list: () => store.get("aiu:favorites", []),
    has: (id) => favs.list().includes(id),
    toggle: (id) => { const l = favs.list(); const i = l.indexOf(id); i >= 0 ? l.splice(i, 1) : l.push(id); store.set("aiu:favorites", l); return favs.has(id); },
  };
  const marks = {
    list: () => store.get("aiu:bookmarks", []),
    add: (m) => { const l = marks.list().filter(x => !(x.id === m.id && x.ch === m.ch)); l.unshift(m); store.set("aiu:bookmarks", l.slice(0, 200)); },
    remove: (id, ch) => store.set("aiu:bookmarks", marks.list().filter(x => !(x.id === id && x.ch === ch))),
  };
  const progress = {
    all: () => store.get("aiu:progress", {}),
    get: (id) => progress.all()[id] || { ch: 0, total: 0 },
    set: (id, ch, total) => { const a = progress.all(); a[id] = { ch, total, t: Date.now() }; store.set("aiu:progress", a); },
  };
  const readerPrefs = {
    get: () => store.get("aiu:reader", { scale: 1.06, wide: false }),
    set: (p) => store.set("aiu:reader", p),
  };

  // ---- helpers ----
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const view = () => $("#view");
  const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString());
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function hashHue(s) { let h = 0; for (const c of String(s)) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h % 360; }
  function catGradient(slug) { const h = hashHue(slug); return `linear-gradient(135deg, hsl(${h} 70% 52%), hsl(${(h + 45) % 360} 68% 40%))`; }
  function readingTime(words) { const m = Math.max(1, Math.round((words || 0) / 220)); return m >= 90 ? `~${(m / 60).toFixed(1)} h read` : `~${m} min read`; }
  function ring(pct, size = 36) {
    const r = (size - 6) / 2, c = 2 * Math.PI * r, off = c * (1 - pct / 100);
    return `<svg class="ring" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="var(--surface-2)" stroke-width="4"/>
      <circle cx="${size / 2}" cy="${size / 2}" r="${r}" fill="none" stroke="var(--accent)" stroke-width="4"
        stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}" stroke-linecap="round"
        transform="rotate(-90 ${size / 2} ${size / 2})" style="transition:stroke-dashoffset .5s"/>
      <text x="50%" y="53%" dominant-baseline="middle" text-anchor="middle" font-size="${size * 0.26}" font-weight="800" fill="currentColor">${pct}%</text></svg>`;
  }
  let toastT;
  function toast(msg) {
    let wrap = $("#toast-wrap"); if (!wrap) { wrap = document.createElement("div"); wrap.id = "toast-wrap"; document.body.appendChild(wrap); }
    const t = document.createElement("div"); t.className = "toast"; t.textContent = msg; wrap.appendChild(t);
    requestAnimationFrame(() => t.classList.add("show"));
    setTimeout(() => { t.classList.remove("show"); setTimeout(() => t.remove(), 300); }, 2200);
  }

  async function getJSON(url) { const r = await fetch(url); if (!r.ok) throw new Error(`${r.status} ${url}`); return r.json(); }
  async function load(key, url) { if (state[key]) return state[key]; state[key] = await getJSON(url); return state[key]; }
  async function loadPublished() {
    if (state.published) return state.published;
    try { state.published = await getJSON(`${DATA}/published.json`); } catch { state.published = []; }
    state.publishedMap = {}; state.published.forEach(p => state.publishedMap[p.id] = p);
    return state.published;
  }
  async function loadOutline(id) {
    if (state.outlineCache[id]) return state.outlineCache[id];
    const o = await getJSON(`${DATA}/outlines/${id}.json`); state.outlineCache[id] = o; return o;
  }
  async function probeApi() { try { const r = await fetch(`${API}/health`); state.apiUp = r.ok; } catch { state.apiUp = false; } }
  const canRead = (id) => state.apiUp || !!state.publishedMap[id];

  // ---- markdown → HTML ----
  function mdInline(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>"); }
  function mdToHtml(md) {
    const lines = String(md || "").split("\n"); const out = []; let list = null;
    const close = () => { if (list) { out.push(`</${list}>`); list = null; } };
    for (const raw of lines) {
      const line = raw.trimEnd();
      if (!line.trim()) { close(); continue; }
      const ul = line.match(/^\s*-\s+(.*)$/), ol = line.match(/^\s*\d+\.\s+(.*)$/);
      if (ul) { if (list !== "ul") { close(); list = "ul"; out.push("<ul>"); } out.push(`<li>${mdInline(ul[1])}</li>`); }
      else if (ol) { if (list !== "ol") { close(); list = "ol"; out.push("<ol>"); } out.push(`<li>${mdInline(ol[1])}</li>`); }
      else { close(); out.push(`<p>${mdInline(line)}</p>`); }
    }
    close(); return out.join("\n");
  }

  // ---- router ----
  function setActive(route) { $$(".nav-item").forEach(a => a.classList.toggle("active", a.dataset.route === route)); }
  function router() {
    const hash = location.hash.slice(1) || "dashboard";
    const [route, ...rest] = hash.split("/");
    setActive(route);
    $("#sidebar").classList.remove("open");
    window.scrollTo(0, 0);
    const fn = routes[route] || routes.dashboard;
    view().innerHTML = `<div class="loading"><span class="spinner" style="display:inline-block;vertical-align:middle"></span> Loading…</div>`;
    Promise.resolve(fn(rest.join("/"))).catch(err => {
      view().innerHTML = `<div class="empty">Could not load this view.<br><small>${esc(err.message)}</small></div>`; console.error(err);
    });
  }

  // ---- shared UI ----
  function shortTitle(b) { return b.title.replace(b.category + ": ", ""); }
  function bookCover(b, cls = "book-cover") {
    return `<div class="${cls}" style="background:${catGradient(b.category_slug)}">
      <div class="bc-cat">${esc(b.category)}</div>
      <div class="bc-title">${esc(shortTitle(b))}</div>
      <div class="bc-foot"><span>${fmt(b.estimated_pages)} pp.</span><span>${readingTime(b.word_count)}</span></div></div>`;
  }
  function bookCard(b, i = 0) {
    const p = progress.get(b.id); const pct = p.total ? Math.round((p.ch / p.total) * 100) : 0;
    return `
    <div class="card" style="animation-delay:${Math.min(i * 30, 360)}ms">
      <a href="#read/${b.id}">${bookCover(b)}</a>
      <div class="meta">
        <span class="tag level lv-${b.level}">${esc(b.level)}</span>
        <span>${fmt(b.chapter_count)} ch.</span><span>${fmt(b.diagram_count)} diagrams</span>
      </div>
      ${pct ? `<div class="progress-track" title="${pct}% read"><span style="width:${pct}%"></span></div>` : ""}
      <div class="card-actions">
        <a class="btn primary" href="#read/${b.id}">${pct ? `Continue · ${pct}%` : "Read online"}</a>
        <button class="btn icon fav" data-id="${b.id}" title="Favorite">${favs.has(b.id) ? "★" : "☆"}</button>
      </div>
    </div>`;
  }
  function wireFavButtons(root) {
    $$(".fav", root).forEach(btn => btn.addEventListener("click", e => {
      e.preventDefault(); const on = favs.toggle(btn.dataset.id); btn.textContent = on ? "★" : "☆"; btn.style.color = on ? "#f59e0b" : "";
      toast(on ? "Added to favorites ★" : "Removed from favorites");
    }));
  }
  function animateCounters(root) {
    $$("[data-count]", root).forEach(el => {
      const target = +el.dataset.count, dur = 950, t0 = performance.now();
      const tick = (t) => { const k = Math.min(1, (t - t0) / dur); el.textContent = Math.round(target * (1 - Math.pow(1 - k, 3))).toLocaleString(); if (k < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    });
  }
  function animateBars(root) { requestAnimationFrame(() => $$(".bar > span", root).forEach(s => s.style.width = s.dataset.w + "%")); }

  // ---- views ----
  const routes = {};

  routes.dashboard = async () => {
    const [stats, cats] = await Promise.all([load("stats", `${DATA}/stats.json`), load("categories", `${DATA}/categories.json`)]);
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const t = stats.targets;
    const cards = [
      ["Books", stats.books, t.books], ["Pages", stats.pages, t.pages], ["Words", stats.words, t.words],
      ["Diagrams", stats.diagrams, t.diagrams], ["Code Samples", stats.code, t.code], ["Assessment Questions", stats.questions, t.questions],
    ].map(([label, val, tgt]) => {
      const pct = Math.min(100, Math.round((val / tgt) * 100));
      return `<div class="stat-card"><div class="label">${label}</div><div class="value" data-count="${val}">0</div>
        <div class="target">Target ${fmt(tgt)} — ${pct}%</div><div class="bar"><span data-w="${pct}"></span></div></div>`;
    }).join("");
    const featured = state.library.slice(0, 8);
    const recent = Object.entries(progress.all()).sort((a, b) => (b[1].t || 0) - (a[1].t || 0)).slice(0, 4)
      .map(([id]) => state.library.find(b => b.id === id)).filter(Boolean);
    view().innerHTML = `
      <div class="hero"><div class="orb a"></div><div class="orb b"></div>
        <h1>Read the world's most complete AI library</h1>
        <p>${fmt(stats.books)} professional, enterprise-grade AI books across ${stats.categories} categories — every title fully readable online with rendered diagrams, interactive quizzes and a distraction-free reader.</p>
        <div class="cta">
          <a class="btn cta-light" href="#library">Browse the library →</a>
          <a class="btn cta-white" href="#ask">✺ Ask Anything</a>
          <button class="btn cta-ghost" id="surprise">🎲 Surprise me</button>
        </div>
      </div>
      <div class="stat-grid">${cards}</div>
      ${recent.length ? `<h2 class="sec-h">Continue reading</h2><div class="continue">${recent.map(continueCard).join("")}</div>` : ""}
      <h2 class="sec-h">Featured titles</h2>
      <div class="cards">${featured.map((b, i) => bookCard(b, i)).join("")}</div>
      <h2 class="sec-h">Explore by category</h2>
      <div class="cat-grid">${cats.map((c, i) => `
        <a class="cat-tile" style="--g:${catGradient(c.slug)};animation-delay:${Math.min(i * 22, 360)}ms" href="#categories/${c.slug}">
          <div class="cat-swatch"></div>
          <div class="cat-body"><div class="cat-name">${esc(c.name)}</div><div class="cat-tag">${esc(c.tagline)}</div>
            <div class="cat-meta">${c.books} books · ${fmt(c.pages)} pp.</div></div>
        </a>`).join("")}</div>`;
    animateCounters(view()); animateBars(view()); wireFavButtons(view());
    $("#surprise").onclick = () => { const b = state.library[Math.floor(Math.random() * state.library.length)]; toast("Opening " + shortTitle(b)); location.hash = `read/${b.id}`; };
  };
  function continueCard(b) {
    const p = progress.get(b.id); const pct = p.total ? Math.round((p.ch / p.total) * 100) : 0;
    return `<a class="cont-card" href="#read/${b.id}" style="--g:${catGradient(b.category_slug)}">
      <div class="cont-ring">${ring(pct, 48)}</div>
      <div><div class="cont-title">${esc(shortTitle(b))}</div>
        <div class="cont-sub">${esc(b.category)} · Chapter ${p.ch || 1} of ${b.chapter_count}</div></div></a>`;
  }

  let libState = { page: 0, perPage: 24, cat: "", level: "", q: "", sort: "id" };
  routes.library = async (arg) => {
    await Promise.all([load("library", `${DATA}/library.json`), load("categories", `${DATA}/categories.json`), loadPublished()]);
    if (arg) libState.cat = arg; renderLibrary();
  };
  function renderLibrary() {
    let items = state.library.slice();
    if (libState.cat) items = items.filter(b => b.category_slug === libState.cat);
    if (libState.level) items = items.filter(b => b.level === libState.level);
    if (libState.q) { const q = libState.q.toLowerCase(); items = items.filter(b => (b.title + " " + b.subtitle + " " + b.keywords.join(" ")).toLowerCase().includes(q)); }
    if (libState.sort === "pages") items.sort((a, b) => b.estimated_pages - a.estimated_pages);
    else if (libState.sort === "title") items.sort((a, b) => a.title.localeCompare(b.title));
    else items.sort((a, b) => a.id.localeCompare(b.id));
    const total = items.length, pages = Math.max(1, Math.ceil(total / libState.perPage));
    libState.page = Math.min(libState.page, pages - 1);
    const slice = items.slice(libState.page * libState.perPage, (libState.page + 1) * libState.perPage);
    const catOpts = ['<option value="">All categories</option>']
      .concat(state.categories.map(c => `<option value="${c.slug}" ${libState.cat === c.slug ? "selected" : ""}>${esc(c.name)} (${c.books})</option>`)).join("");
    view().innerHTML = `
      <div class="page-head"><h1>Document Library</h1><p>Browse, filter and read all ${fmt(state.library.length)} books online.</p></div>
      <div class="toolbar">
        <select id="f-cat">${catOpts}</select>
        <select id="f-level">${["", "Foundational", "Intermediate", "Advanced"].map(l => `<option value="${l}" ${libState.level === l ? "selected" : ""}>${l || "All levels"}</option>`).join("")}</select>
        <select id="f-sort">${[["id", "Sort: catalog"], ["title", "Sort: title"], ["pages", "Sort: pages"]].map(([v, t]) => `<option value="${v}" ${libState.sort === v ? "selected" : ""}>${t}</option>`).join("")}</select>
        <input id="f-q" placeholder="Filter titles…" value="${esc(libState.q)}" />
        <span class="count-note">${fmt(total)} results</span>
      </div>
      <div class="cards" id="lib-cards">${slice.map((b, i) => bookCard(b, i)).join("") || '<div class="empty">No matching books.</div>'}</div>
      <div class="pager">
        <button class="btn" id="prev" ${libState.page === 0 ? "disabled" : ""}>‹ Prev</button>
        <span class="tag">Page ${libState.page + 1} / ${pages}</span>
        <button class="btn" id="next" ${libState.page >= pages - 1 ? "disabled" : ""}>Next ›</button>
      </div>`;
    wireFavButtons(view());
    $("#f-cat").onchange = e => { libState.cat = e.target.value; libState.page = 0; renderLibrary(); };
    $("#f-level").onchange = e => { libState.level = e.target.value; libState.page = 0; renderLibrary(); };
    $("#f-sort").onchange = e => { libState.sort = e.target.value; renderLibrary(); };
    let deb; $("#f-q").oninput = e => { clearTimeout(deb); deb = setTimeout(() => { libState.q = e.target.value; libState.page = 0; renderLibrary(); }, 200); };
    $("#prev").onclick = () => { libState.page--; renderLibrary(); window.scrollTo(0, 0); };
    $("#next").onclick = () => { libState.page++; renderLibrary(); window.scrollTo(0, 0); };
  }

  routes.categories = async (arg) => {
    await Promise.all([load("categories", `${DATA}/categories.json`), load("library", `${DATA}/library.json`), loadPublished()]);
    if (arg) { libState.cat = arg; libState.page = 0; return renderLibrary(); }
    view().innerHTML = `
      <div class="page-head"><h1>Categories</h1><p>${state.categories.length} subject areas, each with a full series of books.</p></div>
      <div class="cat-grid">${state.categories.map((c, i) => `
        <a class="cat-tile" style="--g:${catGradient(c.slug)};animation-delay:${Math.min(i * 20, 360)}ms" href="#categories/${c.slug}">
          <div class="cat-swatch"></div>
          <div class="cat-body"><div class="cat-name">${esc(c.name)}</div><div class="cat-tag">${esc(c.tagline)}</div>
            <div class="cat-meta">${c.books} books · ${fmt(c.pages)} pp. · ${fmt(c.diagrams)} diagrams</div></div>
        </a>`).join("")}</div>`;
  };

  routes.book = async (id) => {
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const b = state.library.find(x => x.id === id);
    if (!b) { view().innerHTML = `<div class="empty">Book not found.</div>`; return; }
    const outline = await loadOutline(id);
    const p = progress.get(id); const pct = p.total ? Math.round((p.ch / p.total) * 100) : 0;
    const topics = outline.chapters.slice(0, 12).map(c => `<a class="chip" href="#read/${id}">${esc(c.title)}</a>`).join("");
    const chapters = outline.chapters.map(c => `
      <a class="chapter-row" href="#read/${id}"><div class="num">${c.number}</div>
        <div><div class="ct">${esc(c.title)}</div><div class="cs">${esc(c.summary)}</div>
          <div class="chip-row">${c.sections.slice(0, 6).map(s => `<span class="chip">${esc(s)}</span>`).join("")}
            ${c.diagrams.length ? `<span class="chip">${c.diagrams.length} diagrams</span>` : ""}</div></div></a>`).join("");
    view().innerHTML = `
      <div class="btn-row" style="margin-bottom:16px"><a class="btn ghost" href="#library">‹ Library</a></div>
      <div class="detail-head">
        <div class="detail-cover" style="background:${catGradient(b.category_slug)}">
          <div><div class="bc-cat">${esc(b.category)}</div><div class="dc-title">${esc(shortTitle(b))}</div></div>
          <div style="font-size:.8rem;opacity:.92">${esc(b.level)} · ${fmt(b.estimated_pages)} pages · ${readingTime(b.word_count)}</div></div>
        <div class="detail-meta">
          <h1>${esc(b.title)}</h1><div class="sub">${esc(b.subtitle)}</div>
          <div class="kv"><span><b>${fmt(b.chapter_count)}</b> chapters</span><span><b>${fmt(b.estimated_pages)}</b> pages</span>
            <span><b>${fmt(b.word_count)}</b> words</span><span><b>${fmt(b.diagram_count)}</b> diagrams</span>
            <span><b>${fmt(b.code_count)}</b> code samples</span><span><b>${fmt(b.question_count)}</b> questions</span></div>
          <div class="kv"><span>Authors: <b>${esc(b.authors.join(", "))}</b></span><span>ISBN <b>${esc(b.isbn)}</b></span><span>v${esc(b.version)}</span></div>
          <div class="btn-row" style="align-items:center">
            <a class="btn primary lg" href="#read/${id}">${pct ? `Continue reading · ${pct}%` : "Start reading"}</a>
            ${pct ? `<span class="ring-wrap">${ring(pct, 44)}</span>` : ""}
            <button class="btn fav" data-id="${id}">${favs.has(id) ? "★ Favorited" : "☆ Favorite"}</button>
          </div>
        </div>
      </div>
      <div class="section-block"><h2>What you'll explore</h2><div class="chip-row">${topics}</div></div>
      <div class="section-block"><h2>About this book</h2><div>${mdToHtml(b.description)}</div></div>
      <div class="section-block"><h2>Table of contents (${outline.chapters.length} chapters)</h2><div class="chapter-list">${chapters}</div></div>`;
    wireFavButtons(view());
  };

  // ---- Immersive chapter reader ----
  let readerCtx = null;
  routes.read = async (id) => {
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const b = state.library.find(x => x.id === id);
    if (!b) { view().innerHTML = `<div class="empty">Book not found.</div>`; return; }
    let content = state.contentCache[id] || null;
    if (!content && state.apiUp) { try { content = await getJSON(`${API}/book/${id}`); state.contentCache[id] = content; } catch {} }
    const pub = state.publishedMap[id];
    if (!content && pub && pub.artifacts.content) { try { content = await getJSON(`${CONTENT}/${pub.artifacts.content}`); state.contentCache[id] = content; } catch {} }
    if (content) renderReader(b, content, id); else renderOutlinePreview(b);
  };

  function diagramHtml(d) {
    const svg = d.render_svg || (d.fmt === "svg" ? d.source : "");
    if (svg) return `<figure class="figure">${svg}<figcaption class="cap">${esc(d.caption)}</figcaption></figure>`;
    return `<figure class="figure"><pre class="fallback">${esc(d.source)}</pre><figcaption class="cap">${esc(d.fmt)} source</figcaption></figure>`;
  }
  function chapterWords(c) { let w = (c.sections || []).reduce((n, s) => n + (s.body ? s.body.split(/\s+/).length : 0), 0); w += (c.code_samples || []).reduce((n, cs) => n + cs.code.split(/\s+/).length, 0); return w; }

  function dropcap(html) { return html.replace("<p>", "<p class='dropcap'>"); }
  function tipCards(body, cls, icon) {
    const lines = body.split("\n"); let lead = ""; const cards = [];
    for (const ln of lines) { const m = ln.match(/^\s*-\s+(.*)/); if (m) cards.push(m[1]); else if (ln.trim()) lead += `<p>${mdInline(ln)}</p>`; }
    return lead + `<div class="tips">` + cards.map(c => `<div class="tip ${cls}"><span class="tip-ic">${icon}</span><div>${mdInline(c)}</div></div>`).join("") + `</div>`;
  }
  function calloutList(body) {
    const items = []; for (const ln of body.split("\n")) { const m = ln.match(/^\s*-\s+(.*)/); if (m) items.push(m[1]); }
    return `<div class="callout"><div class="callout-h">★ Key takeaways</div><ul>${items.map(i => `<li>${mdInline(i)}</li>`).join("")}</ul></div>`;
  }
  function sectionBlock(heading, body) {
    const h = heading.toLowerCase();
    if (h.includes("best practice")) return `<h2>${esc(heading)}</h2>${tipCards(body, "ok", "✓")}`;
    if (h.includes("pitfall")) return `<h2>${esc(heading)}</h2>${tipCards(body, "warn", "⚠")}`;
    if (h.includes("takeaway")) return `${calloutList(body)}`;
    if (h.startsWith("introduction") || h === "introduction") return `<h2>${esc(heading)}</h2>${dropcap(mdToHtml(body))}`;
    return `<h2>${esc(heading)}</h2>${mdToHtml(body)}`;
  }
  function quizBox(q, i) {
    if (q.answer_index < 0) return `<div class="qbox"><b>${i + 1}. ${esc(q.question)}</b><div class="ans show">💡 ${esc(q.explanation)}</div></div>`;
    return `<div class="qbox" data-ans="${q.answer_index}"><b>${i + 1}. ${esc(q.question)}</b><div class="opts">${q.options.map((o, j) => `<button class="opt" data-j="${j}">${String.fromCharCode(65 + j)}. ${esc(o)}</button>`).join("")}</div><div class="ans hidden">${esc(q.explanation)}</div></div>`;
  }
  function explainerHtml(c) {
    const steps = ["Problem", "Approach", "Design", "Build", "Evaluate", "Operate"];
    const yt = "https://www.youtube.com/results?search_query=" + encodeURIComponent(c.title + " explained");
    return `<div class="explainer">
      <div class="exp-head"><span class="exp-badge">\u25B6 Animated walkthrough</span>
        <a class="btn ghost" href="${yt}" target="_blank" rel="noopener">Watch real-world videos \u2197</a></div>
      ${explainerSVG(steps, c.title)}
      <div class="exp-cap">A looping, real-world walkthrough of how teams take \u201C${esc(c.title)}\u201D from problem to production. Use the link above for hands-on video tutorials.</div>
    </div>`;
  }
  function explainerSVG(steps, scenario) {
    const N = steps.length, slot = 1.5, total = (N * slot).toFixed(1);
    const VW = 820, VH = 210, pad = 26;
    const bw = (VW - 2 * pad - (N - 1) * 14) / N, y = 78, bh = 60;
    const xs = []; for (let i = 0; i < N; i++) xs.push(pad + i * (bw + 14));
    let boxes = "", labels = "", conns = "";
    for (let i = 0; i < N; i++) {
      const x = xs[i];
      boxes += `<rect x="${x.toFixed(0)}" y="${y}" width="${bw.toFixed(0)}" height="${bh}" rx="12" fill="#eef2ff" stroke="#c7d2fe"/>`;
      labels += `<text x="${(x + bw / 2).toFixed(0)}" y="${y + bh / 2 - 4}" text-anchor="middle" font-size="13" font-weight="800" fill="#1e293b">${esc(steps[i])}</text>`;
      labels += `<text x="${(x + bw / 2).toFixed(0)}" y="${y + bh / 2 + 15}" text-anchor="middle" font-size="9.5" fill="#64748b">step ${i + 1}</text>`;
      if (i < N - 1) conns += `<line x1="${(x + bw).toFixed(0)}" y1="${y + bh / 2}" x2="${(x + bw + 14).toFixed(0)}" y2="${y + bh / 2}" stroke="#cbd5e1" stroke-width="2"/>`;
    }
    const kt = []; for (let i = 0; i <= N; i++) kt.push((i / N).toFixed(3));
    const vals = xs.map(x => `${x.toFixed(0)} 0`).concat([`${xs[0].toFixed(0)} 0`]).join(";");
    const hl = `<rect x="0" y="${y}" width="${bw.toFixed(0)}" height="${bh}" rx="12" fill="#4338ca" fill-opacity="0.16" stroke="#4338ca" stroke-width="3">
      <animateTransform attributeName="transform" type="translate" dur="${total}s" repeatCount="indefinite" calcMode="discrete" keyTimes="${kt.join(";")}" values="${vals}"/></rect>`;
    const prog = `<rect x="${pad}" y="${VH - 24}" width="0" height="6" rx="3" fill="#4338ca"><animate attributeName="width" dur="${total}s" repeatCount="indefinite" values="0;${VW - 2 * pad}"/></rect>`;
    return `<svg viewBox="0 0 ${VW} ${VH}" class="exp-svg" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
      <rect width="${VW}" height="${VH}" rx="14" fill="#ffffff"/>
      <text x="${pad}" y="42" font-size="13" font-weight="700" fill="#0f172a">Real-world walkthrough</text>
      <circle cx="${VW - pad - 8}" cy="38" r="6" fill="#dc2626"><animate attributeName="opacity" dur="1.4s" repeatCount="indefinite" values="1;0.2;1"/></circle>
      <rect x="${pad}" y="${VH - 24}" width="${VW - 2 * pad}" height="6" rx="3" fill="#e2e8f0"/>
      ${conns}${boxes}${hl}${labels}${prog}</svg>`;
  }
  function chapterHtml(c, n, total) {
    const mins = Math.max(1, Math.round(chapterWords(c) / 220));
    const topics = (c.sections || []).map(s => s.heading).filter(hd => !/introduction|review|walkthrough|takeaway|check your/i.test(hd)).slice(0, 5);
    const diagrams = c.diagrams || [];
    const hasArch = (c.sections || []).some(s => /^Architecture/.test(s.heading));
    let sec = "";
    (c.sections || []).forEach(s => {
      sec += sectionBlock(s.heading, s.body);
      if (/^Introduction/.test(s.heading) && diagrams[0]) sec += diagramHtml(diagrams[0]);
      if (/^Architecture/.test(s.heading) && diagrams.length > 1) sec += diagrams.slice(1).map(diagramHtml).join("");
    });
    if (!hasArch && diagrams.length > 1) sec += diagrams.slice(1).map(diagramHtml).join("");
    const code = (c.code_samples || []).map(cs => `<h3>Listing: ${esc(cs.title)}</h3><pre><code>${esc(cs.code)}</code></pre>`).join("");
    const quiz = (c.questions || []).length ? `<h2>Check your understanding</h2>${(c.questions || []).map(quizBox).join("")}` : "";
    return `
      <div class="ch-hero">
        <div class="ch-kicker">Chapter ${n} of ${total}</div>
        <h1>${esc(c.title)}</h1>
        <div class="ch-meta"><span>📖 ~${mins} min read</span><span>🖼 ${diagrams.length} infographics</span><span>❓ ${(c.questions || []).length} questions</span></div>
        <p class="ch-summary">${esc(c.summary)}</p>
        ${topics.length ? `<div class="chip-row">${topics.map(t => `<span class="chip">${esc(t)}</span>`).join("")}</div>` : ""}
      </div>
      ${explainerHtml(c)}
      ${sec}${code}${quiz}
      <div class="ch-pager">
        <button class="btn" id="pg-prev" ${n <= 1 ? "disabled" : ""}>‹ Previous</button>
        <span class="tag">Chapter ${n} / ${total}</span>
        <button class="btn primary" id="pg-next">${n >= total ? "Finish ✓" : "Next chapter ›"}</button>
      </div>`;
  }
  function renderReader(b, content, id) {
    const total = content.chapters.length; const prefs = readerPrefs.get();
    const saved = progress.get(id); const startCh = Math.min(total, Math.max(1, saved.ch || 1));
    readerCtx = { id, b, content, total, current: startCh };
    const toc = content.chapters.map(c => `<a data-ch="${c.number}">${c.number}. ${esc(c.title)}</a>`).join("");
    view().innerHTML = `
      <div class="reader-bar">
        <a class="btn ghost" href="#book/${id}">‹ Details</a>
        <div class="rb-title">${esc(shortTitle(b))}</div>
        <div class="rb-tools">
          <button class="btn icon" id="font-dn" title="Smaller text">A−</button>
          <button class="btn icon" id="font-up" title="Larger text">A+</button>
          <button class="btn icon" id="width-tg" title="Toggle width">⇔</button>
          <button class="btn icon" id="bookmark-btn" title="Bookmark chapter">⚑</button>
          <span class="rb-ring" id="rb-ring"></span>
        </div>
      </div>
      <div class="reader ${prefs.wide ? "wide" : ""}" id="reader-wrap">
        <nav class="reader-toc" id="reader-toc">${toc}</nav>
        <article class="reader-body" id="reader-body" style="--rfs:${prefs.scale}rem"></article>
      </div>`;
    const applyFont = () => { $("#reader-body").style.setProperty("--rfs", prefs.scale.toFixed(2) + "rem"); readerPrefs.set(prefs); };
    $("#font-dn").onclick = () => { prefs.scale = Math.max(0.9, prefs.scale - 0.08); applyFont(); };
    $("#font-up").onclick = () => { prefs.scale = Math.min(1.5, prefs.scale + 0.08); applyFont(); };
    $("#width-tg").onclick = () => { prefs.wide = !prefs.wide; $("#reader-wrap").classList.toggle("wide", prefs.wide); readerPrefs.set(prefs); };
    $("#bookmark-btn").onclick = () => { const c = content.chapters[readerCtx.current - 1]; marks.add({ id, ch: readerCtx.current, title: b.title, chapter: c.title }); toast("⚑ Bookmarked Chapter " + readerCtx.current); };
    $$("#reader-toc a").forEach(a => a.onclick = () => showChapter(+a.dataset.ch));
    showChapter(startCh);
  }
  function showChapter(n) {
    const ctx = readerCtx; if (!ctx) return; n = Math.min(ctx.total, Math.max(1, n)); ctx.current = n;
    const c = ctx.content.chapters[n - 1]; const host = $("#reader-body");
    host.innerHTML = chapterHtml(c, n, ctx.total);
    host.animate([{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "none" }], { duration: 260, easing: "ease" });
    $$("#reader-toc a").forEach(a => a.classList.toggle("active", +a.dataset.ch === n));
    const act = $(`#reader-toc a[data-ch="${n}"]`); if (act) act.scrollIntoView({ block: "nearest" });
    const pct = Math.round(n / ctx.total * 100); $("#rb-ring").innerHTML = ring(pct, 34);
    progress.set(ctx.id, n, ctx.total); updateProgressPill();
    $$(".qbox[data-ans]", host).forEach(box => { const correct = +box.dataset.ans; $$(".opt", box).forEach(opt => opt.onclick = () => { if (box.classList.contains("answered")) return; box.classList.add("answered"); const j = +opt.dataset.j; $$(".opt", box).forEach(o => { const oj = +o.dataset.j; if (oj === correct) o.classList.add("correct"); else if (oj === j) o.classList.add("wrong"); o.disabled = true; }); $(".ans", box).classList.remove("hidden"); toast(j === correct ? "Correct! ✓" : "See the explanation"); }); });
    $("#pg-prev").onclick = () => showChapter(n - 1);
    $("#pg-next").onclick = () => { if (n >= ctx.total) toast("🎉 You finished the book — great work!"); else showChapter(n + 1); };
    window.scrollTo(0, 0); document.documentElement.scrollTop = 0; document.body.scrollTop = 0;
  }
  function renderOutlinePreview(b) {
    return loadOutline(b.id).then(outline => {
      const body = outline.chapters.map(c => `<section><h1>Chapter ${c.number}. ${esc(c.title)}</h1><p class="cap">${esc(c.summary)}</p><ul>${c.sections.map(s => `<li>${esc(s)}</li>`).join("")}</ul></section>`).join("");
      view().innerHTML = `
        <div class="btn-row" style="margin-bottom:14px"><a class="btn ghost" href="#book/${b.id}">‹ Details</a></div>
        <div class="section-block"><b>Outline preview.</b> Start the app server (<code>python serve.py</code>) to read the full text and infographics of this and every book online.</div>
        <article class="reader-body" style="--rfs:1.06rem">${body}</article>`;
    });
  }
  document.addEventListener("keydown", e => {
    if (!location.hash.startsWith("#read/") || !readerCtx) return;
    if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) return;
    if (e.key === "ArrowRight") { e.preventDefault(); showChapter(readerCtx.current + 1); }
    if (e.key === "ArrowLeft") { e.preventDefault(); showChapter(readerCtx.current - 1); }
  });

  // ---- Ask Anything ----
  const ASK_EXAMPLES = [
    "What is retrieval-augmented generation?", "How do I prevent prompt injection?",
    "When should I fine-tune vs use RAG?", "Best practices for LLM observability",
    "Explain the transformer attention mechanism", "How to govern AI under the EU AI Act?",
    "Difference between LoRA and full fine-tuning?", "How do agents use tools safely?",
  ];
  routes.ask = async (arg) => {
    const q = decodeURIComponent(arg || "");
    view().innerHTML = `
      <div class="page-head"><h1>✺ Ask Anything</h1><p>Ask a question and get a synthesised answer drawn from across the entire ${state.apiUp ? fmt(528) + "-book" : ""} corpus, with citations to the exact books and chapters to read next.</p></div>
      <div class="ask-box"><input id="ask-input" class="ask-input" placeholder="Ask anything about AI, LLMs, RAG, agents, governance…" value="${esc(q)}" /><button class="btn primary" id="ask-go">Ask</button></div>
      <div class="ask-chips">${ASK_EXAMPLES.map(e => `<button class="chip-btn" data-q="${esc(e)}">${esc(e)}</button>`).join("")}</div>
      <div id="ask-results"></div>`;
    const input = $("#ask-input");
    const go = () => { const v = input.value.trim(); if (v) { location.hash = `ask/${encodeURIComponent(v)}`; doAsk(v); } };
    $("#ask-go").onclick = go;
    input.addEventListener("keydown", e => { if (e.key === "Enter") go(); });
    $$(".chip-btn", view()).forEach(c => c.onclick = () => { input.value = c.dataset.q; go(); });
    input.focus(); if (q) doAsk(q);
  };
  async function doAsk(q) {
    const res = $("#ask-results");
    res.innerHTML = `<div class="ask-thinking"><span class="spinner"></span> Searching the library for the best answer…</div>`;
    let data;
    try { data = state.apiUp ? await getJSON(`${API}/ask?q=${encodeURIComponent(q)}`) : await clientAsk(q); }
    catch (e) { res.innerHTML = `<div class="empty">Could not complete the search.<br><small>${esc(e.message)}</small></div>`; return; }
    const terms = (data.terms || q.toLowerCase().split(/\s+/)).filter(t => t.length > 1);
    const sources = data.sources || [];
    res.innerHTML = `
      <div class="ask-answer"><div class="ask-answer-label">Answer</div><p>${hl(data.answer, terms)}</p></div>
      ${sources.length ? `<h2 class="sec-h">Sources — read these next</h2><div class="ask-sources">${sources.map(s => `
        <a class="ask-source" href="#read/${s.book_id}"><div class="as-top"><span class="tag level">${esc(s.category || "")}</span><span class="as-ch">${esc(s.chapter)}</span></div>
          <div class="as-title">${esc(s.book_title)}</div><div class="as-snip">${hl(s.snippet, terms)}</div><div class="as-cta">Open in reader →</div></a>`).join("")}</div>` : ""}
      <div class="ask-followups"><span class="cap">Try also:</span> ${ASK_EXAMPLES.slice(0, 4).map(e => `<button class="chip-btn" data-q="${esc(e)}">${esc(e)}</button>`).join("")}</div>`;
    $$(".ask-followups .chip-btn", res).forEach(c => c.onclick = () => { $("#ask-input").value = c.dataset.q; location.hash = `ask/${encodeURIComponent(c.dataset.q)}`; doAsk(c.dataset.q); });
    res.querySelector(".ask-answer").animate([{ opacity: 0, transform: "translateY(8px)" }, { opacity: 1, transform: "none" }], { duration: 300, easing: "ease" });
  }
  async function clientAsk(q) {
    await load("search", `${DATA}/search-index.json`);
    const terms = q.toLowerCase().split(/\s+/).filter(t => t.length > 1);
    const scored = [];
    for (const r of state.search) {
      const hay = (r.title + " " + r.subtitle + " " + r.category + " " + r.chapters.join(" ") + " " + r.text).toLowerCase();
      let score = 0; for (const t of terms) score += hay.split(t).length - 1;
      if (score) scored.push({ score, r });
    }
    scored.sort((a, b) => b.score - a.score);
    const top = scored.slice(0, 6);
    const answer = top.length ? `Across the library, the most relevant material on “${q}” is in ${top[0].r.category}. ${top[0].r.subtitle}. ${top.slice(0, 3).map(t => t.r.chapters.find(c => terms.some(x => c.toLowerCase().includes(x))) || "").filter(Boolean).map(c => "Key topic: " + c + ".").join(" ")}` : `I couldn't find anything about “${q}”. Try different keywords.`;
    return { answer, terms, sources: top.map(({ r }) => ({ book_id: r.id, book_title: r.title, category: r.category, chapter: (r.chapters.find(c => terms.some(x => c.toLowerCase().includes(x))) || r.chapters[0] || "Overview"), snippet: r.subtitle })) };
  }

  routes.search = async (arg) => {
    await load("search", `${DATA}/search-index.json`);
    const q = decodeURIComponent(arg || "");
    view().innerHTML = `
      <div class="page-head"><h1>Search</h1><p>Full-text search across ${fmt(state.search.length)} books, chapters and topics.</p></div>
      <div class="toolbar"><input id="search-box" style="flex:1" placeholder="Search topics, e.g. retrieval, transformers, governance…" value="${esc(q)}"/></div>
      <div id="search-results"></div>`;
    const box = $("#search-box"); const run = () => doSearch(box.value);
    let deb; box.oninput = () => { clearTimeout(deb); deb = setTimeout(run, 160); };
    box.focus(); if (q) run();
  };
  function doSearch(q) {
    const res = $("#search-results"); q = q.trim();
    if (!q) { res.innerHTML = `<div class="empty">Type to search across the whole library.</div>`; return; }
    const terms = q.toLowerCase().split(/\s+/); const scored = [];
    for (const r of state.search) {
      const hay = (r.title + " " + r.subtitle + " " + r.category + " " + r.chapters.join(" ") + " " + r.text + " " + r.keywords.join(" ")).toLowerCase();
      let score = 0; for (const t of terms) { const c = hay.split(t).length - 1; if (c) score += c; if (r.title.toLowerCase().includes(t)) score += 5; }
      if (score) { const chMatch = r.chapters.filter(c => terms.some(t => c.toLowerCase().includes(t))).slice(0, 3); scored.push({ r, score, chMatch }); }
    }
    scored.sort((a, b) => b.score - a.score);
    const top = scored.slice(0, 40);
    res.innerHTML = top.length ? `<div class="count-note" style="margin:0 0 12px">${scored.length} matches</div>` + top.map(({ r, chMatch }) => `
      <a class="result" href="#book/${r.id}"><h3>${hl(r.title, terms)} <span class="tag level">${esc(r.level)}</span></h3>
        <div class="snippet">${esc(r.category)} · ${fmt(r.pages)} pp. — ${hl(r.subtitle, terms)}</div>
        ${chMatch.length ? `<div class="snippet">Chapters: ${chMatch.map(c => hl(c, terms)).join(" · ")}</div>` : ""}</a>`).join("")
      : `<div class="empty">No results for “${esc(q)}”.</div>`;
  }
  function hl(text, terms) {
    let out = esc(text);
    (terms || []).forEach(t => { if (t && t.length > 1) out = out.replace(new RegExp(`(${t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig"), "<mark>$1</mark>"); });
    return out;
  }

  routes.diagrams = async () => {
    await Promise.all([load("library", `${DATA}/library.json`), load("stats", `${DATA}/stats.json`), loadPublished()]);
    const kinds = ["Architecture", "Application Flow", "Business Process", "Data Flow", "Sequence", "Class", "Component", "Deployment", "Network", "Cloud Architecture", "RAG Architecture", "Agent Architecture", "Security Architecture", "DevOps Pipeline", "CI/CD Pipeline", "Infrastructure", "Knowledge Graph", "Data Lineage", "Capability Map", "Operating Model"];
    const fmts = ["mermaid", "plantuml", "svg", "drawio"];
    const samples = [];
    if (state.apiUp) { for (const bk of state.library.slice(0, 3)) { try { const c = await getJSON(`${API}/book/${bk.id}`); c.chapters.forEach(ch => ch.diagrams.forEach(d => samples.push({ ...d, id: bk.id }))); } catch {} } }
    else { for (const id of (state.published || []).slice(0, 3).map(p => p.id)) { try { const c = await getJSON(`${CONTENT}/${state.publishedMap[id].artifacts.content}`); c.chapters.forEach(ch => ch.diagrams.forEach(d => samples.push({ ...d, id }))); } catch {} } }
    const gallery = samples.filter(d => d.render_svg).slice(0, 9).map(d => `<a class="figure" href="#read/${d.id}">${d.render_svg}<div class="cap">${esc(d.kind)} (${esc(d.fmt)})</div></a>`).join("");
    view().innerHTML = `
      <div class="page-head"><h1>Diagram Browser</h1><p>The library contains ${fmt(state.stats.diagrams)} professional diagrams across ${kinds.length} diagram types, rendered with 25 infographic templates and 12 curated colour palettes — over 200 distinct visual patterns — and exported as Mermaid, PlantUML, SVG and Draw.io.</p></div>
      <div class="section-block"><h2>Diagram types</h2><div class="chip-row">${kinds.map(k => `<span class="tag">${esc(k)}</span>`).join("")}</div></div>
      <div class="section-block"><h2>Source formats</h2><div class="chip-row">${fmts.map(f => `<span class="tag level">${esc(f)}</span>`).join("")}</div></div>
      ${gallery ? `<h2 class="sec-h">Live rendered examples</h2><div class="cards">${gallery}</div>` : ""}`;
  };

  const LEARNING_PATHS = [
    { name: "RAG Engineer", desc: "From embeddings to production retrieval-augmented generation.", steps: ["embeddings", "vector-databases", "rag", "graphrag", "ai-observability"] },
    { name: "LLM Application Developer", desc: "Build, prompt and ship LLM-powered applications.", steps: ["ai-foundations", "transformers", "llms", "prompt-engineering", "generative-ai", "llmops"] },
    { name: "Agentic AI Specialist", desc: "Design autonomous and multi-agent systems.", steps: ["llms", "agentic-ai", "multi-agent-systems", "mcp", "agentops"] },
    { name: "AI Platform Architect", desc: "Architect and operate enterprise AI platforms.", steps: ["ai-architecture", "mlops", "llmops", "ai-observability", "ai-security", "ai-governance"] },
    { name: "Model Customisation Expert", desc: "Adapt foundation models to your domain.", steps: ["fine-tuning", "peft", "lora", "rlhf"] },
    { name: "Responsible AI Lead", desc: "Govern AI safely, fairly and compliantly.", steps: ["responsible-ai", "ai-governance", "ai-security", "ai-testing"] },
  ];
  const CERT_PATHS = [
    { name: "Certified Enterprise AI Architect", desc: "Capstone certification across architecture, ops, security and governance.", steps: ["ai-architecture", "ai-security", "ai-governance", "mlops", "llmops"] },
    { name: "Certified Generative AI Practitioner", desc: "Foundations through applied generative AI and prompting.", steps: ["ai-foundations", "generative-ai", "prompt-engineering", "llms", "rag"] },
    { name: "Certified Agentic Systems Engineer", desc: "Autonomous agents, tools and operations.", steps: ["agentic-ai", "multi-agent-systems", "mcp", "agentops"] },
  ];
  function renderPaths(title, intro, paths) {
    return Promise.all([load("library", `${DATA}/library.json`), load("categories", `${DATA}/categories.json`)]).then(() => {
      const catName = s => (state.categories.find(c => c.slug === s) || {}).name || s;
      view().innerHTML = `
        <div class="page-head"><h1>${title}</h1><p>${intro}</p></div>
        ${paths.map(p => `<div class="path-card"><div style="font-weight:800;font-size:1.05rem">${esc(p.name)}</div>
          <div class="meta">${esc(p.desc)} · ${p.steps.length} stages · ~${p.steps.length * 280} pages</div>
          <div class="path-steps">${p.steps.map((s, i) => `<a class="path-step" href="#categories/${s}"><span class="n">${i + 1}</span>${esc(catName(s))}</a>`).join("")}</div></div>`).join("")}`;
    });
  }
  routes.paths = () => renderPaths("Learning Paths", "Curated, sequenced tracks from foundations to mastery. Click any stage to open its books.", LEARNING_PATHS);
  routes.certifications = () => renderPaths("Certification Paths", "Structured certification tracks. Read the books in order, then complete the assessment and certification questions in each.", CERT_PATHS);

  routes.favorites = async () => {
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const items = favs.list().map(id => state.library.find(b => b.id === id)).filter(Boolean);
    view().innerHTML = `<div class="page-head"><h1>Favorites</h1><p>${items.length} saved titles.</p></div>
      <div class="cards">${items.map((b, i) => bookCard(b, i)).join("") || '<div class="empty">No favorites yet. Tap the ☆ on any book.</div>'}</div>`;
    wireFavButtons(view());
  };
  routes.bookmarks = async () => {
    await load("library", `${DATA}/library.json`);
    const items = marks.list();
    view().innerHTML = `<div class="page-head"><h1>Bookmarks</h1><p>${items.length} saved chapter bookmarks.</p></div>
      ${items.length ? items.map(m => `<div class="result"><h3>${esc(m.title)}</h3><div class="snippet">Chapter ${m.ch}: ${esc(m.chapter || "")}</div>
        <div class="btn-row" style="margin-top:8px"><a class="btn primary" href="#read/${m.id}">Open</a><button class="btn rm" data-id="${m.id}" data-ch="${m.ch}">Remove</button></div></div>`).join("")
        : '<div class="empty">No bookmarks yet. Use the ⚑ button while reading.</div>'}`;
    $$(".rm", view()).forEach(b => b.onclick = () => { marks.remove(b.dataset.id, +b.dataset.ch); toast("Bookmark removed"); router(); });
  };

  // ---- chrome ----
  function updateProgressPill() {
    const all = progress.all(); const ids = Object.keys(all);
    const done = ids.filter(id => all[id].total && all[id].ch >= all[id].total).length;
    $("#progress-pill").textContent = ids.length ? `${ids.length} started · ${done} finished` : "";
  }
  async function updateSidebarStats() {
    try { const s = await load("stats", `${DATA}/stats.json`);
      $("#sidebar-stats").innerHTML = `<b>${fmt(s.books)}</b> books · <b>${fmt(s.pages)}</b> pages<br><b>${fmt(s.words)}</b> words · <b>${fmt(s.diagrams)}</b> diagrams`;
    } catch { $("#sidebar-stats").textContent = "Run the engine catalog command."; }
  }
  function initTheme() {
    const saved = store.get("aiu:theme", null);
    if (saved) document.documentElement.dataset.theme = saved;
    $("#theme-toggle").onclick = () => { const dark = document.documentElement.dataset.theme === "dark"; document.documentElement.dataset.theme = dark ? "" : "dark"; store.set("aiu:theme", dark ? "" : "dark"); };
  }
  function initScrollChrome() {
    const bar = $("#reading-progress"), top = $("#to-top");
    const onScroll = () => { const h = document.documentElement; const max = h.scrollHeight - h.clientHeight; bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%"; top.classList.toggle("show", h.scrollTop > 420); };
    window.addEventListener("scroll", onScroll, { passive: true });
    top.onclick = () => window.scrollTo({ top: 0, behavior: "smooth" });
  }
  async function init() {
    initTheme(); updateSidebarStats(); updateProgressPill(); initScrollChrome();
    $("#hamburger").onclick = () => $("#sidebar").classList.toggle("open");
    const gs = $("#global-search-input");
    gs.addEventListener("keydown", e => { if (e.key === "Enter" && gs.value.trim()) location.hash = `search/${encodeURIComponent(gs.value.trim())}`; });
    document.addEventListener("keydown", e => { if (e.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); gs.focus(); } });
    window.addEventListener("hashchange", router);
    await probeApi();
    router();
  }
  document.addEventListener("DOMContentLoaded", init);
})();
