/* fluent 课程站点自检：390px 横向溢出 + 本地链接 404 + 基础结构 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import fs from 'node:fs';
import path from 'node:path';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9793;
const ROOT_DIR = path.resolve(import.meta.dirname, '..');
const ROOT = 'file:///' + ROOT_DIR.replace(/\\/g, '/') + '/fluent';
const DIR = path.join(ROOT_DIR, 'fluent');

const pages = ['index.html'];
for (let i = 1; i <= 12; i++) pages.push(`web/${String(i).padStart(2, '0')}.html`);
pages.push('web/lessons/index.html');
for (let i = 1; i <= 48; i++) pages.push(`web/lessons/l${String(i).padStart(2, '0')}.html`);
pages.push('web/bank.html', 'web/gates.html', 'web/ppt/index.html');
pages.push('web/ppt/u/index.html');
pages.push('web/coverage.html', 'web/terms.html', 'web/review.html', 'web/bench.html');
pages.push('web/syllabus.html');
pages.push('web/ch/index.html');
for (let i = 1; i <= 24; i++) pages.push(`web/ch/${String(i).padStart(2, '0')}.html`);
pages.push('web/walk/index.html');
for (let i = 1; i <= 12; i++) pages.push(`web/walk/u${String(i).padStart(2, '0')}.html`);
for (let i = 1; i <= 12; i++) pages.push(`web/ppt/u/${String(i).padStart(2, '0')}.html`);

const ALL = pages.map(p => `${ROOT}/${p}`);

// ── 1. 链接检查（离线、纯文件系统） ──
const missing = [];
for (const p of pages) {
  const abs = path.join(DIR, p);
  const html = fs.readFileSync(abs, 'utf8');
  for (const m of html.matchAll(/href="([^"]+)"/g)) {
    const href = m[1];
    if (/^(#|https?:|data:|mailto:)/.test(href)) continue;
    if (href.includes("'") || href.includes('+')) continue;  // 跳过脚本里拼接的字符串
    const target = href.split('#')[0];
    if (!target) continue;
    const t = path.resolve(path.dirname(abs), target);
    if (!fs.existsSync(t)) missing.push([p, href]);
  }
}
console.log(`链接检查：${pages.length} 页，缺失 ${missing.length} 条`);
missing.slice(0, 20).forEach(([p, h]) => console.log('  ✗', p, '→', h));

// ── 2. 390px 溢出 ──
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
      return { over: de.scrollWidth - de.clientWidth,
               h1: document.querySelectorAll('h1').length,
               title: document.title };
    })()`);
  }

  const bad = [];
  for (const u of ALL) {
    const r = await probe(u);
    if (r.over > 0) bad.push([u.replace(ROOT + '/', ''), r.over]);
  }
  console.log(`390px 扫描：${ALL.length} 页，溢出 ${bad.length} 页`);
  bad.forEach(([u, o]) => console.log('  ✗', u, '+' + o + 'px'));

  // 首页进度脚本是否可跑
  await probe(`${ROOT}/index.html`);
  const prog = await evaluate(`(() => {
    const t = document.getElementById('tL');
    return t ? t.textContent : 'missing';
  })()`);
  console.log('首页进度文本:', prog);

  // 复习计划页：灌入假进度，验证排程 / 逾期 / 标记完成
  await probe(`${ROOT}/web/review.html`);
  const seeded = await evaluate(`(() => {
    try {
      var d = new Date(); d.setDate(d.getDate() - 3);
      localStorage.setItem('fl-lesson-v1', JSON.stringify({ '1': d.getTime(), '2': Date.now() }));
      localStorage.setItem('fl-review-v1', JSON.stringify({ '1': [Date.now()] }));
      return 'ok';
    } catch (e) { return 'ERR:' + e.message; }
  })()`);
  console.log('灌入复习测试数据:', seeded);
  await evaluate('location.reload()');
  await sleep(600);
  const rv = await evaluate(`(() => JSON.stringify({
    today: document.getElementById('rvTT').textContent,
    over: document.getElementById('rvTO').textContent,
    rounds: document.getElementById('rvTR').textContent,
    items: document.querySelectorAll('#rvNow .rv-item').length,
    overItems: document.querySelectorAll('#rvNow .rv-item.over').length,
    curve: document.querySelectorAll('#rvCurve .rv-c').length
  }))()`);
  console.log('复习排程:', rv);
  const rvOk = rv === JSON.stringify({
    today: '2 项', over: '1 项', rounds: '1 / 288',
    items: 3, overItems: 1, curve: 2
  });
  console.log(rvOk ? '复习排程符合预期 ✓' : '复习排程与预期不符 ✗');
  await evaluate(`document.querySelector('#rvNow button[data-g]').click()`);
  const rv2 = await evaluate(`document.getElementById('rvTR').textContent`);
  console.log('标记一轮后:', rv2, rv2 === '2 / 288' ? '✓' : '✗');
  await evaluate(`localStorage.clear()`);

  ws.close();
  proc.kill();
}

main().catch(e => { console.error(e); proc.kill(); process.exit(1); });
