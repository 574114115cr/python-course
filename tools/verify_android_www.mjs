/* android/www 渲染验证：404 监听 + 390px 布局 + 侧栏行为 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import path from 'node:path';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PYTHON = 'C:/Users/57411/.workbuddy/binaries/python/envs/default/Scripts/python.exe';
const WWW = path.resolve(import.meta.dirname, '..', 'android', 'www');
const PORT = 8092;
const CDP_PORT = 9786;

// 直接用 python -m http.server 起静态服务（目录=android/www）
const server = spawn(PYTHON, ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'],
  { cwd: WWW, stdio: 'ignore' });
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${CDP_PORT}`,
  '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });

function cleanup() { try { server.kill(); } catch {} try { chrome.kill(); } catch {} }

async function main() {
  let up = false;
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/index.html`); if (r.ok) { up = true; break; } } catch {}
    await sleep(250);
  }
  if (!up) throw new Error('http.server 未起来');
  console.log('www 服务就绪');

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
  let id = 0; const pending = new Map(); const events = []; const net = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    else if (m.method === 'Page.loadEventFired') events.push(m.method);
    else if (m.method === 'Network.responseReceived') {
      const r = m.params.response;
      if (r.status >= 400) net.push(r.status + ' ' + r.url.replace(`http://127.0.0.1:${PORT}/`, ''));
    }
  };
  const send = (method, params = {}) => new Promise((res) => {
    const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
  });
  const evaluate = (expr, awaitPromise = false) => send('Runtime.evaluate',
    { expression: expr, returnByValue: true, awaitPromise })
    .then(r => r.result?.result?.value);
  await send('Page.enable');
  await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride',
    { width: 390, height: 844, deviceScaleFactor: 1, mobile: false });

  async function open(url) {
    const loaded = new Promise((res) => {
      const t = setInterval(() => { if (events.length) { clearInterval(t); res(); } }, 50);
      setTimeout(() => { clearInterval(t); res(); }, 10000);
    });
    events.length = 0;
    await send('Page.navigate', { url });
    await loaded;
    await sleep(500);
  }

  const PAGES = [
    'index.html',
    'web/lessons/05.html',
    'web/lessons/index.html',
    'web/bank.html',
    'web/gate1.html',
    'web/ppt/index.html',
    'web/ppt/u/01.html',
    'web/08.html',
    'python-course-syllabus.html',
    'python-learning-roadmap.html',
  ];

  const pass = [], fail = [];
  const expect = (n, ok) => (ok ? pass : fail).push(n);

  for (const p of PAGES) {
    net.length = 0;
    await open(`http://127.0.0.1:${PORT}/${p}`);
    const info = await evaluate(`(() => {
      const de = document.documentElement;
      const side = document.querySelector('.side');
      return JSON.stringify({
        title: document.title.slice(0, 24),
        overflow: de.scrollWidth - de.clientWidth,
        side: side ? getComputedStyle(side).display : 'N/A',
        nativeJs: !!document.querySelector('script[src*="app-native.js"]'),
        chromeCss: !!document.querySelector('link[href*="app-chrome.css"]')
      });
    })()`);
    const o = JSON.parse(info);
    console.log(p.padEnd(30), JSON.stringify(o));
    expect(`${p} 无 404`, net.length === 0);
    if (net.length) console.log('    404:', net.slice(0, 5).join(' ; '));
    expect(`${p} 无横向溢出`, o.overflow <= 0);
    expect(`${p} 注入了 app-chrome.css`, o.chromeCss);
    expect(`${p} 注入了 app-native.js`, o.nativeJs);
  }

  // app-native.js 语法有效性（new Function 包裹检查）
  const jsOk = await evaluate(`fetch('app-native.js').then(r => r.text()).then(t => {
    try { new Function(t); return 'OK'; } catch (e) { return 'BAD:' + e.message; }
  })`, true);
  console.log('app-native.js 语法:', jsOk);
  expect('app-native.js 语法合法', jsOk === 'OK');

  console.log('\nPASS ' + pass.length + ' 项；FAIL ' + fail.length + ' 项');
  fail.forEach(f => console.log('  ✗', f));
  ws.close(); cleanup();
  if (fail.length) process.exit(2);
  console.log('WWW_ALL_PASS');
}
main().catch(e => { console.error('ERR', e.message); cleanup(); process.exit(1); });
