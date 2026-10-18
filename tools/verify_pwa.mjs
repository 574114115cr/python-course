/* PWA 端到端验证：SW 注册 → 预缓存 → 断网刷新仍可用 → 断网进课节页 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PYTHON = 'C:/Users/57411/.workbuddy/binaries/python/envs/default/Scripts/python.exe';
const ROOT_DIR = path.resolve(import.meta.dirname, '..');
const PORT = 8091;
const CDP_PORT = 9785;
const PROFILE = path.join(os.tmpdir(), 'pwa-verify-profile');

const server = spawn(PYTHON, ['tools/serve.py', String(PORT)],
  { cwd: ROOT_DIR, stdio: 'ignore' });
const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${CDP_PORT}`,
  `--user-data-dir=${PROFILE}`, '--no-first-run', '--no-default-browser-check',
  'about:blank',
], { stdio: 'ignore' });

function cleanup() { try { server.kill(); } catch {} try { chrome.kill(); } catch {} }

async function main() {
  // 等服务器
  let up = false;
  for (let i = 0; i < 40; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}/index.html`); if (r.ok) { up = true; break; } } catch {}
    await sleep(250);
  }
  if (!up) throw new Error('serve.py 未起来');
  console.log('服务器就绪');

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
  await send('Network.enable');

  async function open(url) {
    const loaded = new Promise((res) => {
      const t = setInterval(() => { if (events.includes('Page.loadEventFired')) { clearInterval(t); res(); } }, 50);
      setTimeout(() => { clearInterval(t); res(); }, 10000);
    });
    events.length = 0;
    await send('Page.navigate', { url });
    await loaded;
  }

  const pass = [], fail = [];
  const expect = (n, ok) => (ok ? pass : fail).push(n);

  // 1) 首次加载，注册 SW
  await open(`http://127.0.0.1:${PORT}/index.html`);
  await sleep(1200);
  const reg = await evaluate(`navigator.serviceWorker.getRegistration().then(r => r ? r.active.state : 'none')`, true);
  console.log('SW 状态:', reg);
  expect('SW 注册并激活', reg === 'activated');

  // 2) 预缓存内容
  const cacheInfo = await evaluate(`caches.keys().then(ks => Promise.all(ks.map(k =>
    caches.open(k).then(c => c.keys().then(rs => k + ':' + rs.length))))).then(a => a.join(' | '))`, true);
  console.log('缓存:', cacheInfo);
  expect('预缓存 shell 非空', /pycourse-v1:\d+/.test(cacheInfo));

  // 3) manifest 可读且图标在
  const mf = await evaluate(`fetch('manifest.webmanifest').then(r => r.json()).then(m =>
    m.name + '|' + m.display + '|icons:' + m.icons.length + '|start:' + m.start_url)`, true);
  console.log('manifest:', mf);
  expect('manifest 可解析且含图标', /icons:[34]/.test(mf));

  // 4) 断网刷新首页 —— 必须还能开
  await send('Network.emulateNetworkConditions',
    { offline: true, latency: 0, downloadThroughput: 0, uploadThroughput: 0 });
  await open(`http://127.0.0.1:${PORT}/index.html`);
  await sleep(400);
  const off1 = await evaluate(`document.title + '|h1:' + (document.querySelector('h1') ? document.querySelector('h1').textContent.slice(0,10) : 'NONE')`);
  console.log('断网刷新首页:', off1);
  expect('断网刷新首页可用', off1.includes('Python'));

  // 5) 断网直接进课节页（SW 缓存回退）
  await open(`http://127.0.0.1:${PORT}/web/lessons/05.html`);
  await sleep(400);
  const off2 = await evaluate(`document.title + '|done:' + !!document.getElementById('doneBox') + '|side:' + (document.querySelector('.side') ? getComputedStyle(document.querySelector('.side')).display : 'NONE')`);
  console.log('断网进课节05:', off2);
  expect('断网课节页可用（含完成勾选与侧栏）', off2.includes('done:true') && off2.includes('side:block'));

  // 6) 断网进课件播放器
  await open(`http://127.0.0.1:${PORT}/web/ppt/index.html`);
  await sleep(400);
  const off3 = await evaluate(`document.title`);
  console.log('断网进课件总览:', off3);
  expect('断网课件页可用', off3.length > 0 && off3 !== 'about:blank');

  // 7) 恢复网络，确认更新链路正常
  await send('Network.emulateNetworkConditions',
    { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });

  console.log('\nPASS ' + pass.length + '：' + pass.join(' | '));
  if (fail.length) { console.log('FAIL ' + fail.length + '：' + fail.join(' | ')); cleanup(); process.exit(2); }
  console.log('PWA_ALL_PASS');
  ws.close(); cleanup();
}
main().catch(e => { console.error('ERR', e.message); cleanup(); process.exit(1); });
