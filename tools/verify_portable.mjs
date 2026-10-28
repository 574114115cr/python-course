/* 便携包 file:// 实测：解压 zip → CDP 加载 → 渲染/图片/进度/窄屏四项检查。
   便携版不走服务器，所以这是交付前的硬验证（不能只看打包成功）。

   运行：node tools/verify_portable.mjs [zip 路径]
 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const ROOT_DIR = path.resolve(import.meta.dirname, '..');
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const ZIP = process.argv[2] || path.join(ROOT_DIR, 'dist', 'Python课程包-便携版.zip');
const PORT = 9787;

// 解压到临时目录（去掉 zip 内的顶层文件夹层级由下面定位）
// 不用 os.tmpdir()：本机 TEMP 被指到 workbuddy-update 目录，且 powershell 不在
// node 的 PATH 里（spawn ENOENT），两项都会让校验直接崩。改用工作区内的唯一目录 +
// python zipfile 解压（venv 解释器一定有）。目录名带时间戳，不必先删旧目录
// （递归删除在沙箱里可能被 safe-delete 拦下）。
const PY = 'C:/Users/57411/.workbuddy/binaries/python/envs/default/Scripts/python.exe';
const TMP = path.join(ROOT_DIR, '.cache', `portable-verify-${Date.now()}`);
fs.mkdirSync(TMP, { recursive: true });

function unzip() {
  return new Promise((res, rej) => {
    const code = 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])';
    const p = spawn(PY, ['-c', code, ZIP, TMP], { stdio: 'ignore' });
    p.on('error', rej);
    p.on('exit', (c) => (c === 0 ? res() : rej(new Error('unzip exit ' + c))));
  });
}

function findDir(name) {
  for (const e of fs.readdirSync(TMP)) {
    const p = path.join(TMP, e);
    if (fs.statSync(p).isDirectory() && e.includes(name)) return p;
  }
  return TMP;
}

const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`,
  '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
function cleanup() { try { proc.kill(); } catch {} }

async function main() {
  await unzip();
  const base = findDir('Python课程包-便携版');
  const url = (rel) => 'file:///' + path.join(base, rel).replace(/\\/g, '/');
  console.log('解压目录:', base);

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
    else if (m.method === 'Page.loadEventFired') events.push(m.method);
  };
  const send = (method, params = {}) => new Promise((res) => {
    const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params }));
  });
  const evaluate = (expr) => send('Runtime.evaluate', { expression: expr, returnByValue: true })
    .then(r => r.result?.result?.value);
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride',
    { width: 390, height: 844, deviceScaleFactor: 1, mobile: false });

  async function open(u) {
    const loaded = new Promise((res) => {
      const t = setInterval(() => { if (events.length) { clearInterval(t); res(); } }, 50);
      setTimeout(() => { clearInterval(t); res(); }, 10000);
    });
    events.length = 0;
    await send('Page.navigate', { url: u });
    await loaded;
    await sleep(600);
  }

  const pass = [], fail = [];
  const expect = (n, ok) => (ok ? pass : fail).push(n);

  // 1) 首页渲染 + CSS 生效 + PWA 文件在位
  await open(url('index.html'));
  const home = await evaluate(`(() => {
    const nav = document.querySelector('.nav');
    return JSON.stringify({
      title: document.title,
      navBg: nav ? getComputedStyle(nav).backgroundColor : 'NONE',
      manifest: !!document.querySelector('link[rel=manifest]'),
      swReg: 'serviceWorker' in navigator,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
    });
  })()`);
  const h = JSON.parse(home);
  console.log('首页:', home);
  expect('首页标题正确', h.title.includes('Python'));
  expect('CSS 生效（导航有背景色）', h.navBg && h.navBg !== 'NONE' && h.navBg !== 'rgba(0, 0, 0, 0)');
  expect('首页无横向溢出', h.overflow <= 0);

  // 2) 课节页 + 课件 webp 图片加载 + 侧栏
  //    注意：侧栏图是 loading="lazy"，窄屏下侧栏在正文下方，必须先滚到可见才加载
  await open(url('web/lessons/05.html'));
  await evaluate(`(() => {
    const img = document.querySelector('.side .pptbox img');
    if (img) img.scrollIntoView();
  })()`);
  await sleep(800);
  const lesson = await evaluate(`(() => {
    const img = document.querySelector('.side .pptbox img');
    return JSON.stringify({
      title: document.title,
      imgOk: img ? img.naturalWidth > 0 : 'no-img',
      side: document.querySelector('.side') ? getComputedStyle(document.querySelector('.side')).display : 'NONE',
      doneBox: !!document.getElementById('doneBox'),
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
    });
  })()`);
  const l = JSON.parse(lesson);
  console.log('课节05:', lesson);
  expect('课节页标题正确', l.title.includes('第 5 节'));
  expect('课件 webp 加载成功', l.imgOk === true);
  expect('侧栏可见', l.side === 'block');
  expect('课节页无横向溢出', l.overflow <= 0);

  // 3) 课件播放器图片
  await open(url('web/ppt/u/01.html'));
  const player = await evaluate(`(() => {
    const img = document.querySelector('img');
    return JSON.stringify({
      title: document.title.slice(0, 20),
      imgOk: img ? img.naturalWidth > 0 : 'no-img'
    });
  })()`);
  const p = JSON.parse(player);
  console.log('播放器:', player);
  expect('播放器标题正确', p.title.includes('课件'));
  expect('播放器幻灯片加载', p.imgOk === true);

  // 4) localStorage 进度存取（file:// 下必须可用）
  await open(url('web/lessons/index.html'));
  const ls = await evaluate(`(() => {
    try {
      localStorage.setItem('lesson-done-v1', JSON.stringify({ 5: true }));
      const v = JSON.parse(localStorage.getItem('lesson-done-v1') || '{}');
      return JSON.stringify({ ok: v['5'] === true });
    } catch (e) { return JSON.stringify({ ok: false, err: e.message }); }
  })()`);
  console.log('localStorage:', ls);
  expect('localStorage 进度存取正常', JSON.parse(ls).ok === true);

  console.log('\nPASS ' + pass.length + ' 项；FAIL ' + fail.length + ' 项');
  fail.forEach(f => console.log('  ✗', f));
  ws.close(); cleanup();
  fs.rmSync(TMP, { recursive: true, force: true });
  if (fail.length) process.exit(2);
  console.log('PORTABLE_ALL_PASS');
}
main().catch(e => { console.error('ERR', e.message); cleanup(); process.exit(1); });
