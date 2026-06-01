/* AI-University portal — framework-free SPA.
 * Reads the engine's generated JSON (library, categories, stats, search index,
 * per-book outlines) and the published content/ artefacts. */
(() => {
  "use strict";

  // Local dev (serve.py): relative paths. Production hosts: CDN from this repo on GitHub.
  const CDN_BASE = "https://cdn.jsdelivr.net/gh/ankit05121980/AI-University@main";
  const isLocalHost = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  const DATA = isLocalHost ? "../data" : `${CDN_BASE}/data`;
  const CONTENT = isLocalHost ? "../content" : `${CDN_BASE}/content`;

  const state = {
    library: null, categories: null, stats: null, search: null,
    published: null, outlineCache: {}, contentCache: {},
  };

  // ---- storage ----
  const store = {
    get(key, def) { try { return JSON.parse(localStorage.getItem(key)) ?? def; } catch { return def; } },
    set(key, val) { localStorage.setItem(key, JSON.stringify(val)); },
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
  const view = () => $("#view");
  const fmt = (n) => (n == null ? "—" : n.toLocaleString());
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  function el(html) { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; }

  async function getJSON(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`${r.status} ${url}`);
    return r.json();
  }
  async function load(key, url) {
    if (state[key]) return state[key];
    state[key] = await getJSON(url);
    return state[key];
  }
  async function loadPublished() {
    if (state.published) return state.published;
    try { state.published = await getJSON(`${DATA}/published.json`); }
    catch { state.published = []; }
    state.publishedMap = {};
    state.published.forEach(p => state.publishedMap[p.id] = p);
    return state.published;
  }
  async function loadOutline(id) {
    if (state.outlineCache[id]) return state.outlineCache[id];
    const o = await getJSON(`${DATA}/outlines/${id}.json`);
    state.outlineCache[id] = o; return o;
  }

  // ---- minimal markdown → HTML for section bodies ----
  function mdInline(s) {
    return esc(s)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/`([^`]+)`/g, "<code>$1</code>");
  }
  function mdToHtml(md) {
    const lines = md.split("\n");
    const out = [];
    let list = null; // 'ul' | 'ol'
    const closeList = () => { if (list) { out.push(`</${list}>`); list = null; } };
    for (const raw of lines) {
      const line = raw.trimEnd();
      if (!line.trim()) { closeList(); continue; }
      const ul = line.match(/^\s*-\s+(.*)$/);
      const ol = line.match(/^\s*\d+\.\s+(.*)$/);
      if (ul) { if (list !== "ul") { closeList(); list = "ul"; out.push("<ul>"); } out.push(`<li>${mdInline(ul[1])}</li>`); }
      else if (ol) { if (list !== "ol") { closeList(); list = "ol"; out.push("<ol>"); } out.push(`<li>${mdInline(ol[1])}</li>`); }
      else { closeList(); out.push(`<p>${mdInline(line)}</p>`); }
    }
    closeList();
    return out.join("\n");
  }

  // ---- nav ----
  function setActive(route) {
    document.querySelectorAll(".nav-item").forEach(a => a.classList.toggle("active", a.dataset.route === route));
  }

  function router() {
    const hash = location.hash.slice(1) || "dashboard";
    const [route, ...rest] = hash.split("/");
    const arg = rest.join("/");
    setActive(route);
    $("#sidebar").classList.remove("open");
    const fn = routes[route] || routes.dashboard;
    view().innerHTML = `<div class="loading">Loading…</div>`;
    Promise.resolve(fn(arg)).catch(err => {
      view().innerHTML = `<div class="empty">Could not load this view.<br><small>${esc(err.message)}</small><br><br>Make sure you are serving the repository root (see README) so that <code>/data</code> and <code>/content</code> are reachable.</div>`;
      console.error(err);
    });
  }

  // ---- shared UI ----
  function bookCard(b) {
    const pub = state.publishedMap && state.publishedMap[b.id];
    const p = progress.get(b.id);
    const pct = p.total ? Math.round((p.ch / p.total) * 100) : 0;
    return `
    <div class="card">
      <a href="#book/${b.id}">
        <div class="book-cover">
          <div class="bc-cat">${esc(b.category)}</div>
          <div class="bc-title">${esc(b.title.replace(b.category + ": ", ""))}</div>
        </div>
      </a>
      <div class="meta">
        <span class="tag level">${esc(b.level)}</span>
        <span>${fmt(b.estimated_pages)} pp.</span>
        <span>${fmt(b.chapter_count)} ch.</span>
        <span>${fmt(b.diagram_count)} dia.</span>
        ${pub ? '<span class="tag pub">Downloadable</span>' : ""}
      </div>
      ${pct ? `<div class="progress-track"><span style="width:${pct}%"></span></div>` : ""}
      <div class="card-actions">
        <a class="btn primary" href="#book/${b.id}">Open</a>
        ${pub ? `<a class="btn" href="${CONTENT}/${pub.artifacts.pdf}" download>PDF</a>` : ""}
        <button class="btn icon fav" data-id="${b.id}" title="Favorite">${favs.has(b.id) ? "★" : "☆"}</button>
      </div>
    </div>`;
  }

  function wireFavButtons(root) {
    root.querySelectorAll(".fav").forEach(btn => btn.addEventListener("click", e => {
      e.preventDefault();
      const on = favs.toggle(btn.dataset.id);
      btn.textContent = on ? "★" : "☆";
    }));
  }

  // ---- views ----
  const routes = {};

  routes.dashboard = async () => {
    const [stats, cats] = await Promise.all([
      load("stats", `${DATA}/stats.json`),
      load("categories", `${DATA}/categories.json`),
    ]);
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const t = stats.targets;
    const cards = [
      ["Books", stats.books, t.books], ["Pages", stats.pages, t.pages],
      ["Words", stats.words, t.words], ["Diagrams", stats.diagrams, t.diagrams],
      ["Code Samples", stats.code, t.code], ["Assessment Questions", stats.questions, t.questions],
    ].map(([label, val, tgt]) => {
      const pct = Math.min(100, Math.round((val / tgt) * 100));
      return `<div class="stat-card"><div class="label">${label}</div><div class="value">${fmt(val)}</div>
        <div class="target">Target ${fmt(tgt)} — ${pct}%</div><div class="bar"><span style="width:${pct}%"></span></div></div>`;
    }).join("");

    const featured = state.library.filter(b => state.publishedMap[b.id]).slice(0, 8)
      .concat(state.library.slice(0, 8)).slice(0, 8);

    const recent = Object.entries(progress.all()).sort((a, b) => (b[1].t || 0) - (a[1].t || 0)).slice(0, 4)
      .map(([id]) => state.library.find(b => b.id === id)).filter(Boolean);

    view().innerHTML = `
      <div class="page-head"><h1>Enterprise AI Knowledge Library</h1>
        <p>An automated publishing platform with ${fmt(stats.books)} professional AI books across ${stats.categories} categories — every title professionally formatted, searchable, viewable online and downloadable as PDF, DOCX, PPTX, HTML and Markdown.</p></div>
      <div class="stat-grid">${cards}</div>
      ${recent.length ? `<h2 style="margin:28px 0 12px">Continue reading</h2><div class="cards">${recent.map(bookCard).join("")}</div>` : ""}
      <h2 style="margin:28px 0 12px">Featured titles</h2>
      <div class="cards">${featured.map(bookCard).join("")}</div>
      <h2 style="margin:28px 0 12px">Browse by category</h2>
      <div class="cards">${cats.map(c => `
        <a class="card" href="#categories/${c.slug}">
          <div style="font-weight:800">${esc(c.name)}</div>
          <div class="meta">${esc(c.tagline)}</div>
          <div class="meta"><span>${c.books} books</span><span>${fmt(c.pages)} pp.</span><span>${fmt(c.diagrams)} dia.</span></div>
        </a>`).join("")}</div>`;
    wireFavButtons(view());
  };

  // Library with filters + pagination
  let libState = { page: 0, perPage: 24, cat: "", level: "", q: "", sort: "id", pubOnly: false };
  routes.library = async (arg) => {
    await Promise.all([load("library", `${DATA}/library.json`),
      load("categories", `${DATA}/categories.json`), loadPublished()]);
    if (arg) libState.cat = arg;
    renderLibrary();
  };
  function renderLibrary() {
    let items = state.library.slice();
    if (libState.cat) items = items.filter(b => b.category_slug === libState.cat);
    if (libState.level) items = items.filter(b => b.level === libState.level);
    if (libState.pubOnly) items = items.filter(b => state.publishedMap[b.id]);
    if (libState.q) { const q = libState.q.toLowerCase(); items = items.filter(b => (b.title + " " + b.subtitle + " " + b.keywords.join(" ")).toLowerCase().includes(q)); }
    if (libState.sort === "pages") items.sort((a, b) => b.estimated_pages - a.estimated_pages);
    else if (libState.sort === "title") items.sort((a, b) => a.title.localeCompare(b.title));
    else items.sort((a, b) => a.id.localeCompare(b.id));

    const total = items.length;
    const pages = Math.max(1, Math.ceil(total / libState.perPage));
    libState.page = Math.min(libState.page, pages - 1);
    const slice = items.slice(libState.page * libState.perPage, (libState.page + 1) * libState.perPage);
    const catOpts = ['<option value="">All categories</option>']
      .concat(state.categories.map(c => `<option value="${c.slug}" ${libState.cat === c.slug ? "selected" : ""}>${esc(c.name)} (${c.books})</option>`)).join("");

    view().innerHTML = `
      <div class="page-head"><h1>Document Library</h1><p>Browse, filter and open all ${fmt(state.library.length)} books.</p></div>
      <div class="toolbar">
        <select id="f-cat">${catOpts}</select>
        <select id="f-level">${["", "Foundational", "Intermediate", "Advanced"].map(l => `<option value="${l}" ${libState.level === l ? "selected" : ""}>${l || "All levels"}</option>`).join("")}</select>
        <select id="f-sort">${[["id", "Sort: catalog"], ["title", "Sort: title"], ["pages", "Sort: pages"]].map(([v, t]) => `<option value="${v}" ${libState.sort === v ? "selected" : ""}>${t}</option>`).join("")}</select>
        <label class="tag" style="cursor:pointer"><input type="checkbox" id="f-pub" ${libState.pubOnly ? "checked" : ""}/> Downloadable only</label>
        <input id="f-q" placeholder="Filter titles…" value="${esc(libState.q)}" />
        <span class="count-note">${fmt(total)} results</span>
      </div>
      <div class="cards" id="lib-cards">${slice.map(bookCard).join("") || '<div class="empty">No matching books.</div>'}</div>
      <div class="pager">
        <button class="btn" id="prev" ${libState.page === 0 ? "disabled" : ""}>‹ Prev</button>
        <span class="tag">Page ${libState.page + 1} / ${pages}</span>
        <button class="btn" id="next" ${libState.page >= pages - 1 ? "disabled" : ""}>Next ›</button>
      </div>`;
    wireFavButtons(view());
    $("#f-cat").onchange = e => { libState.cat = e.target.value; libState.page = 0; renderLibrary(); };
    $("#f-level").onchange = e => { libState.level = e.target.value; libState.page = 0; renderLibrary(); };
    $("#f-sort").onchange = e => { libState.sort = e.target.value; renderLibrary(); };
    $("#f-pub").onchange = e => { libState.pubOnly = e.target.checked; libState.page = 0; renderLibrary(); };
    let deb; $("#f-q").oninput = e => { clearTimeout(deb); deb = setTimeout(() => { libState.q = e.target.value; libState.page = 0; renderLibrary(); }, 200); };
    $("#prev").onclick = () => { libState.page--; renderLibrary(); window.scrollTo(0, 0); };
    $("#next").onclick = () => { libState.page++; renderLibrary(); window.scrollTo(0, 0); };
  }

  routes.categories = async (arg) => {
    await Promise.all([load("categories", `${DATA}/categories.json`),
      load("library", `${DATA}/library.json`), loadPublished()]);
    if (arg) { libState.cat = arg; libState.page = 0; return renderLibrary(); }
    view().innerHTML = `
      <div class="page-head"><h1>Categories</h1><p>${state.categories.length} subject areas, each with a full series of books.</p></div>
      <div class="cards">${state.categories.map(c => `
        <a class="card" href="#categories/${c.slug}">
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
    const dls = pub ? Object.entries({ pdf: "PDF", docx: "DOCX", pptx: "PPTX", html: "HTML", md: "Markdown" })
      .filter(([k]) => pub.artifacts[k]).map(([k, label]) => `<a class="btn" href="${CONTENT}/${pub.artifacts[k]}" download>${label}</a>`).join("") : "";

    const chapters = outline.chapters.map(c => `
      <div class="chapter-row">
        <div class="num">${c.number}</div>
        <div>
          <div class="ct">${esc(c.title)}</div>
          <div class="cs">${esc(c.summary)}</div>
          <div class="chip-row">${c.sections.slice(0, 6).map(s => `<span class="chip">${esc(s)}</span>`).join("")}
            ${c.diagrams.length ? `<span class="chip">${c.diagrams.length} diagrams</span>` : ""}</div>
        </div>
      </div>`).join("");

    view().innerHTML = `
      <div class="btn-row" style="margin-bottom:16px"><a class="btn ghost" href="#library">‹ Library</a></div>
      <div class="detail-head">
        <div class="detail-cover"><div><div class="bc-cat">${esc(b.category)}</div><div class="dc-title">${esc(b.title.replace(b.category + ": ", ""))}</div></div>
          <div style="font-size:.8rem;opacity:.9">${esc(b.level)} · ${fmt(b.estimated_pages)} pages</div></div>
        <div class="detail-meta">
          <h1>${esc(b.title)}</h1>
          <div class="sub">${esc(b.subtitle)}</div>
          <div class="kv">
            <span><b>${fmt(b.chapter_count)}</b> chapters</span>
            <span><b>${fmt(b.estimated_pages)}</b> pages</span>
            <span><b>${fmt(b.word_count)}</b> words</span>
            <span><b>${fmt(b.diagram_count)}</b> diagrams</span>
            <span><b>${fmt(b.code_count)}</b> code samples</span>
            <span><b>${fmt(b.question_count)}</b> questions</span>
          </div>
          <div class="kv"><span>Authors: <b>${esc(b.authors.join(", "))}</b></span><span>ISBN <b>${esc(b.isbn)}</b></span><span>v${esc(b.version)}</span></div>
          <div class="btn-row">
            ${pub ? `<a class="btn primary" href="#read/${id}">Read online</a>` : `<a class="btn primary" href="#read/${id}">Preview outline</a>`}
            <button class="btn fav" data-id="${id}">${favs.has(id) ? "★ Favorited" : "☆ Favorite"}</button>
            ${dls}
          </div>
          ${!pub ? `<p class="cap" style="margin-top:12px">Full export files for this title are generated on demand. Run <code>python -m aupub.cli publish --ids ${id}</code> in <code>engine/</code> to produce its PDF, DOCX, PPTX, HTML and Markdown.</p>` : ""}
        </div>
      </div>
      <div class="section-block"><h2>Executive summary</h2><div>${mdToHtml(esc(b.description))}</div></div>
      <div class="section-block"><h2>Table of contents (${outline.chapters.length} chapters)</h2><div class="chapter-list">${chapters}</div></div>`;
    wireFavButtons(view());
  };

  // Reader — full content if published, else outline preview
  routes.read = async (id) => {
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const b = state.library.find(x => x.id === id);
    if (!b) { view().innerHTML = `<div class="empty">Book not found.</div>`; return; }
    const pub = state.publishedMap[id];
    let content = null;
    if (pub && pub.artifacts.content) {
      if (state.contentCache[id]) content = state.contentCache[id];
      else { content = await getJSON(`${CONTENT}/${pub.artifacts.content}`); state.contentCache[id] = content; }
    }
    if (content) renderReader(b, content, pub);
    else renderOutlinePreview(b);
  };

  const KROKI_ENGINE = { plantuml: "plantuml", drawio: "diagramnet" };
  const diagramSourceStore = new Map();
  let diagramSourceSeq = 0;

  function stashDiagramSource(source) {
    const id = String(++diagramSourceSeq);
    diagramSourceStore.set(id, source);
    return id;
  }

  function diagramHtml(d, diagramsBase) {
    const cap = `<p class="cap">${esc(d.caption || d.title || "")}</p>`;
    if (d.fmt === "mermaid") {
      return `<div class="diagram"><pre class="mermaid">${esc(d.source)}</pre></div>${cap}`;
    }
    if (d.fmt === "svg" && d.source && d.source.trim().startsWith("<svg")) {
      return `<div class="diagram diagram-svg">${d.source}</div>${cap}`;
    }
    if (d.fmt === "svg" && d.file && diagramsBase) {
      return `<div class="diagram"><img class="diagram-img" alt="${esc(d.caption || d.title)}" loading="lazy" src="${diagramsBase}/${encodeURI(d.file)}"/></div>${cap}`;
    }
    if (d.fmt === "plantuml" || d.fmt === "drawio") {
      const sid = stashDiagramSource(d.source);
      const engine = KROKI_ENGINE[d.fmt];
      return `<div class="diagram diagram-kroki" data-kroki-engine="${engine}" data-kroki-id="${sid}"><div class="diagram-loading">Rendering diagram…</div></div>${cap}`;
    }
    return `<div class="diagram"><pre class="diagram-fallback"><code>${esc((d.source || "").slice(0, 800))}</code></pre></div><p class="cap">${esc(d.fmt)} source — ${esc(d.caption)}</p>`;
  }

  async function renderKrokiDiagram(el) {
    const engine = el.dataset.krokiEngine;
    const source = diagramSourceStore.get(el.dataset.krokiId);
    if (!engine || source == null) return;
    try {
      const res = await fetch(`https://kroki.io/${engine}/svg`, {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: source,
      });
      if (!res.ok) throw new Error(`Kroki HTTP ${res.status}`);
      const svg = await res.text();
      el.innerHTML = `<div class="diagram-svg">${svg}</div>`;
    } catch (err) {
      el.innerHTML = `<pre class="diagram-fallback"><code>${esc(source.slice(0, 500))}${source.length > 500 ? "…" : ""}</code></pre><p class="cap">Could not render diagram (${esc(err.message)}).</p>`;
    }
  }

  async function hydrateDiagrams(root) {
    const scope = root || document;
    const kroki = [...scope.querySelectorAll(".diagram-kroki[data-kroki-id]")];
    await Promise.all(kroki.map(renderKrokiDiagram));
    if (window.renderMermaid) {
      try { await window.renderMermaid(scope.querySelector(".reader-body") || scope); }
      catch (e) { console.warn("Mermaid render:", e); }
    }
  }

  function renderReader(b, content, pub) {
    const diagramsBase = pub?.artifacts?.diagrams_dir ? `${CONTENT}/${pub.artifacts.diagrams_dir}` : null;
    const toc = content.chapters.map(c => `<a href="#ch-${c.number}" data-ch="${c.number}">${c.number}. ${esc(c.title)}</a>`).join("");
    const body = content.chapters.map(c => {
      let html = `<h1 id="ch-${c.number}">Chapter ${c.number}. ${esc(c.title)}</h1><p class="cap">${esc(c.summary)}</p>`;
      for (const s of c.sections) {
        html += `<h2>${esc(s.heading)}</h2>${mdToHtml(s.body)}`;
      }
      if (c.diagrams && c.diagrams.length) {
        html += `<h2>Figures</h2>${c.diagrams.map(d => diagramHtml(d, diagramsBase)).join("")}`;
      }
      for (const cs of c.code_samples) html += `<h3>Listing: ${esc(cs.title)}</h3><pre><code>${esc(cs.code)}</code></pre>`;
      html += `<h2>Review Questions</h2>` + c.questions.map((q, i) => {
        if (q.answer_index < 0) return `<div class="qbox"><b>${i + 1}. ${esc(q.question)}</b><div class="ans">Guidance: ${esc(q.explanation)}</div></div>`;
        return `<div class="qbox"><b>${i + 1}. ${esc(q.question)}</b>${q.options.map((o, j) => `<span class="opt">${String.fromCharCode(65 + j)}. ${esc(o)}</span>`).join("")}<div class="ans">Answer ${String.fromCharCode(65 + q.answer_index)}. ${esc(q.explanation)}</div></div>`;
      }).join("");
      return `<section class="rch" data-ch="${c.number}">${html}</section>`;
    }).join("");

    const dls = Object.entries({ pdf: "PDF", docx: "DOCX", pptx: "PPTX", md: "MD" })
      .filter(([k]) => pub.artifacts[k]).map(([k, l]) => `<a class="btn" href="${CONTENT}/${pub.artifacts[k]}" download>${l}</a>`).join("");

    view().innerHTML = `
      <div class="btn-row" style="margin-bottom:14px">
        <a class="btn ghost" href="#book/${b.id}">‹ Details</a>${dls}
        <button class="btn" id="bookmark-btn">⚑ Bookmark current chapter</button>
      </div>
      <div class="reader">
        <nav class="reader-toc">${toc}</nav>
        <article class="reader-body" id="reader-body">${body}</article>
      </div>`;
    progress.set(b.id, 0, content.chapters.length);

    hydrateDiagrams(view());
    // scroll spy + progress
    const tocLinks = view().querySelectorAll(".reader-toc a");
    const sections = view().querySelectorAll(".rch");
    let current = 1;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          current = +en.target.dataset.ch;
          tocLinks.forEach(a => a.classList.toggle("active", +a.dataset.ch === current));
          progress.set(b.id, current, content.chapters.length);
          updateProgressPill();
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    sections.forEach(s => obs.observe(s));
    $("#bookmark-btn").onclick = () => {
      const c = content.chapters[current - 1];
      marks.add({ id: b.id, ch: current, title: b.title, chapter: c.title });
      $("#bookmark-btn").textContent = "⚑ Bookmarked!";
      setTimeout(() => $("#bookmark-btn").textContent = "⚑ Bookmark current chapter", 1500);
    };
  }

  function renderOutlinePreview(b) {
    loadOutline(b.id).then(outline => {
      const body = outline.chapters.map(c => `
        <section><h1>Chapter ${c.number}. ${esc(c.title)}</h1><p class="cap">${esc(c.summary)}</p>
        <ul>${c.sections.map(s => `<li>${esc(s)}</li>`).join("")}</ul></section>`).join("");
      view().innerHTML = `
        <div class="btn-row" style="margin-bottom:14px"><a class="btn ghost" href="#book/${b.id}">‹ Details</a></div>
        <div class="section-block"><b>Outline preview.</b> This title's full text and downloads are generated on demand by the engine
          (<code>python -m aupub.cli publish --ids ${b.id}</code>). The complete chapter structure is shown below.</div>
        <article class="reader-body">${body}</article>`;
    });
  }

  // Search
  routes.search = async (arg) => {
    await load("search", `${DATA}/search-index.json`);
    const q = decodeURIComponent(arg || "");
    view().innerHTML = `
      <div class="page-head"><h1>Search</h1><p>Full-text search across ${fmt(state.search.length)} books, chapters and topics.</p></div>
      <div class="toolbar"><input id="search-box" style="flex:1" placeholder="Search topics, e.g. retrieval, transformers, governance…" value="${esc(q)}"/></div>
      <div id="search-results"></div>`;
    const box = $("#search-box");
    const run = () => doSearch(box.value);
    let deb; box.oninput = () => { clearTimeout(deb); deb = setTimeout(run, 180); };
    box.focus();
    if (q) run();
  };
  function doSearch(q) {
    const res = $("#search-results");
    q = q.trim();
    if (!q) { res.innerHTML = `<div class="empty">Type to search.</div>`; return; }
    const terms = q.toLowerCase().split(/\s+/);
    const scored = [];
    for (const r of state.search) {
      const hay = (r.title + " " + r.subtitle + " " + r.category + " " + r.chapters.join(" ") + " " + r.text + " " + r.keywords.join(" ")).toLowerCase();
      let score = 0;
      for (const t of terms) { const c = hay.split(t).length - 1; if (c) score += c; if (r.title.toLowerCase().includes(t)) score += 5; }
      if (score) {
        const chMatch = r.chapters.filter(c => terms.some(t => c.toLowerCase().includes(t))).slice(0, 3);
        scored.push({ r, score, chMatch });
      }
    }
    scored.sort((a, b) => b.score - a.score);
    const top = scored.slice(0, 40);
    res.innerHTML = top.length ? top.map(({ r, chMatch }) => `
      <a class="result" href="#book/${r.id}">
        <h3>${hl(r.title, terms)} <span class="tag level">${esc(r.level)}</span></h3>
        <div class="snippet">${esc(r.category)} · ${fmt(r.pages)} pp. — ${hl(r.subtitle, terms)}</div>
        ${chMatch.length ? `<div class="snippet">Chapters: ${chMatch.map(c => hl(c, terms)).join(" · ")}</div>` : ""}
      </a>`).join("") : `<div class="empty">No results for “${esc(q)}”.</div>`;
  }
  function hl(text, terms) {
    let out = esc(text);
    terms.forEach(t => { if (t.length > 1) out = out.replace(new RegExp(`(${t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig"), "<mark>$1</mark>"); });
    return out;
  }

  // Diagram browser
  routes.diagrams = async () => {
    await Promise.all([load("library", `${DATA}/library.json`), load("stats", `${DATA}/stats.json`), loadPublished()]);
    const kinds = ["Architecture", "Application Flow", "Business Process", "Data Flow", "Sequence", "Class", "Component", "Deployment", "Network", "Cloud Architecture", "RAG Architecture", "Agent Architecture", "Security Architecture", "DevOps Pipeline", "CI/CD Pipeline", "Infrastructure", "Knowledge Graph", "Data Lineage", "Capability Map", "Operating Model"];
    const fmts = ["mermaid", "plantuml", "svg", "drawio"];
    // gather sample diagrams from published book content (includes diagram source)
    const pubIds = (state.published || []).map(p => p.id).slice(0, 4);
    const samples = [];
    for (const id of pubIds) {
      const pub = state.publishedMap[id];
      const o = await loadOutline(id);
      if (!pub?.artifacts?.content) continue;
      let bookContent = state.contentCache[id];
      if (!bookContent) {
        bookContent = await getJSON(`${CONTENT}/${pub.artifacts.content}`);
        state.contentCache[id] = bookContent;
      }
      bookContent.chapters.forEach(ch => {
        (ch.diagrams || []).forEach(d => samples.push({ ...d, book: o.title, id }));
      });
    }
    view().innerHTML = `
      <div class="page-head"><h1>Diagram Browser</h1><p>The library contains ${fmt(state.stats.diagrams)} professional diagrams generated in Mermaid, PlantUML, SVG and Draw.io across ${kinds.length} diagram types.</p></div>
      <div class="section-block"><h2>Diagram types</h2><div class="chip-row">${kinds.map(k => `<span class="tag">${esc(k)}</span>`).join("")}</div></div>
      <div class="section-block"><h2>Source formats</h2><div class="chip-row">${fmts.map(f => `<span class="tag level">${esc(f)}</span>`).join("")}</div>
        <p class="cap">Diagram source files are stored separately alongside each published book (under its <code>diagrams/</code> folder).</p></div>
      <h2 style="margin:20px 0 12px">Sample figures from published titles</h2>
      <div class="cards">${samples.slice(0, 12).map((d, i) => `
        <div class="card">
          <div style="font-weight:700">${esc(d.title)}</div>
          <div class="meta"><span class="tag">${esc(d.kind)}</span><span class="tag level">${esc(d.fmt)}</span></div>
          <div class="meta">${esc(d.book)}</div>
          <div class="diagram-preview" id="diagram-preview-${i}"></div>
          <a class="btn primary" style="margin-top:10px" href="#read/${d.id}">Open book</a>
        </div>`).join("")}</div>`;
    const prev = view();
    samples.slice(0, 12).forEach((d, i) => {
      const slot = prev.querySelector(`#diagram-preview-${i}`);
      if (!slot) return;
      const sid = stashDiagramSource(d.source || "");
      slot.innerHTML = d.fmt === "mermaid"
        ? `<pre class="mermaid" style="font-size:.65rem">${esc(d.source)}</pre>`
        : d.fmt === "svg" && d.source && d.source.trim().startsWith("<svg")
          ? `<div class="diagram-svg">${d.source}</div>`
          : `<div class="diagram-kroki" data-kroki-engine="${KROKI_ENGINE[d.fmt] || ""}" data-kroki-id="${sid}"><div class="diagram-loading">…</div></div>`;
    });
    hydrateDiagrams(prev);
  };

  // Download center
  routes.downloads = async () => {
    await Promise.all([loadPublished(), load("library", `${DATA}/library.json`)]);
    const rows = (state.published || []).map(p => {
      const a = p.artifacts;
      const links = [["pdf", "PDF"], ["docx", "DOCX"], ["pptx", "PPTX"], ["html", "HTML"], ["md", "MD"]]
        .filter(([k]) => a[k]).map(([k, l]) => `<a class="btn" href="${CONTENT}/${a[k]}" download>${l}</a>`).join("");
      return `<div class="result"><h3>${esc(p.title)}</h3>
        <div class="snippet">${esc(p.category)} · ${esc(p.level)} · ${fmt(p.estimated_pages)} pp.</div>
        <div class="btn-row" style="margin-top:8px">${links} <a class="btn ghost" href="#read/${p.id}">Read online</a></div></div>`;
    }).join("");
    view().innerHTML = `
      <div class="page-head"><h1>Download Center</h1>
        <p>Every published book is available in five formats. ${state.published ? state.published.length : 0} titles are pre-rendered in this demo corpus; the engine can publish all ${fmt(state.library.length)} on demand.</p></div>
      ${rows || '<div class="empty">No published books yet. Run the publish command in engine/.</div>'}`;
  };

  // Learning paths
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
      const firstBook = s => (state.library.find(b => b.category_slug === s) || {});
      view().innerHTML = `
        <div class="page-head"><h1>${title}</h1><p>${intro}</p></div>
        ${paths.map(p => `
          <div class="path-card">
            <div style="font-weight:800;font-size:1.05rem">${esc(p.name)}</div>
            <div class="meta">${esc(p.desc)} · ${p.steps.length} stages · ~${p.steps.length * 280} pages</div>
            <div class="path-steps">${p.steps.map((s, i) => { const fb = firstBook(s); return `<a class="path-step" href="#categories/${s}"><span class="n">${i + 1}</span>${esc(catName(s))}</a>`; }).join("")}</div>
          </div>`).join("")}`;
    });
  }
  routes.paths = () => renderPaths("Learning Paths", "Curated, sequenced tracks that take you from foundations to mastery across multiple categories.", LEARNING_PATHS);
  routes.certifications = () => renderPaths("Certification Paths", "Structured certification tracks. Read the books in order, complete the assessments and certification questions in each.", CERT_PATHS);

  // Favorites & bookmarks
  routes.favorites = async () => {
    await Promise.all([load("library", `${DATA}/library.json`), loadPublished()]);
    const items = favs.list().map(id => state.library.find(b => b.id === id)).filter(Boolean);
    view().innerHTML = `<div class="page-head"><h1>Favorites</h1><p>${items.length} saved titles.</p></div>
      <div class="cards">${items.map(bookCard).join("") || '<div class="empty">No favorites yet. Tap the ☆ on any book.</div>'}</div>`;
    wireFavButtons(view());
  };
  routes.bookmarks = async () => {
    await load("library", `${DATA}/library.json`);
    const items = marks.list();
    view().innerHTML = `<div class="page-head"><h1>Bookmarks</h1><p>${items.length} saved chapter bookmarks.</p></div>
      ${items.length ? items.map(m => `<div class="result"><h3>${esc(m.title)}</h3>
        <div class="snippet">Chapter ${m.ch}: ${esc(m.chapter || "")}</div>
        <div class="btn-row" style="margin-top:8px"><a class="btn primary" href="#read/${m.id}">Open</a>
        <button class="btn rm" data-id="${m.id}" data-ch="${m.ch}">Remove</button></div></div>`).join("")
        : '<div class="empty">No bookmarks yet. Use “Bookmark current chapter” while reading.</div>'}`;
    view().querySelectorAll(".rm").forEach(b => b.onclick = () => { marks.remove(b.dataset.id, +b.dataset.ch); router(); });
  };

  // ---- progress pill + theme + chrome ----
  function updateProgressPill() {
    const all = progress.all();
    const ids = Object.keys(all);
    const started = ids.length;
    const done = ids.filter(id => all[id].total && all[id].ch >= all[id].total).length;
    $("#progress-pill").textContent = started ? `${started} started · ${done} finished` : "";
  }
  async function updateSidebarStats() {
    try {
      const s = await load("stats", `${DATA}/stats.json`);
      $("#sidebar-stats").innerHTML = `<b>${fmt(s.books)}</b> books · <b>${fmt(s.pages)}</b> pages<br><b>${fmt(s.words)}</b> words · <b>${fmt(s.diagrams)}</b> diagrams`;
    } catch { $("#sidebar-stats").textContent = "Run the engine catalog command."; }
  }
  function initTheme() {
    const saved = store.get("aiu:theme", null);
    if (saved) document.documentElement.dataset.theme = saved;
    $("#theme-toggle").onclick = () => {
      const cur = document.documentElement.dataset.theme === "dark" ? "" : "dark";
      document.documentElement.dataset.theme = cur; store.set("aiu:theme", cur);
    };
  }

  function init() {
    initTheme();
    updateSidebarStats();
    updateProgressPill();
    $("#hamburger").onclick = () => $("#sidebar").classList.toggle("open");
    const gs = $("#global-search-input");
    gs.addEventListener("keydown", e => { if (e.key === "Enter" && gs.value.trim()) location.hash = `search/${encodeURIComponent(gs.value.trim())}`; });
    window.addEventListener("hashchange", router);
    router();
  }
  document.addEventListener("DOMContentLoaded", init);
})();
