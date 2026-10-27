/* 全站 390px 横向溢出扫描 + 课节页侧栏行为抽查 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9782;
const ROOT_DIR = path.resolve(import.meta.dirname, '..');
const ROOT = 'file:///' + ROOT_DIR.replace(/\\/g, '/');

const lessons = Array.from({ length: 111 }, (_, i) =>
  `${ROOT}/web/lessons/${String(i + 1).padStart(2, '0')}.html`);
const units = Array.from({ length: 22 }, (_, i) => `${ROOT}/web/${String(i).padStart(2, '0')}.html`);
const players = Array.from({ length: 22 }, (_, i) => `${ROOT}/web/ppt/u/${String(i).padStart(2, '0')}.html`);
const others = [
  `${ROOT}/index.html`, `${ROOT}/python-learning-roadmap.html`, `${ROOT}/python-course-syllabus.html`,
  `${ROOT}/web/lessons/index.html`, `${ROOT}/web/bank.html`, `${ROOT}/web/gate1.html`,
  `${ROOT}/web/gate2.html`, `${ROOT}/web/ppt/index.html`, `${ROOT}/web/ppt/u/index.html`,
  `${ROOT}/web/review.html`, `${ROOT}/web/terms.html`, `${ROOT}/web/coverage.html`,
];
const ALL = [...lessons, ...units, ...players, ...others];

const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`,
  '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });

async function main() {
  let targets = null;
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
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
  const evaluate = (expr) => send('Runtime.evaluate', { expression: expr, returnByValue: true })
    .then(r => r.result.result.value);
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride',
    { width: 390, height: 844, deviceScaleFactor: 1, mobile: false });

  async function probe(url) {
    const loaded = new Promise((res) => {
      const t = setInterval(() => { if (events.includes('Page.loadEventFired')) { clearInterval(t); res(); } }, 50);
      setTimeout(() => { clearInterval(t); res(); }, 6000);
    });
    events.length = 0;
    await send('Page.navigate', { url });
    await loaded;
    await sleep(120);
    return evaluate(`(() => {
      const de = document.documentElement;
      return de.scrollWidth - de.clientWidth;
    })()`);
  }

  const bad = [];
  for (const u of ALL) {
    const over = await probe(u);
    if (over > 0) bad.push([u.replace(`${ROOT}/`, ''), over]);
  }
  console.log(`扫描 ${ALL.length} 页 @390px，溢出 ${bad.length} 页`);
  bad.forEach(([u, o]) => console.log('  ✗', u, '+' + o + 'px'));

  // 课节页侧栏行为抽查（第 1 / 63 / 111 节）
  const sideChecks = [];
  for (const u of [`${ROOT}/web/lessons/01.html`, `${ROOT}/web/lessons/63.html`, `${ROOT}/web/lessons/111.html`]) {
    const loaded = new Promise((res) => {
      const t = setInterval(() => { if (events.includes('Page.loadEventFired')) { clearInterval(t); res(); } }, 50);
      setTimeout(() => { clearInterval(t); res(); }, 6000);
    });
    events.length = 0;
    await send('Page.navigate', { url: u });
    await loaded;
    await sleep(200);
    const r = await evaluate(`(() => {
      const side = document.querySelector('.side'), main = document.querySelector('.main');
      const rs = side.getBoundingClientRect(), rm = main.getBoundingClientRect();
      return JSON.stringify({
        side: getComputedStyle(side).display,
        mainFirst: rm.top <= rs.top,
        toc: !!document.querySelector('.side .toc a'),
        ppt: !!document.querySelector('.side .pptbox'),
        links: document.querySelectorAll('.side .nlist a').length,
        allCatalog: !!document.querySelector('.side .nall')
      });
    })()`);
    sideChecks.push([u.split('/').pop(), r]);
  }
  sideChecks.forEach(([n, r]) => console.log('侧栏', n, r));

  ws.close(); proc.kill();
  fs.writeFileSync(path.join(os.tmpdir(), 'sweep_result.json'),
    JSON.stringify({ scanned: ALL.length, bad }, null, 2));
  if (bad.length) process.exit(2);
  console.log('ALL_PAGES_NO_OVERFLOW');
}
main().catch(e => { console.error('ERR', e.message); try { proc.kill(); } catch {} process.exit(1); });
