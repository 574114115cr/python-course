/* 深色/浅色两套主题的真实对比度审计（CDP，不靠肉眼）。
 *
 * 查三件事：
 *  1. 每个可见文本元素的 WCAG 对比度（正文 4.5、大字号 3.0），两套主题都查；
 *  2. 深色下仍然是浅底的面板（漏翻的白块）—— 这是「刺眼/看不清」的主因；
 *  3. 切换按钮：每页都有、点得动、三态循环、刷新后记得住。
 *
 * 用法：
 *   node tools/verify_dark.mjs                 # 审计
 *   node tools/verify_dark.mjs --shots .cache/shots   # 顺手截图，肉眼复核
 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PYTHON = 'C:/Users/57411/.workbuddy/binaries/python/envs/default/Scripts/python.exe';
const ROOT_DIR = path.resolve(import.meta.dirname, '..');
const PORT = 8092;
const CDP_PORT = 9787;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'dark-verify-'));
const shotDir = (() => {
  const i = process.argv.indexOf('--shots');
  return i > 0 ? path.resolve(ROOT_DIR, process.argv[i + 1]) : null;
})();

const PAGES = [
  'index.html',
  'python-course-syllabus.html',
  'python-learning-roadmap.html',
  'web/00.html',
  'web/05.html',
  'web/lessons/index.html',
  'web/lessons/01.html',
  'web/lessons/45.html',
  'web/bank.html',
  'web/gate1.html',
  'web/terms.html',
  'web/coverage.html',
  'web/plan.html',
  'web/review.html',
  'web/ppt/index.html',
  'fluent/index.html',
  'fluent/web/01.html',
  'fluent/web/lessons/l01.html',
  'fluent/web/lessons/index.html',
  'fluent/web/bank.html',
  'fluent/web/gates.html',
  'fluent/web/syllabus.html',
  'fluent/web/terms.html',
  'fluent/web/bench.html',
  'fluent/web/ch/01.html',
  'fluent/web/walk/u01.html',
  'fluent/web/ppt/index.html',
];

const server = spawn(PYTHON, ['tools/serve.py', String(PORT)],
  { cwd: ROOT_DIR, stdio: 'ignore' });
const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${CDP_PORT}`,
  `--user-data-dir=${PROFILE}`, '--no-first-run', '--no-default-browser-check',
  '--window-size=1440,900', 'about:blank',
], { stdio: 'ignore' });

function cleanup() { try { server.kill(); } catch {} try { chrome.kill(); } catch {} }

const SCAN = `(() => {
  const lum = (c) => { const a = c.map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
    return 0.2126*a[0] + 0.7152*a[1] + 0.0722*a[2]; };
  const ratio = (f, b) => { const a = lum(f), b2 = lum(b); const hi = Math.max(a,b2), lo = Math.min(a,b2);
    return (hi + 0.05) / (lo + 0.05); };
  const parse = (s) => { const m = s.match(/rgba?\\(([^)]+)\\)/); if (!m) return null;
    const p = m[1].split(/[,/\\s]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const over = (fg, bg) => [0,1,2].map(i => Math.round(fg[i]*fg[3] + bg[i]*(1-fg[3])));
  // 沿祖先找真正的底色（透明就往上，遇到渐变图就放弃）
  function bgOf(el) {
    let acc = null, node = el;
    const stack = [];
    while (node && node !== document.documentElement) {
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { stack.push(c); if (c.a >= 0.999) break; }
      node = node.parentElement;
    }
    const bodyCs = getComputedStyle(document.body);
    let base = [255,255,255];
    const bc = parse(bodyCs.backgroundColor);
    if (bc && bc.a > 0.99) base = [bc.r, bc.g, bc.b];
    acc = base;
    for (let i = stack.length - 1; i >= 0; i--) acc = over([stack[i].r, stack[i].g, stack[i].b, stack[i].a], acc);
    return acc;
  }
  function sel(el) {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const cl = (el.className && typeof el.className === 'string') ? el.className.trim().split(/\\s+/).slice(0,2) : [];
    if (cl.length) s += '.' + cl.join('.');
    return s;
  }
  // content-visibility:auto 的子树默认没几何信息，先全部摊开再量
  const fix = document.createElement('style');
  fix.id = '__cvfix';
  fix.textContent = '*{content-visibility:visible!important;contain-intrinsic-size:auto!important;'
    + 'transition:none!important;animation:none!important}';
  document.head.appendChild(fix);
  const low = [], lightPatches = [];
  let checked = 0, skipped = 0;
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const own = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim()).map(n => n.textContent.trim()).join(' ');
    const r = el.getBoundingClientRect();
    if (own) {
      if (parseFloat(cs.opacity) < 0.5) continue;
      if (r.width < 2 || r.height < 2) continue;
      const fg = parse(cs.color);
      const bg = fg ? bgOf(el) : null;
      if (!fg || !bg) { skipped++; continue; }
      const f = over([fg.r, fg.g, fg.b, fg.a], bg);
      const cr = ratio(f, bg);
      checked++;
      const size = parseFloat(cs.fontSize);
      const bold = (parseInt(cs.fontWeight, 10) || 400) >= 600;
      const need = (size >= 24 || (bold && size >= 18.66)) ? 3.0 : 4.5;
      if (cr < need) low.push({ sel: sel(el), text: own.slice(0, 34), cr: +cr.toFixed(2), need,
        color: cs.color, bg: 'rgb(' + bg.join(',') + ')', size });
    }
    // 深色下仍是浅底的大块
    if (cs.backgroundImage === 'none') {
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0.6 && r.width * r.height > 4000) {
        const L = lum([c.r, c.g, c.b]);
        if (L > 0.5) lightPatches.push({ sel: sel(el), L: +L.toFixed(2), area: Math.round(r.width * r.height), html: el.outerHTML.slice(0, 90) });
      }
    }
  }
  fix.remove();
  low.sort((a, b) => a.cr - b.cr);
  lightPatches.sort((a, b) => b.area - a.area);
  return JSON.stringify({
    checked, skipped, lowN: low.length, patchN: lightPatches.length,
    low: low.slice(0, 14), patches: lightPatches.slice(0, 10),
  });
})()`;

async function main() {
  let up = false;
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/index.html`); if (r.ok) { up = true; break; } } catch {}
    await sleep(250);
  }
  if (!up) throw new Error('serve.py 未起来');

  let targets = null;
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${CDP_PORT}/json/list`);
      if (r.ok) { targets = await r.json(); if (targets.some(t => t.type === 'page')) break; }
    } catch {}
    await sleep(250);
  }
  const page = targets.find(t => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('ws fail')); });
  let id = 0; const pending = new Map(); const events = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    else if (m.method) events.push(m.method);
  };
  const send = (method, params = {}) => new Promise((res) => {
    const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
  });
  const evaluate = (expr, awaitPromise = false) =>
    send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise })
      .then(r => {
        if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 300));
        return r.result?.result?.value;
      });
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride',
    { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });

  async function open(rel) {
    const url = `http://127.0.0.1:${PORT}/${rel}`;
    const loaded = new Promise((res) => {
      const t = setInterval(() => { if (events.includes('Page.loadEventFired')) { clearInterval(t); res(); } }, 40);
      setTimeout(() => { clearInterval(t); res(); }, 12000);
    });
    events.length = 0;
    await send('Page.navigate', { url });
    await loaded;
    await sleep(120);
  }

  const pass = [], fail = [], detail = [];
  const expect = (n, ok, extra) => { (ok ? pass : fail).push(n + (extra ? ' ' + extra : '')); };

  if (shotDir) fs.mkdirSync(shotDir, { recursive: true });

  for (const rel of PAGES) {
    await open(rel);
    const hasBtn = await evaluate(`!!document.getElementById('thBtn')`);
    const btnBox = await evaluate(`(() => { const b = document.getElementById('thBtn');
      if (!b) return 'none'; const r = b.getBoundingClientRect();
      const cs = getComputedStyle(b); return [r.width|0, r.height|0, cs.display, cs.visibility].join('|'); })()`);
    const inChrome = await evaluate(`(() => { const b = document.getElementById('thBtn');
      return b ? !!b.closest('.top-in, .nav-in') : false; })()`);
    expect(`${rel} 切换按钮`, hasBtn && !btnBox.startsWith('0|') && !btnBox.includes('none'),
      btnBox + (inChrome ? ' 顶栏内' : ' 悬浮'));

    // 三态循环 + 持久化
    const cycle = await evaluate(`(() => {
      const r = document.documentElement, out = [];
      window.__theme.set('auto'); out.push(r.getAttribute('data-theme-mode') + '/' + r.getAttribute('data-theme'));
      window.__theme.set('light'); out.push(r.getAttribute('data-theme-mode') + '/' + r.getAttribute('data-theme'));
      window.__theme.set('dark'); out.push(r.getAttribute('data-theme-mode') + '/' + r.getAttribute('data-theme'));
      out.push(localStorage.getItem('py-theme-v1'));
      out.push(getComputedStyle(r).colorScheme);
      return out.join(',');
    })()`);
    expect(`${rel} 主题三态`, /auto\/\w+,light\/light,dark\/dark,dark,dark/.test(cycle), cycle);

    for (const theme of ['light', 'dark']) {
      await evaluate(`window.__theme.set('${theme}')`);
      await sleep(160);
      const raw = await evaluate(SCAN);
      const r = JSON.parse(raw);
      if (shotDir) {
        const name = rel.replace(/[\\/]/g, '_').replace(/\.html$/, '') + '-' + theme + '.png';
        const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
        if (shot.result?.data) fs.writeFileSync(path.join(shotDir, name), Buffer.from(shot.result.data, 'base64'));
      }
      expect(`${rel} ${theme} 对比度`, r.lowN === 0, `查 ${r.checked} 处，低于标准 ${r.lowN}（跳过 ${r.skipped}）`);
      if (r.lowN) detail.push(`  ${rel} [${theme}] 低对比 ${r.lowN}：` +
        r.low.map(o => `\n    ${o.cr}:1 (需${o.need}) ${o.sel} "${o.text}" ${o.color} on ${o.bg}`).join(''));
      if (theme === 'dark') {
        expect(`${rel} 深色无浅底残留`, r.patchN === 0, `浅底块 ${r.patchN}`);
        if (r.patchN) detail.push(`  ${rel} [dark] 浅底残留：` +
          r.patches.map(o => `\n    L=${o.L} ${o.area}px² ${o.sel}  ${o.html}`).join(''));
      }
    }
    // 刷新后是否记得
    await evaluate(`window.__theme.set('dark')`);
    await open(rel);
    const kept = await evaluate(`document.documentElement.getAttribute('data-theme')`);
    expect(`${rel} 刷新记住选择`, kept === 'dark', kept);
    await evaluate(`window.__theme.set('auto')`);
  }

  console.log('PASS ' + pass.length);
  if (fail.length) {
    console.log('\nFAIL ' + fail.length + '：');
    for (const f of fail) console.log('  ✗ ' + f);
  }
  if (detail.length) {
    console.log('\n明细：');
    for (const d of detail) console.log(d);
  }
  if (fail.length) { cleanup(); process.exit(2); }
  console.log('\nDARK_ALL_PASS');
  ws.close(); cleanup();
}
main().catch(e => { console.error('ERR', e.message); cleanup(); process.exit(1); });
