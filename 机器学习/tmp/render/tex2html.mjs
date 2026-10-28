/**
 * tex2html.mjs — faithful-enough LaTeX(article/ctex) -> print-ready HTML renderer.
 *
 * Supports the subset used by the 机器学习作业一 documents:
 *   \section*, \textbf/\textit/\emph/\texttt, {\large ...}, \color{...} \Large \large
 *   \begin{enumerate}[opts]\item   (nested), \begin{itemize}\item
 *   \begin{table}[H] + tabular + \toprule/\midrule/\bottomrule/\cmidrule,
 *   \multirow, \multicolumn, \caption, \label, \ref
 *   \[ ... \] display math, $...$ inline math (rendered by MathJax, offline),
 *   \begin{tikzpicture} -> native SVG, \clearpage -> page-break, \today.
 *
 * Usage: node tex2html.mjs <input.tex> <output.html> <title>
 */
import fs from 'node:fs';
import path from 'node:path';
import { initMathJax } from './mj.mjs';

/* ------------------------------------------------------------------ utils */

/** Strip LaTeX comments (a % that is not escaped). */
const stripComments = (src) =>
  src.split('\n').map((line) => {
    let out = '';
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '\\' && i + 1 < line.length) { out += ch + line[i + 1]; i++; continue; }
      if (ch === '%') break;
      out += ch;
    }
    return out;
  }).join('\n');

/** index just past the \begin{name} that starts at `start`, braces balanced. */
function skipBegin(src, start) {
  let i = src.indexOf('{', start);
  let depth = 0;
  for (; i < src.length; i++) {
    if (src[i] === '\\') { i++; continue; }
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) return i + 1; }
  }
  return src.length;
}

/** return {inner, end} for the brace group starting at index of '{' (== start). */
function readGroup(src, start) {
  let i = start, depth = 0;
  for (; i < src.length; i++) {
    const ch = src[i];
    if (ch === '\\') { i++; continue; }
    if (ch === '{') depth++;
    else if (ch === '}') { depth--; if (depth === 0) return { inner: src.slice(start + 1, i), end: i + 1 }; }
  }
  return { inner: src.slice(start + 1), end: src.length };
}

/** optional [..] argument */
function readOpt(src, start) {
  if (src[start] !== '[') return null;
  let depth = 0;
  for (let i = start; i < src.length; i++) {
    if (src[i] === '\\') { i++; continue; }
    if (src[i] === '[') depth++;
    else if (src[i] === ']') { depth--; if (depth === 0) return { inner: src.slice(start + 1, i), end: i + 1 }; }
  }
  return null;
}

/** Index just past a brace-balanced group starting at `src[i]` (== '{'). */
function matchBrace(src, i) {
  let d = 0;
  for (; i < src.length; i++) {
    if (src[i] === '\\') { i++; continue; }
    if (src[i] === '{') d++;
    else if (src[i] === '}') { d--; if (d === 0) return i + 1; }
  }
  return -1;
}

/**
 * Extract the body of the first tabular in `src`.
 *
 * Column specs may themselves contain braces (`c@{\quad}ccc`), so the spec must
 * be brace-balanced rather than matched with `[^}]*` — that mistake silently
 * swallows half the body into the "spec".
 */
function extractTabular(src) {
  const at = src.search(/\\begin\s*\{tabular\}/);
  if (at === -1) return null;
  const specOpen = src.indexOf('{', src.indexOf('}', at) + 1);
  if (specOpen === -1) return null;
  const specEnd = matchBrace(src, specOpen);
  if (specEnd === -1) return null;
  const spec = src.slice(specOpen + 1, specEnd - 1);
  const bodyStart = specEnd;
  const endRel = src.slice(bodyStart).search(/\\end\s*\{tabular\}/);
  if (endRel === -1) return null;
  return { spec, body: src.slice(bodyStart, bodyStart + endRel) };
}

/** find matching \end{name} for a \begin{name} at `envStart`; returns {inner,end}. */
function readEnvBody(src, envStart, name) {
  const endRe = new RegExp(`\\\\end\\s*\\{${name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\}`);
  let depth = 1, i = envStart;
  while (i < src.length) {
    const b = src.indexOf('\\begin', i);
    const e = endRe.exec(src.slice(i));
    const eIdx = e ? i + e.index : -1;
    if (eIdx === -1) return { inner: src.slice(envStart), end: src.length };
    if (b !== -1 && b < eIdx) {
      // any nested environment increases depth
      const g = readGroup(src, src.indexOf('{', b));
      const nm = g.inner.trim();
      // self-contained environments handled elsewhere still nest
      depth++;
      i = skipBegin(src, b);
      continue;
    }
    depth--;
    if (depth === 0) return { inner: src.slice(envStart, eIdx), end: eIdx + e[0].length };
    i = eIdx + e[0].length;
  }
  return { inner: src.slice(envStart), end: src.length };
}

