/**
 * gen_pdf.mjs — render a styled HTML file to PDF with headless Chromium, and
 * additionally report layout diagnostics (content width vs. the 6in text
 * block) using Chrome's DevTools Protocol. Falls back to the simple
 * --print-to-pdf path when CDP is unavailable.
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const [htmlPath, pdfPath] = process.argv.slice(2);
const abs = path.resolve(htmlPath);

const profile = path.join(process.cwd(), 'chrome-profile-v2');
const port = 9333;

const chrome = spawn(CHROME, [
  '--headless=old',
  '--no-sandbox',
  '--disable-gpu',
  '--disable-crash-reporter',
  '--disable-breakpad',
  '--disable-background-networking',
  '--disable-component-update',
  '--disable-sync',
  '--disable-extensions',
  '--no-first-run',
  `--user-data-dir=${profile}`,
  `--remote-debugging-port=${port}`,
  '--no-pdf-header-footer',
  `--print-to-pdf=${path.resolve(pdfPath)}`,
  `file://${abs}`,
], { stdio: ['ignore', 'ignore', 'ignore'] });

const get = (url) =>
  new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function diagnostics() {
  let targets;
  for (let i = 0; i < 40; i++) {
    try { targets = JSON.parse(await get(`http://127.0.0.1:${port}/json/list`)); break; }
    catch { await sleep(250); }
  }
  if (!targets) return null;
  const page = targets.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
  if (!page) return null;

  const { WebSocket } = await import('ws').catch(() => ({ WebSocket: null }));
  if (!WebSocket) return null;

  return await new Promise((resolve) => {
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    let id = 0;
    const pending = new Map();
    const send = (method, params = {}) => new Promise((res) => {
      const mid = ++id;
      pending.set(mid, res);
      ws.send(JSON.stringify({ id: mid, method, params }));
    });
    ws.on('message', (raw) => {
      const msg = JSON.parse(raw.toString());
      if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); }
    });
    ws.on('open', async () => {
      const expr = `(() => {
        const main = document.querySelector('main');
        const r = main.getBoundingClientRect();
        const cw = main.clientWidth;
        const over = [];
        for (const el of document.querySelectorAll('main *')) {
          const b = el.getBoundingClientRect();
          if (b.width > cw + 1) over.push([el.tagName + (el.className ? '.' + String(el.className).split(' ')[0] : ''), Math.round(b.width)]);
        }
        return JSON.stringify({ contentWidthPx: cw, mainLeft: r.left, over: over.slice(0, 12),
          tables: [...document.querySelectorAll('table')].map(t => Math.round(t.getBoundingClientRect().width)),
          figs: [...document.querySelectorAll('svg.tikz')].map(t => Math.round(t.getBoundingClientRect().width)) });
      })()`;
      const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
      resolve(res && res.result ? res.result.value : null);
      ws.close();
    });
  });
}

try {
  const d = await diagnostics();
  if (d) {
    const j = JSON.parse(d);
    const pt = (px) => (px * 0.72).toFixed(1);
    console.log(`content width: ${j.contentWidthPx}px = ${pt(j.contentWidthPx)}pt (6in = 432pt)`);
    console.log(`table widths (pt): ${j.tables.map(pt).join(', ')}`);
    console.log(`figure widths (pt): ${j.figs.map(pt).join(', ')}`);
    if (j.over.length) console.log('ELEMENTS WIDER THAN TEXT BLOCK:', j.over.map(([n, w]) => `${n}:${pt(w)}pt`).join(', '));
    else console.log('no element exceeds the text block width');
  } else {
    console.log('(CDP diagnostics unavailable; PDF written by --print-to-pdf)');
  }
} finally {
  await sleep(1500);
  chrome.kill('SIGKILL');
}

// wait for the pdf to settle
for (let i = 0; i < 40 && !fs.existsSync(pdfPath); i++) await sleep(250);
console.log(`${pdfPath}: ${fs.existsSync(pdfPath) ? fs.statSync(pdfPath).size + ' bytes' : 'MISSING'}`);
