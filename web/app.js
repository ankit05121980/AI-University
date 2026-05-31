/* AI-University portal — framework-free SPA.
 * Talks to the serve.py API (full read-online + downloads + Ask Anything for
 * every book), with graceful fallback to the committed demo corpus + static
 * search index when no API is available. */
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

  // ---- helpers ----
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const view = () => $("#view");
  const fmt = (n) => (n == null ? "—" : Number(n).toLocaleString());
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

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

  // a book can be fully read online if the API is up (any book) or it is in the demo corpus
  const canRead = (id) => state.apiUp || !!state.publishedMap[id];
  function dlUrl(id, k, pub) { return state.apiUp ? `${API}/download/${id}/${k}` : (pub ? `${CONTENT}/${pub.artifacts[k]}` : "#"); }
  function downloadLinks(id, pub, only) {
    const fmts = [["pdf", "PDF"], ["docx", "DOCX"], ["pptx", "PPTX"], ["html", "HTML"], ["md", "Markdown"]];
    return fmts.filter(([k]) => (only ? only.includes(k) : true) && (state.apiUp || (pub && pub.artifacts[k])))
      .map(([k, l]) => `<a class="btn" href="${dlUrl(id, k, pub)}" download>${l}</a>`).join("");
  }

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

  // ---- nav / router ----
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
  function bookCard(b, i = 0) {
    const pub = state.publishedMap[b.id];
    const available = state.apiUp || pub;
    const p = progress.get(b.id); const pct = p.total ? Math.round((p.ch / p.total) * 100) : 0;
    return `
    <div class="card" style="animation-delay:${Math.min(i * 35, 400)}ms">
      <a href="#book/${b.id}"><div class="book-cover">
        <div class="bc-cat">${esc(b.category)}</div>
        <div class="bc-title">${esc(b.title.replace(b.category + ": ", ""))}</div></div></a>
      <div class="meta">
        <span class="tag level">${esc(b.level)}</span>
        <span>${fmt(b.estimated_pages)} pp.</span><span>${fmt(b.chapter_count)} ch.</span><span>${fmt(b.diagram_count)} dia.</span>
        ${available ? '<span class="tag pub">Read &amp; download</span>' : ""}
      </div>
      ${pct ? `<div class="progress-track" title="${pct}% read"><span style="width:${pct}%"></span></div>` : ""}
      <div class="card-actions">
        <a class="btn primary" href="#read/${b.id}">Read online</a>
        ${available ? `<a class="btn" href="${dlUrl(b.id, "pdf", pub)}" download>PDF</a>` : ""}
        <button class="btn icon fav" data-id="${b.id}" title="Favorite">${favs.has(b.id) ? "★" : "☆"}</button>
      </div>
    </div>`;
  }
  function wireFavButtons(root) {
    $$(".fav", root).forEach(btn => btn.addEventListener("click", e => {
      e.preventDefault(); const on = favs.toggle(btn.dataset.id); btn.textContent = on ? "★" : "☆"; btn.style.color = on ? "#f59e0b" : "";
    }));
  }
  function animateCounters(root) {
    $$("[data-count]", root).forEach(el => {
      const target = +el.dataset.count, dur = 900, t0 = performance.now();
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
        <h1>Enterprise AI Knowledge Library</h1>
        <p>${fmt(stats.books)} professional, enterprise-grade AI books across ${stats.categories} categories — every title fully readable online with diagrams, searchable, and downloadable as PDF, DOCX, PPTX, HTML and Markdown.</p>
        <div class="cta"><a class="btn" style="background:rgba(255,255,255,.16);color:#fff;border:none" href="#library">Browse the library →</a>
          <a class="btn" style="background:#fff;color:var(--accent);border:none" href="#ask">✺ Ask Anything</a></div>
        ${state.apiUp ? "" : `<p style="margin-top:10px;font-size:.82rem;opacity:.9">Tip: run <code>python serve.py</code> to read &amp; download all ${fmt(stats.books)} books (you appear to be on a static server, so only the ${state.published.length} demo books are fully available).</p>`}
      </div>
      <div class="stat-grid">${cards}</div>
      ${recent.length ? `<h2 style="margin:28px 0 12px">Continue reading</h2><div class="cards">${recent.map((b, i) => bookCard(b, i)).join("")}</div>` : ""}
      <h2 style="margin:28px 0 12px">Featured titles</h2>
      <div class="cards">${featured.map((b, i) => bookCard(b, i)).join("")}</div>
      <h2 style="margin:28px 0 12px">Browse by category</h2>
      <div class="cards">${cats.map((c, i) => `
        <a class="card" style="animation-delay:${Math.min(i * 25, 400)}ms" href="#categories/${c.slug}">
          <div style="font-weight:800">${esc(c.name)}</div><div class="meta">${esc(c.tagline)}</div>
          <div class="meta"><span>${c.books} books</span><span>${fmt(c.pages)} pp.</span><span>${fmt(c.diagrams)} dia.</span></div>
        </a>`).join("")}</div>`;
    animateCounters(view()); animateBars(view()); wireFavButtons(view());
  };

  let libState = { page: 0, perPage: 24, cat: "", level: "", q: "", sort: "id", pubOnly: false };
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
      <div class="cards">${state.categories.map((c, i) => `
        <a class="card" style="animation-delay:${Math.min(i * 25, 400)}ms" href="#categories/${c.slug}">
          <div class="book-cover"><div class="bc-cat">${c.books} books</div><div class="bc-title">${esc(c.name)}</div></div>
          <div class="meta">${esc(c.tagline)}</div>
          <div class="meta"><span>${fmt(c.pages)} pp.</span><span>${fmt(c.words)} words</span><span>${fmt(c.diagrams)} diagrams</span></div>
        </a>`).join("")}</div>`;
  };

  routes.book = async (id) => {
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const b = state.library.find(x => x.id === id);
    if (!b) { view().innerHTML = `<div class="empty">Book not found.</div>`; return; }
    const outline = await loadOutline(id);
    const pub = state.publishedMap[id];
    const dls = downloadLinks(id, pub);
    const chapters = outline.chapters.map(c => `
      <div class="chapter-row"><div class="num">${c.number}</div>
        <div><div class="ct">${esc(c.title)}</div><div class="cs">${esc(c.summary)}</div>
          <div class="chip-row">${c.sections.slice(0, 6).map(s => `<span class="chip">${esc(s)}</span>`).join("")}
            ${c.diagrams.length ? `<span class="chip">${c.diagrams.length} diagrams</span>` : ""}</div></div></div>`).join("");
    view().innerHTML = `
      <div class="btn-row" style="margin-bottom:16px"><a class="btn ghost" href="#library">‹ Library</a></div>
      <div class="detail-head">
        <div class="detail-cover"><div><div class="bc-cat">${esc(b.category)}</div><div class="dc-title">${esc(b.title.replace(b.category + ": ", ""))}</div></div>
          <div style="font-size:.8rem;opacity:.9">${esc(b.level)} · ${fmt(b.estimated_pages)} pages</div></div>
        <div class="detail-meta">
          <h1>${esc(b.title)}</h1><div class="sub">${esc(b.subtitle)}</div>
          <div class="kv"><span><b>${fmt(b.chapter_count)}</b> chapters</span><span><b>${fmt(b.estimated_pages)}</b> pages</span>
            <span><b>${fmt(b.word_count)}</b> words</span><span><b>${fmt(b.diagram_count)}</b> diagrams</span>
            <span><b>${fmt(b.code_count)}</b> code samples</span><span><b>${fmt(b.question_count)}</b> questions</span></div>
          <div class="kv"><span>Authors: <b>${esc(b.authors.join(", "))}</b></span><span>ISBN <b>${esc(b.isbn)}</b></span><span>v${esc(b.version)}</span></div>
          <div class="btn-row"><a class="btn primary" href="#read/${id}">${canRead(id) ? "Read online" : "Preview outline"}</a>
            <button class="btn fav" data-id="${id}">${favs.has(id) ? "★ Favorited" : "☆ Favorite"}</button>${dls}</div>
          ${!canRead(id) ? `<p class="cap" style="margin-top:12px">Run <code>python serve.py</code> from the repo root to read and download this and all ${fmt(state.library.length)} books online.</p>` : ""}
        </div>
      </div>
      <div class="section-block"><h2>About this book</h2><div>${mdToHtml(b.description)}</div></div>
      <div class="section-block"><h2>Table of contents (${outline.chapters.length} chapters)</h2><div class="chapter-list">${chapters}</div></div>`;
    wireFavButtons(view());
  };

  routes.read = async (id) => {
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const b = state.library.find(x => x.id === id);
    if (!b) { view().innerHTML = `<div class="empty">Book not found.</div>`; return; }
    let content = state.contentCache[id] || null;
    if (!content && state.apiUp) { try { content = await getJSON(`${API}/book/${id}`); state.contentCache[id] = content; } catch {} }
    const pub = state.publishedMap[id];
    if (!content && pub && pub.artifacts.content) { try { content = await getJSON(`${CONTENT}/${pub.artifacts.content}`); state.contentCache[id] = content; } catch {} }
    if (content) renderReader(b, content, id, pub); else renderOutlinePreview(b);
  };

  function diagramHtml(d) {
    const svg = d.render_svg || (d.fmt === "svg" ? d.source : "");
    if (svg) return `<div class="figure">${svg}<div class="cap">${esc(d.caption)}</div></div>`;
    return `<div class="figure"><pre class="fallback">${esc(d.source)}</pre><div class="cap">${esc(d.fmt)} source — ${esc(d.caption)}</div></div>`;
  }

  function renderReader(b, content, id, pub) {
    const toc = content.chapters.map(c => `<a href="#ch-${c.number}" data-ch="${c.number}">${c.number}. ${esc(c.title)}</a>`).join("");
    const body = content.chapters.map(c => {
      let html = `<h1 id="ch-${c.number}">Chapter ${c.number}. ${esc(c.title)}</h1><p class="cap">${esc(c.summary)}</p>`;
      for (const s of c.sections) {
        html += `<h2>${esc(s.heading)}</h2>${mdToHtml(s.body)}`;
        if (s.heading.startsWith("Architecture")) html += (c.diagrams || []).map(diagramHtml).join("");
      }
      for (const cs of (c.code_samples || [])) html += `<h3>Listing: ${esc(cs.title)}</h3><pre><code>${esc(cs.code)}</code></pre>`;
      html += `<h2>Review Questions</h2>` + (c.questions || []).map((q, i) => {
        if (q.answer_index < 0) return `<div class="qbox"><b>${i + 1}. ${esc(q.question)}</b><div class="ans">Guidance: ${esc(q.explanation)}</div></div>`;
        return `<div class="qbox"><b>${i + 1}. ${esc(q.question)}</b>${q.options.map((o, j) => `<span class="opt">${String.fromCharCode(65 + j)}. ${esc(o)}</span>`).join("")}
          <button class="btn ghost reveal">Reveal answer</button><div class="ans hidden">Answer ${String.fromCharCode(65 + q.answer_index)}. ${esc(q.explanation)}</div></div>`;
      }).join("");
      return `<section class="rch" data-ch="${c.number}">${html}</section>`;
    }).join("");
    const dls = downloadLinks(id, pub, ["pdf", "docx", "pptx", "md"]);
    view().innerHTML = `
      <div class="btn-row" style="margin-bottom:14px"><a class="btn ghost" href="#book/${id}">‹ Details</a>${dls}
        ${(state.apiUp || (pub && pub.artifacts.pdf)) ? `<a class="btn" href="${dlUrl(id, "pdf", pub)}" target="_blank">Open PDF ↗</a>` : ""}
        <button class="btn" id="bookmark-btn">⚑ Bookmark current chapter</button></div>
      <div class="reader"><nav class="reader-toc">${toc}</nav><article class="reader-body" id="reader-body">${body}</article></div>`;
    progress.set(b.id, 0, content.chapters.length);
    $$(".qbox .reveal", view()).forEach(btn => btn.onclick = () => { const a = btn.nextElementSibling; a.classList.toggle("hidden"); btn.textContent = a.classList.contains("hidden") ? "Reveal answer" : "Hide answer"; });
    const tocLinks = $$(".reader-toc a", view()), sections = $$(".rch", view());
    let current = 1;
    const obs = new IntersectionObserver((entries) => entries.forEach(en => {
      if (en.isIntersecting) { current = +en.target.dataset.ch; tocLinks.forEach(a => a.classList.toggle("active", +a.dataset.ch === current)); progress.set(b.id, current, content.chapters.length); updateProgressPill(); }
    }), { rootMargin: "-15% 0px -75% 0px" });
    sections.forEach(s => obs.observe(s));
    $("#bookmark-btn").onclick = () => { const c = content.chapters[current - 1]; marks.add({ id: b.id, ch: current, title: b.title, chapter: c.title }); $("#bookmark-btn").textContent = "⚑ Bookmarked!"; setTimeout(() => $("#bookmark-btn").textContent = "⚑ Bookmark current chapter", 1500); };
  }

  function renderOutlinePreview(b) {
    return loadOutline(b.id).then(outline => {
      const body = outline.chapters.map(c => `<section><h1>Chapter ${c.number}. ${esc(c.title)}</h1><p class="cap">${esc(c.summary)}</p><ul>${c.sections.map(s => `<li>${esc(s)}</li>`).join("")}</ul></section>`).join("");
      view().innerHTML = `
        <div class="btn-row" style="margin-bottom:14px"><a class="btn ghost" href="#book/${b.id}">‹ Details</a></div>
        <div class="section-block"><b>Outline preview.</b> Start the app server (<code>python serve.py</code>) to read the full text and diagrams of this and every book online.</div>
        <article class="reader-body">${body}</article>`;
    });
  }

  // ---- Ask Anything ----
  const ASK_EXAMPLES = [
    "What is retrieval-augmented generation?",
    "How do I prevent prompt injection?",
    "When should I fine-tune vs use RAG?",
    "Best practices for LLM observability",
    "Explain the transformer attention mechanism",
    "How to govern AI under the EU AI Act?",
    "What is the difference between LoRA and full fine-tuning?",
    "How do agents use tools safely?",
  ];
  routes.ask = async (arg) => {
    const q = decodeURIComponent(arg || "");
    view().innerHTML = `
      <div class="page-head"><h1>✺ Ask Anything</h1><p>Ask a question and get a synthesised answer drawn from across the entire ${state.apiUp ? "528-book" : "library"} corpus, with citations to the exact books and chapters to read next.</p></div>
      <div class="ask-box">
        <input id="ask-input" class="ask-input" placeholder="Ask anything about AI, LLMs, RAG, agents, governance…" value="${esc(q)}" />
        <button class="btn primary" id="ask-go">Ask</button>
      </div>
      <div class="ask-chips">${ASK_EXAMPLES.map(e => `<button class="chip-btn" data-q="${esc(e)}">${esc(e)}</button>`).join("")}</div>
      <div id="ask-results"></div>`;
    const input = $("#ask-input");
    const go = () => { const v = input.value.trim(); if (v) { location.hash = `ask/${encodeURIComponent(v)}`; doAsk(v); } };
    $("#ask-go").onclick = go;
    input.addEventListener("keydown", e => { if (e.key === "Enter") go(); });
    $$(".chip-btn", view()).forEach(c => c.onclick = () => { input.value = c.dataset.q; go(); });
    input.focus();
    if (q) doAsk(q);
  };

  async function doAsk(q) {
    const res = $("#ask-results");
    res.innerHTML = `<div class="ask-thinking"><span class="spinner"></span> Searching the library for the best answer…</div>`;
    let data;
    try {
      if (state.apiUp) data = await getJSON(`${API}/ask?q=${encodeURIComponent(q)}`);
      else data = await clientAsk(q);
    } catch (e) { res.innerHTML = `<div class="empty">Could not complete the search.<br><small>${esc(e.message)}</small></div>`; return; }
    const terms = (data.terms || q.toLowerCase().split(/\s+/)).filter(t => t.length > 1);
    const sources = data.sources || [];
    res.innerHTML = `
      <div class="ask-answer">
        <div class="ask-answer-label">Answer</div>
        <p>${hl(data.answer, terms)}</p>
      </div>
      ${sources.length ? `<h2 style="margin:22px 0 12px">Sources — read these next</h2>
        <div class="ask-sources">${sources.map(s => `
          <a class="ask-source" href="#read/${s.book_id}">
            <div class="as-top"><span class="tag level">${esc(s.category || "")}</span><span class="as-ch">${esc(s.chapter)}</span></div>
            <div class="as-title">${esc(s.book_title)}</div>
            <div class="as-snip">${hl(s.snippet, terms)}</div>
            <div class="as-cta">Open in reader →</div>
          </a>`).join("")}</div>` : ""}
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
    const answer = top.length ? `Across the library, the most relevant material on “${q}” is found in ${top[0].r.category}. ${top[0].r.subtitle}. ${top.slice(0, 3).map(t => t.r.chapters.find(c => terms.some(x => c.toLowerCase().includes(x))) || "").filter(Boolean).map(c => "Key topic: " + c + ".").join(" ")}`
      : `I couldn't find anything about “${q}”. Try different keywords.`;
    return { answer, terms, sources: top.map(({ r }) => ({ book_id: r.id, book_title: r.title, category: r.category, chapter: (r.chapters.find(c => terms.some(x => c.toLowerCase().includes(x))) || r.chapters[0] || "Overview"), snippet: r.subtitle })) };
  }

  // Search
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
    // pull a few rendered SVGs to preview, via API if available else demo outlines
    const samples = [];
    if (state.apiUp) {
      const ids = state.library.slice(0, 3).map(b => b.id);
      for (const id of ids) { try { const c = await getJSON(`${API}/book/${id}`); c.chapters.forEach(ch => ch.diagrams.forEach(d => samples.push({ ...d, id }))); } catch {} }
    }
    const gallery = samples.slice(0, 9).filter(d => d.render_svg).map(d => `<div class="figure">${d.render_svg}<div class="cap">${esc(d.kind)} (${esc(d.fmt)})</div></div>`).join("");
    view().innerHTML = `
      <div class="page-head"><h1>Diagram Browser</h1><p>The library contains ${fmt(state.stats.diagrams)} professional diagrams in Mermaid, PlantUML, SVG and Draw.io across ${kinds.length} diagram types.</p></div>
      <div class="section-block"><h2>Diagram types</h2><div class="chip-row">${kinds.map(k => `<span class="tag">${esc(k)}</span>`).join("")}</div></div>
      <div class="section-block"><h2>Source formats</h2><div class="chip-row">${fmts.map(f => `<span class="tag level">${esc(f)}</span>`).join("")}</div></div>
      ${gallery ? `<h2 style="margin:20px 0 12px">Live rendered examples</h2><div class="cards">${gallery}</div>` : ""}`;
  };

  routes.downloads = async () => {
    await Promise.all([loadPublished(), load("library", `${DATA}/library.json`)]);
    const list = state.apiUp ? state.library : (state.published || []);
    const rows = list.slice(0, state.apiUp ? 60 : list.length).map(p => {
      const id = p.id; const pub = state.publishedMap[id];
      return `<div class="result"><h3>${esc(p.title)}</h3>
        <div class="snippet">${esc(p.category)} · ${esc(p.level)} · ${fmt(p.estimated_pages)} pp.</div>
        <div class="btn-row" style="margin-top:8px">${downloadLinks(id, pub)} <a class="btn ghost" href="#read/${id}">Read online</a></div></div>`;
    }).join("");
    view().innerHTML = `
      <div class="page-head"><h1>Download Center</h1>
        <p>${state.apiUp ? `Every one of the ${fmt(state.library.length)} books is downloadable in five formats (generated on demand). Showing the first 60 — use the Library to find any title.` : `${(state.published || []).length} demo titles are pre-rendered. Run <code>python serve.py</code> to download all ${fmt(state.library.length)}.`}</p></div>
      ${rows || '<div class="empty">No books available.</div>'}`;
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
        : '<div class="empty">No bookmarks yet. Use “Bookmark current chapter” while reading.</div>'}`;
    $$(".rm", view()).forEach(b => b.onclick = () => { marks.remove(b.dataset.id, +b.dataset.ch); router(); });
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