/* ------------------------------------------------------------------- math */

const M = []; // math placeholders
const storeMath = (tex, display) => `\u0001MJ${M.push({ tex, display }) - 1}\u0001`;
const MATH_RE = /\u0001MJ(\d+)\u0001/g;

/* ------------------------------------------------------------ inline text */

/** label -> table number, filled in by renderTabular; used for \ref. */
const LABELS = new Map();
let tableCounter = 0;

/**
 * Convert inline LaTeX text to HTML.
 *
 * Order matters: the LaTeX source is escaped for HTML *first*, then LaTeX text
 * commands are turned into real markup. Doing it the other way round destroys
 * the tags we just produced.
 */
function inline(src) {
  let s = src;
  // 1. protect inline math so the escaped text never touches it
  s = s.replace(/(?<!\\)\$(.+?)(?<!\\)\$/gs, (m, tex) => storeMath(tex, false));
  // 2. escape what is plain text in the source
  s = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // 3. structural no-ops (now operating on escaped text)
  s = s.replace(/\\(label|index|nonumber)\s*\{[^{}]*\}/g, '');
  s = s.replace(/\\ref\s*\{([^{}]*)\}/g, (m, k) => (LABELS.has(k) ? LABELS.get(k) : k));

  // 4. character escapes and spacing
  s = s.replace(/\\%/g, '%');
  s = s.replace(/\\&/g, '&amp;');
  s = s.replace(/\\_/g, '_');
  s = s.replace(/\\#/g, '#');
  s = s.replace(/\\\{/g, '{').replace(/\\\}/g, '}');
  s = s.replace(/\\[,;:]/g, '\u2009');
  s = s.replace(/\\q?quad\b/g, '\u2003\u2003');
  s = s.replace(/\\enspace\b/g, '\u2002');
  s = s.replace(/\\ /g, '\u00a0');
  s = s.replace(/~/g, '\u00a0');
  s = s.replace(/\\today\b/g, '2026 年 9 月 14 日');
  s = s.replace(/\\LaTeX\b/g, 'LaTeX');
  s = s.replace(/\\TeX\b/g, 'TeX');
  s = s.replace(/---/g, '\u2014').replace(/--/g, '\u2013');

  // 5. markup commands -> real tags
  s = s.replace(/\\textbf\s*\{/g, '<b>');
  s = s.replace(/\\textit\s*\{/g, '<i>');
  s = s.replace(/\\emph\s*\{/g, '<i>');
  s = s.replace(/\\texttt\s*\{/g, '<code>');
  s = s.replace(/\\underline\s*\{/g, '<u>');
  s = s.replace(/\\mbox\s*\{/g, '<span class="mbox">');
  s = s.replace(/\\mathrm\s*\{/g, '<span class="rm">');
  s = s.replace(/\\color\s*\{(\w+)\}/g, '<span class="color-$1">');
  s = s.replace(/\{\s*\\Large\b\s*/g, '<span class="fs-Large">');
  s = s.replace(/\{\s*\\large\b\s*/g, '<span class="fs-large">');
  s = s.replace(/\\Large\b/g, '<span class="fs-Large">');
  s = s.replace(/\\large\b/g, '<span class="fs-large">');
  s = s.replace(/\\bfseries\b/g, '');
  s = s.replace(/\\centering\b/g, '');

  return s;
}

/* ----------------------------------------------------------------- tables */

const BLOCK_CMDS = ['section', 'subsection', 'begin', 'end', 'clearpage', 'newpage', 'item'];

function startsBlock(line) {
  const t = line.trim();
  if (!t) return false;
  if (/^\\\[/.test(t)) return true;
  if (/^\\(begin|end|section|subsection|clearpage|newpage|item)\b/.test(t)) return true;
  return false;
}

/** split a tabular body into rows, each row an array of cell sources. */
function parseRows(body) {
  const rows = [];
  let cell = '', row = [], depth = 0;
  const pushCell = () => { row.push(cell.trim()); cell = ''; };
  const pushRow = () => {
    pushCell();
    if (row.some((c) => c !== '') || row.length > 1) rows.push(row);
    row = [];
  };
  for (let i = 0; i < body.length; i++) {
    const ch = body[i];
    if (ch === '\\') {
      const rest = body.slice(i);
      if (/^\\\\(\s*\[[^\]]*\])?/.test(rest)) {
        const m = rest.match(/^\\\\(\s*\[[^\]]*\])?/);
        if (depth === 0 && row.length >= 0 && cell !== '' ) { pushRow(); i += m[0].length - 1; continue; }
        pushRow(); i += m[0].length - 1; continue;
      }
      if (/^\\(top|mid|bottom)rule\b/.test(rest)) {
        const m = rest.match(/^\\(top|mid|bottom)rule\b/);
        if (cell.trim() !== '') pushCell();
        rows.push({ rule: m[1] });
        i += m[0].length - 1;
        continue;
      }
      if (/^\\cmidrule\b/.test(rest)) {
        const m = rest.match(/^\\cmidrule(\([^)]*\))?\s*\{(\d+)-(\d+)\}/);
        if (cell.trim() !== '') pushCell();
        if (m) rows.push({ cmidrule: [Number(m[2]), Number(m[3])] });
        i += (m ? m[0].length : rest.indexOf('}') + 1) - 1;
        continue;
      }
      if (/^\\hline\b/.test(rest)) { i += 5; continue; }
      cell += ch + (body[i + 1] ?? ''); i++; continue;
    }
    if (ch === '{') { depth++; cell += ch; continue; }
    if (ch === '}') { depth--; cell += ch; continue; }
    if (ch === '&' && depth === 0) { pushCell(); continue; }
    cell += ch;
  }
  if (cell.trim() !== '' || row.length) pushRow();
  return rows.filter((r) => r.rule || r.cmidrule || r.some((c) => c !== ''));
}

/**
 * Render a tabular. Handles \toprule/\midrule/\bottomrule as horizontal rules,
 * \cmidrule{a-b} as a partial rule carried on the row above it, and
 * \multirow / \multicolumn spanning.
 */
function renderTabular(body, spec, caption, label) {
  const parsed = parseRows(body); // may contain {rule:'top'|'mid'|'bottom'} and {cmidrule:[a,b]}

  /* --- group content rows between horizontal rules ---------------------- */
  const groups = [[]];
  for (const item of parsed) {
    if (item.rule) {
      if (groups[groups.length - 1].length) groups.push([]);
      continue;
    }
    if (item.cmidrule) { groups[groups.length - 1].push({ cmidrule: item.cmidrule }); continue; }
    groups[groups.length - 1].push(item);
  }
  const clean = groups.filter((g) => g.length);

  /* --- render cells, resolving vertical merges inside each group -------- */
  const rowsHtml = [];
  const groupMeta = []; // for border classes

  clean.forEach((group, gi) => {
    // split off cmidrule markers (they annotate the row above)
    const rules = new Map(); // rowIndex -> [[a,b],...]
    const rows = [];
    group.forEach((item) => {
      if (item.cmidrule) { rules.set(rows.length - 1, [...(rules.get(rows.length - 1) || []), item.cmidrule]); return; }
      rows.push(item);
    });

    const grid = rows.map((cells) => cells.map((raw) => {
      let cell = raw, rowspan = 1, colspan = 1, align = 'center';
      const mc = cell.match(/^\\multicolumn\s*\{(\d+)\}\s*\{([^{}]*)\}\s*\{([\s\S]*)\}$/);
      if (mc) {
        colspan = Number(mc[1]);
        align = /\bl\b/.test(mc[2]) ? 'left' : /\br\b/.test(mc[2]) ? 'right' : 'center';
        cell = mc[3];
      }
      const mr = cell.match(/^\\multirow\s*\{(\d+)\}\s*\{[^{}]*\}\s*\{([\s\S]*)\}$/);
      if (mr) { rowspan = Number(mr[1]); cell = mr[2]; }
      return { html: inline(cell), rowspan, colspan, align };
    }));

    // apply rowspans (multirow covers the next `rowspan-1` rows in this group)
    for (let r = 0; r < grid.length; r++) {
      for (let c = 0; c < grid[r].length; c++) {
        const cell = grid[r][c];
        if (!cell || cell.rowspan <= 1) continue;
        const span = Math.min(cell.rowspan, grid.length - r);
        if (span > 1) for (let k = 1; k < span; k++) grid[r + k].splice(c + 1, 0, null); // keep column alignment
      }
    }

    grid.forEach((row, ri) => {
      const tds = [];
      for (const cell of row) {
        if (cell === null) continue;
        const cls = [];
        if (cell.align !== 'center') cls.push(`ta-${cell.align}`);
        const cm = rules.get(ri);
        if (cm) cls.push(...cm.map(([a, b]) => `cm-${a}-${b}`));
        const attrs = [];
        if (cell.rowspan > 1) attrs.push(`rowspan="${Math.min(cell.rowspan, grid.length - ri)}"`);
        if (cell.colspan > 1) attrs.push(`colspan="${cell.colspan}"`);
        if (cls.length) attrs.push(`class="${cls.join(' ')}"`);
        tds.push(`<td ${attrs.join(' ')}>${cell.html}</td>`);
      }
      rowsHtml.push({ html: `<tr data-group="${gi}">${tds.join('')}</tr>`, group: gi, first: ri === 0, last: ri === rows.length - 1 });
    });
    groupMeta.push({ first: rowsHtml.length - rows.length, last: rowsHtml.length - 1 });
  });

  // classes: booktabs rules at the top of the table, under each group, and at the end
  const html = rowsHtml.map((r, i) => {
    const cls = [];
    if (i === 0) cls.push('ruletop');
    if (i === rowsHtml.length - 1) cls.push('rulebottom');
    if (r.last && i !== rowsHtml.length - 1) cls.push('rulemid');
    return r.html.replace('<tr ', `<tr class="${cls.join(' ')}" `);
  });

  const nCols = Math.max(...rowsHtml.map((r) => (r.html.match(/<td/g) || []).length), 1);

  if (label) { tableCounter += 1; LABELS.set(label, String(tableCounter)); }
  const cap = caption ? `<div class="caption">表 ${tableCounter}&nbsp;&nbsp;${inline(caption)}</div>` : '';
  return {
    html: `<div class="tablewrap">\n<table class="booktabs">\n${html.join('\n')}\n</table>\n${cap}</div>`,
    nCols,
  };
}

/* ------------------------------------------------------------- tikzpicture */

/** Parse a minimal subset of tikz: axes, ticks, plot coordinates, diagonal, nodes. */
function renderTikz(src, opt) {
  const xcm = Number((opt.match(/x=([\d.]+)cm/) || [, '5.2'])[1]);
  const ycm = Number((opt.match(/y=([\d.]+)cm/) || [, '3.6'])[1]);
  const W = 320, H = 230, padL = 46, padB = 34, padT = 18, padR = 12;
  const plotW = W - padL - padR, plotH = H - padB - padT;
  const X = (v) => (padL + v * plotW).toFixed(1);
  const Y = (v) => (H - padB - v * plotH).toFixed(1);

  const out = [];
  const xlab = src.match(/--\s*\(([\d.]+),0\)\s*node\[right\]\s*\{\$?([^}$]*?)\$?\}/);
  const ylab = src.match(/--\s*\(0,([\d.]+)\)\s*node\[above\]\s*\{\$?([^}$]*?)\$?\}/);
  const esc = (v) => String(v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const xlabel = esc(xlab ? xlab[2] : 'x');
  const ylabel = esc(ylab ? ylab[2] : 'y');
  const ticks = ((src.match(/\\foreach\s+\\v\s+in\s*\{([^}]*)\}/) || [])[1] || '0,0.2,0.4,0.6,0.8,1.0')
    .split(',').map((s) => Number(s.trim())).filter((n) => !Number.isNaN(n));

  const diag = /gray,dashed/.test(src);
  const plotLine = src.match(/\\draw\s*\[(\w+),thick\]\s*plot\s+coordinates\s*\{([^}]*)\}/s);
  const pts = [];
  if (plotLine) {
    const body = plotLine[2];
    const re = /\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)/g;
    let m;
    while ((m = re.exec(body))) pts.push([Number(m[1]), Number(m[2])]);
  }
  const points = []; // filled dots
  const fillRe = /\\fill\s*\[\w+\]\s*\(([\d.]+),([\d.]+)\)/g;
  let fm;
  while ((fm = fillRe.exec(src))) points.push([Number(fm[1]), Number(fm[2])]);

  out.push(`<svg class="tikz" viewBox="0 0 ${W} ${H}" role="img">`);
  // ticks + grid labels
  ticks.forEach((v) => {
    out.push(`<line class="axis-tick" x1="${X(v)}" y1="${Y(0)}" x2="${X(v)}" y2="${(Number(Y(0)) + 3).toFixed(1)}"/>`);
    out.push(`<text class="tick" x="${X(v)}" y="${H - padB + 13}" text-anchor="middle">${v}</text>`);
    out.push(`<line class="axis-tick" x1="${X(0)}" y1="${Y(v)}" x2="${(Number(X(0)) - 3).toFixed(1)}" y2="${Y(v)}"/>`);
    out.push(`<text class="tick" x="${padL - 6}" y="${(Number(Y(v)) + 3).toFixed(1)}" text-anchor="end">${v}</text>`);
  });
  // axes
  out.push(`<line class="axis" x1="${X(0)}" y1="${Y(0)}" x2="${(W - padR + 4).toFixed(1)}" y2="${Y(0)}"/>`);
  out.push(`<line class="axis" x1="${X(0)}" y1="${Y(0)}" x2="${X(0)}" y2="${(padT - 6).toFixed(1)}"/>`);
  out.push(`<text class="axtitle" x="${W - padR + 6}" y="${(Number(Y(0)) + 4).toFixed(1)}">${xlabel}</text>`);
  out.push(`<text class="axtitle" x="${padL}" y="${(padT - 9).toFixed(1)}" text-anchor="middle">${ylabel}</text>`);
  if (diag) out.push(`<line class="diag" x1="${X(0)}" y1="${Y(0)}" x2="${X(1)}" y2="${Y(1)}"/>`);
  // curve
  if (pts.length) {
    const color = /blue/.test(plotLine[1]) ? 'var(--curve-a)' : /red/.test(plotLine[1]) ? 'var(--curve-b)' : '#333';
    out.push(`<polyline class="curve" style="stroke:${color}" points="${pts.map(([a, b]) => `${X(a)},${Y(b)}`).join(' ')}"/>`);
    pts.forEach(([a, b]) => out.push(`<circle class="dot" style="fill:${color}" cx="${X(a)}" cy="${Y(b)}" r="2.4"/>`));
  }
  // title node: \node at (.54,1.05) {\small P-R 曲线};
  const t = src.match(/\\node\s+at\s*\(([\d.]+),([\d.]+)\)\s*\{\\small\s+([^}]*)\}/);
  if (t) out.push(`<text class="plotcap" x="${X(Number(t[1]))}" y="${Y(Number(t[2]))}">${t[3]}</text>`);
  out.push('</svg>');
  return out.join('\n');
}

/* ------------------------------------------------------------- block walk */

function convertBody(src) {
  let buf = src;
  const html = [];
  const listStack = [];
  let para = [];
  let openLi = 0; // nesting depth at which an <li> is still open

  const takeLine = () => {
    const nl = buf.indexOf('\n');
    if (nl === -1) { const l = buf; buf = ''; return l; }
    const l = buf.slice(0, nl);
    buf = buf.slice(nl + 1);
    return l;
  };
  const peekLine = () => {
    const nl = buf.indexOf('\n');
    return nl === -1 ? buf : buf.slice(0, nl);
  };

  const flushPara = () => {
    const text = para.join(' ').replace(/\s+/g, ' ').trim();
    para = [];
    if (!text) return;
    if (openLi) html[html.length - 1] += `<p>${inline(text)}</p>`;
    else html.push(`<p>${inline(text)}</p>`);
  };
  const closeLi = () => {
    flushPara();
    if (openLi) { html[html.length - 1] += '</li>'; openLi = 0; }
  };
  /** Close open lists until the stack is `newDepth` deep (0 closes all). */
  const closeLists = (newDepth = 0) => {
    closeLi();
    while (listStack.length > newDepth) html.push(`</${listStack.pop().type}>`);
  };

  /* consume everything of environment `name` that starts at the very beginning
     of the buffer, returning its body. */
  const takeEnv = (name) => {
    const tagRe = new RegExp(`^\\\\begin\\s*\\{${name}\\}(\\[[^\\]]*\\])?`);
    const m = buf.match(tagRe);
    if (!m) return null;
    const endTag = `\\end{${name}}`;
    const end = buf.indexOf(endTag);
    if (end === -1) return null;
    const inner = buf.slice(m[0].length, end);
    buf = buf.slice(end + endTag.length).replace(/^[ \t]*\n?/, '');
    return inner;
  };

  let guard = 0;
  while (buf.trim() !== '' && guard++ < 100000) {
    const line = peekLine();
    const t = line.trim();

    /* blank line: paragraph boundary ---------------------------------- */
    if (t === '') { takeLine(); flushPara(); continue; }

    /* display math \[ ... \] ------------------------------------------ */
    if (t.startsWith('\\[')) {
      takeLine();
      flushPara();
      const closeRe = /(?<!\\)(?:\\\\)*\\\]/g;
      let end = -1;
      for (let m; (m = closeRe.exec(buf)); ) {
        const j = m.index + m[0].length - 2; // index of the backslash pair before ]
        let nb = 0;
        for (let k = j; k >= 0 && buf[k] === '\\'; k--) nb++;
        if (nb % 2 === 1) { end = j + 1; break; } // single \] closes display math
      }
      const tex = buf.slice(0, end === -1 ? buf.length : end);
      html.push(`<div class="eq">${storeMath(tex.trim(), true)}</div>`);
      buf = buf.slice(end === -1 ? buf.length : end + 2);
      continue;
    }

    /* environments ----------------------------------------------------- */
    const envM = t.match(/^\\begin\s*\{([^}]*)\}/);
    if (envM) {
      const name = envM[1];
      const opt = readOpt(line, line.indexOf('}', line.indexOf('\\begin')) + 1);
      const optStr = opt ? opt.inner : '';
      const HANDLED = ['table', 'figure', 'tikzpicture', 'center', 'center*'];
      if (!HANDLED.includes(name)) takeLine();

      if (name === 'enumerate' || name === 'itemize') {
        closeLi();
        flushPara();
        const depth = listStack.length;
        const roomy = /itemsep\s*=\s*0\.(8|9|7)/.test(optStr);
        const tag = name === 'enumerate' ? 'ol' : 'ul';
        const cls = [roomy ? 'roomy' : '', depth > 0 && tag === 'ul' ? 'sub' : ''].filter(Boolean).join(' ');
        const extra = depth > 0 && tag === 'ol' ? ' type="a"' : '';
        html.push(`<${tag}${cls ? ` class="${cls}"` : ''}${extra}>`);
        listStack.push({ type: tag });
        continue;
      }

      if (name === 'table' || name === 'figure') {
        flushPara();
        const inner = takeEnv(name) || '';
        const tab = extractTabular(inner);
        if (tab) {
          const cap = inner.match(/\\caption\s*\{([\s\S]*?)\}\s*(?=\\label|$)/);
          const lab = inner.match(/\\label\s*\{([^}]*)\}/);
          html.push(renderTabular(tab.body, tab.spec, cap ? cap[1].trim() : '', lab ? lab[1] : '').html);
        }
        continue;
      }

      if (name === 'tikzpicture') {
        flushPara();
        const inner = takeEnv(name) || '';
        html.push(`<div class="fig">${renderTikz(inner, optStr)}</div>`);
        continue;
      }

      if (name === 'center' || name === 'center*') {
        flushPara();
        const inner = takeEnv(name) || '';
        const tab = extractTabular(inner);
        if (tab) {
          html.push(renderTabular(tab.body, tab.spec, '', '').html);
        } else if (/\\begin\s*\{/.test(inner)) {
          html.push(`<div class="center">${convertBody(inner)}</div>`);
        } else {
          html.push(`<div class="center">${inline(inner.replace(/\n/g, ' '))}</div>`);
        }
        continue;
      }

      // unknown environment: descend into it (content is emitted inline)
      continue;
    }

    /* \end{...} -------------------------------------------------------- */
    const endM = t.match(/^\\end\s*\{([^}]*)\}/);
    if (endM) {
      takeLine();
      const name = endM[1];
      if (name === 'enumerate' || name === 'itemize') {
        closeLi();
        flushPara();
        const idx = listStack.map((e) => e.type).lastIndexOf(name);
        if (idx !== -1) closeLists(idx); // leave the stack at the matching list
      }
      continue;
    }

    /* \item ------------------------------------------------------------ */
    if (/^\\item\b/.test(t)) {
      takeLine();
      if (openLi) closeLi();
      else flushPara();
      const rest = t.replace(/^\\item\s*(\[[^\]]*\])?/, '').trim();
      html.push('<li>');
      openLi = listStack.length;
      if (rest) para.push(rest);
      continue;
    }

    /* page breaks ------------------------------------------------------ */
    if (/^\\(clearpage|newpage|pagebreak)\b/.test(t)) {
      takeLine(); closeLi(); flushPara();
      html.push('<div class="pagebreak"></div>');
      continue;
    }

    /* \section / \subsection ------------------------------------------- */
    const secM = t.match(/^\\(section|subsection)\*?\s*(?:\[[^\]]*\])?\s*\{([\s\S]*)\}$/);
    if (secM) {
      takeLine();
      closeLi();
      flushPara();
      const tag = secM[1] === 'section' ? 'h2' : 'h3';
      html.push(`<${tag} class="sec">${inline(secM[2])}</${tag}>`);
      continue;
    }

    /* plain paragraph text --------------------------------------------- */
    takeLine();
    para.push(t);
  }

  closeLists(0);
  flushPara();
  return html.join('\n');
}

