// Reusable builders — the HTML/CSS equivalent of the Manim _common.py helpers.
// Text/structure are plain HTML (CSS flexbox handles layout/wrapping); DIAGRAMS
// are rendered by Mermaid (c.diagram) as clean SVG. A scene composes these, then
// animates them with the anime.js timeline (ctx.tl), which is seekable so frames
// can be captured deterministically.

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text != null) node.textContent = text;
  return node;
}

const SEMANTIC = {
  DANGER: 'var(--danger)', OK: 'var(--ok)', PRIMARY: 'var(--primary)',
  ACCENT: 'var(--accent)', HIGHLIGHT: 'var(--highlight)', TEXT: 'var(--text)',
  MUTED: 'var(--muted)',
};

export function createComponents(lang) {
  const L = (idText, enText) => (lang === 'en' ? enText : idText);

  const content = () => el('div', 'content');

  function titleBar(text, opts = {}) {
    const bar = el('div', 'title-bar');
    if (opts.eyebrow) {
      const col = el('div');
      col.style.display = 'flex';
      col.style.flexDirection = 'column';
      col.appendChild(el('div', 'eyebrow', opts.eyebrow));
      col.appendChild(el('div', 'bar-title', text));
      bar.appendChild(col);
    } else {
      bar.appendChild(el('div', 'bar-title', text));
    }
    return bar;
  }

  function titleText(text, opts = {}) {
    const n = el('div', 'title', text);
    if (opts.color) n.style.color = SEMANTIC[opts.color] || opts.color;
    if (opts.size) n.style.fontSize = opts.size + 'px';
    return n;
  }

  function bodyText(text, opts = {}) {
    const n = el('div', 'body-text', text);
    if (opts.color) n.style.color = SEMANTIC[opts.color] || opts.color;
    if (opts.size) n.style.fontSize = opts.size + 'px';
    return n;
  }

  function sectionLabel(text, opts = {}) {
    const n = el('div', 'section-label', text);
    if (opts.color) n.style.color = SEMANTIC[opts.color] || opts.color;
    return n;
  }

  function bulletList(items, opts = {}) {
    const list = el('div', 'bullet-list');
    for (const item of items) {
      const row = el('div', 'bullet');
      const dot = el('div', 'dot');
      if (opts.dotColor) dot.style.background = SEMANTIC[opts.dotColor] || opts.dotColor;
      row.appendChild(dot);
      row.appendChild(el('div', 'txt', item));
      list.appendChild(row);
    }
    return list;
  }

  // Code is rendered verbatim (textContent) — raw &, <, > are fine.
  function codeCard(code, opts = {}) {
    const card = el('div', 'code-card');
    if (opts.accent) card.style.borderColor = SEMANTIC[opts.accent] || opts.accent;
    if (opts.title) card.appendChild(el('div', 'code-title', opts.title));
    const pre = el('pre');
    pre.textContent = code;
    if (opts.size) pre.style.fontSize = opts.size + 'px';
    card.appendChild(pre);
    return card;
  }

  /**
   * Render a Mermaid diagram (UML classDiagram, flowchart, sequenceDiagram, …)
   * from its text definition and return a <div> wrapping the SVG. ASYNC — the
   * scene must `await c.diagram(...)`. Use a classDiagram for UML:
   *   await c.diagram(`classDiagram
   *     class AppConfig {
   *       -instance: AppConfig
   *       +getInstance() AppConfig
   *     }`)
   */
  async function diagram(def, opts = {}) {
    const id = 'mmd-' + Math.random().toString(36).slice(2);
    const {svg} = await window.mermaid.render(id, def);
    const wrap = el('div', 'diagram');
    if (opts.maxWidth) wrap.style.maxWidth = opts.maxWidth;
    wrap.innerHTML = svg;
    return wrap;
  }

  return {L, el, content, titleBar, titleText, bodyText, sectionLabel,
          bulletList, codeCard, diagram, SEMANTIC};
}