async function main() {
  const [inFile, outFile, docTitle] = process.argv.slice(2);
  const raw = fs.readFileSync(inFile, 'utf8');
  const clean = stripComments(raw);
  const bodyStart = clean.indexOf('\\begin{document}');
  const bodyEnd = clean.lastIndexOf('\\end{document}');
  let body = clean.slice(bodyStart + '\\begin{document}'.length, bodyEnd);

  // expand project macro \ans
  body = body.replace(/\\ans\b/g, '\\textbf{\\large 解：}');

  const content = convertBody(body);
  const mj = await initMathJax();

  // MathJax typeset all display math items
  const items = M.map((it) => ({ tex: it.tex, display: it.display }));
  const rendered = await mj.typesetAll(items);
  rendered.forEach((svg, k) => { M[k].svg = svg; });

  const finalHtml = content.replace(MATH_RE, (m, idx) => {
    const it = M[Number(idx)];
    return it.svg || `<code>${it.tex}</code>`;
  });
  const leftover = M.filter((it) => !it.svg).length;

  const page = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>${docTitle || path.basename(inFile)}</title>
<style>
${CSS}
</style>
</head>
<body>
<div class="page">
<header class="runhead"><span>2026年秋季</span><span>机器学习</span><span>作业一</span></header>
<main>
${finalHtml}
</main>
<footer class="runfoot"></footer>
</div>
</body>
</html>
`;
  fs.writeFileSync(outFile, page, 'utf8');

  // Guard: leftover LaTeX in the printed HTML means a construct was not parsed
  // (this is how the `c@{\\quad}` column-spec bug reached the page).
  const LEAK = /\\(begin|end)\s*\{|\\(top|mid|bottom)rule|\\cmidrule|\\caption|\\multirow|\\multicolumn|\\item\b/;
  const leaks = (finalHtml.match(new RegExp(LEAK.source, 'g')) || []);
  const leakKinds = [...new Set(leaks)];

  // Guard: every table must have a uniform column count and no cell may hold
  // LaTeX furniture (an unbalanced spec used to leak "ccc@{\\quad}ccc}" here).
  const tables = [...finalHtml.matchAll(/<table class="booktabs">([\s\S]*?)<\/table>/g)];
  const tableIssues = [];
  tables.forEach((t, ti) => {
    // Count logical columns: a colspan="3" cell occupies three columns, a
    // rowspan cell is still one column on its row.
    const rows = [...t[1].matchAll(/<tr[^>]*>([\s\S]*?)<\/tr>/g)].map((r) => {
      let n = 0;
      for (const c of r[1].matchAll(/<td([^>]*)>/g)) n += Number((c[1].match(/colspan="(\d+)"/) || [, '1'])[1]);
      return n;
    });
    if (new Set(rows).size > 1) tableIssues.push(`table ${ti + 1}: uneven columns ${rows.join('/')}`);
    const cells = [...t[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((c) => c[1]);
    cells.forEach((c) => {
      const plain = c.replace(/<svg[\s\S]*?<\/svg>/g, '');
      if (/@\{|\\[a-zA-Z]+|\$/.test(plain)) tableIssues.push(`table ${ti + 1}: LaTeX left in cell "${plain.slice(0, 30)}"`);
    });
  });

  console.log(`wrote ${outFile}: ${content.length} chars, ${M.length} math items, ${leftover} unrendered, ${tables.length} tables`);
  if (tableIssues.length) tableIssues.slice(0, 8).forEach((m) => console.error(`  !! TABLE PROBLEM: ${m}`));
  else console.log('  ok: all tables have uniform columns and clean cells');
  if (leaks.length) {
    console.error(`  !! WARNING: ${leaks.length} unparsed LaTeX token(s) in output: ${leakKinds.join(', ')}`);
    const at = finalHtml.search(LEAK);
    console.error(`     first at char ${at}: ...${finalHtml.slice(Math.max(0, at - 70), at + 90).replace(/\n/g, ' ')}...`);
  } else {
    console.log('  ok: no unparsed LaTeX left in the output');
  }
}

const CSS = `
/* Print sizes follow LaTeX article[8pt]: body 8pt, \\section 11.2pt (\\large),
   \\Large 13.4pt, \\small 7.4pt. 1 CSS px prints as 0.72pt, so these are set
   with pt directly and verified against the PDF text operators. */
:root{ --curve-a:#1565c0; --curve-b:#c62828; --rule:#000; --text:#111; }
*{box-sizing:border-box;}
html,body{margin:0;padding:0;}
body{
  /* "Songti SC" alone resolves to the Bold face here; naming the weight
     explicitly is what yields the regular face. */
  font-family:"Songti SC Regular","Songti SC","STSong","Noto Serif CJK SC","Times New Roman",serif;
  font-size:8pt; line-height:1.45; color:var(--text);
  -webkit-print-color-adjust:exact; print-color-adjust:exact;
}
@page{ size:A4; margin:0; }
.runhead{display:none;}
main{
  /* geometry: total={6in,8in} centered on A4 -> 6in wide, 25.4mm + 25.4mm tall */
  width:6in; margin:0 auto; padding:25.4mm 0;
}
p{margin:0 0 .42em 0; text-align:justify; text-justify:inter-ideograph; text-indent:0;}
.eq{margin:.4em 0 .5em 0; text-align:center;}
.eq mjx-container[display="true"]{margin:0 !important;}
h2.sec{font-size:11.2pt; font-weight:bold; margin:.85em 0 .5em 0; text-align:left;
  break-after:avoid; break-inside:avoid;}
h3{font-size:9.8pt; margin:.75em 0 .4em 0;}
b,strong{font-weight:bold;}
.fs-Large{font-size:13.4pt; font-weight:bold;}
.fs-large{font-size:11.2pt; font-weight:bold;}
.color-blue{color:#0000cc;}
code{font-family:Menlo,monospace; font-size:.95em;}
ul,ol{margin:.3em 0 .5em 0; padding-left:2.5em;}
ol.roomy > li{margin-bottom:.5em;}
ol.sub,ul.sub{padding-left:2.2em;}
ol.sub{list-style-type:lower-alpha;}
li{margin-bottom:.12em;}
li > p{margin:.18em 0;}
.pagebreak{break-after:page; height:0;}
.tablewrap{text-align:center; margin:.6em 0 .8em 0; break-inside:avoid;}
table.booktabs{border-collapse:collapse; margin:0 auto; font-size:7.4pt;}
table.booktabs td{padding:1px 6px; text-align:center; white-space:nowrap;}
table.booktabs td.ta-left{text-align:left;} table.booktabs td.ta-right{text-align:right;}
table.booktabs tr.ruletop td{border-top:1.2px solid var(--rule); border-bottom:.7px solid var(--rule);}
table.booktabs tr.rulemid td{border-bottom:.7px solid var(--rule);}
table.booktabs tr.rulebottom td{border-bottom:1.2px solid var(--rule);}
/* \\cmidrule{2-4}: booktabs draws this partial rule just under the first header
   row, spanning only those columns (all of which carry the cm-N-M class). */
table.booktabs tr.ruletop td[class*="cm-"]{
  border-bottom:none;
  background-image:linear-gradient(var(--rule),var(--rule));
  background-repeat:no-repeat; background-position:left 100%; background-size:100% .7px;
}
.caption{caption-side:bottom; font-size:7.4pt; margin-top:.25em; text-align:center;}
.center{text-align:center; margin:.45em 0;}
.fig{text-align:center; margin:.6em 0 .9em 0; break-inside:avoid;}
svg.tikz{width:96mm; height:auto;}
svg.tikz .axis{stroke:#111; stroke-width:.9;}
svg.tikz .axis-tick{stroke:#111; stroke-width:.8;}
svg.tikz .tick{font:6.6px "Songti SC Regular",serif; fill:#111;}
svg.tikz .axtitle{font:8px "Songti SC Regular",serif; fill:#111;}
svg.tikz .curve{fill:none; stroke-width:1.4;}
svg.tikz .diag{stroke:#9a9a9a; stroke-dasharray:4 3; stroke-width:.8;}
svg.tikz .plotcap{font:7.4px "Songti SC Regular",serif; fill:#111; text-anchor:middle;}
mjx-container{font-size:100% !important;}
mjx-container svg{vertical-align:-0.25em;}
`;
main().catch((e) => { console.error(e); process.exit(1); });
