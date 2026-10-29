/* 补强项实测（CDP，不靠肉眼）——审计链覆盖不到的四项新功能：
 *  1. 周计划页 plan.html：周次连续无缺号、课节链接无死链、两档切换、进度联动
 *  2. 首页 ETA：注入进度后算出完成日期，落后时明确说出落后几周
 *  3. 题库按需加载：首屏不拉 bank-ans.js，点「看答案」才拉且答案真正填进去
 *  4. 打印：@media print 下代码块必须是浅底深字（否则打出来一片黑）
 *
 * 用法：node tools/verify_extras.mjs
 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PYTHON = 'C:/Users/57411/.workbuddy/binaries/python/envs/default/Scripts/python.exe';
const ROOT_DIR = path.resolve(import.meta.dirname, '..');
const PORT = 8093;
const CDP_PORT = 9788;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'extras-verify-'));
const DAY = 86400000;

const server = spawn(PYTHON, ['tools/serve.py', String(PORT)], { cwd: ROOT_DIR, stdio: 'ignore' });
const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${CDP_PORT}`,
  `--user-data-dir=${PROFILE}`, '--no-first-run', '--no-default-browser-check',
  '--window-size=1440,900', 'about:blank',
], { stdio: 'ignore' });
function cleanup() { try { server.kill(); } catch {} try { chrome.kill(); } catch {} }

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
        if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 400));
        return r.result?.result?.value;
      });
  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');
  await send('Emulation.setDeviceMetricsOverride',
    { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });

  async function open(rel) {
    const url = `http://127.0.0.1:${PORT}/${rel}`;
    const loaded = new Promise((res) => {
      const t = setInterval(() => { if (events.includes('Page.loadEventFired')) { clearInterval(t); res(); } }, 40);
      setTimeout(() => { clearInterval(t); res(); }, 15000);
    });
    events.length = 0;
    await send('Page.navigate', { url });
    await loaded;
    await sleep(150);
  }

  const pass = [], fail = [];
  const expect = (name, ok, extra) => { (ok ? pass : fail).push(name + (extra ? ' → ' + extra : '')); };

  /* ───── 1. 周计划页 ───── */
  // 两档各有自己的 tbody，只统计「当前可见」的那一份
  const VIS = `(() => {
    const ts = [document.getElementById('tb1'), document.getElementById('tb2')].filter(t => t && t.offsetParent !== null);
    const rows = ts.length ? [...ts[0].querySelectorAll('tr')] : [];
    return JSON.stringify({
      id: ts.map(t => t.id).join(','),
      n: rows.length,
      ws: rows.map(r => r.dataset.w).join(','),
      dup: rows.length - new Set(rows.map(r => r.dataset.w)).size,
      empty: rows.filter(r => !r.querySelector('.cl a')).map(r => r.dataset.w),
      hrefs: rows.map(r => [...r.querySelectorAll('.cl a')].map(a => a.getAttribute('href'))).flat(),
    });
  })()`;

  await open('web/plan.html');
  const w = JSON.parse(await evaluate(VIS));
  const wantWs = Array.from({ length: 30 }, (_, i) => i).join(',');
  expect('周计划 周次连续 0–29 无缺号', w.ws === wantWs && w.dup === 0,
    `${w.id} ${w.n} 行 / 重复 ${w.dup}`);
  expect('周计划 无空周（每周都有课节链接）', w.empty.length === 0, '空周 ' + JSON.stringify(w.empty));

  // 链接可达：逐个 HEAD（同源，相对 web/ 目录）
  const hrefList = [...new Set(w.hrefs)];
  const badHref = [];
  for (const h of hrefList) {
    const r = await fetch(`http://127.0.0.1:${PORT}/web/${h}`).catch(() => null);
    if (!r || !r.ok) badHref.push(h + (r ? ':' + r.status : ':ERR'));
  }
  expect('周计划 课节链接全部可达', badHref.length === 0,
    `${hrefList.length} 个链接，坏 ${badHref.length} ${badHref.slice(0, 3).join(' ')}`);

  // 两档切换：不只是换一句说明，周表本身要换成对应周数的那一份
  const pace = JSON.parse(await evaluate(`(() => {
    const btns = [...document.querySelectorAll('.pb')];
    const std = JSON.parse(${VIS});
    btns.find(b => b.dataset.pace === '2').click();
    const light = JSON.parse(${VIS});
    const note = (document.getElementById('paceNote') || {}).textContent || '';
    // 必须当场取成字符串：style 是活引用，切回标准档后又变回 none 了
    const sts2Shown = document.getElementById('sts2').style.display;
    const sts1Shown = document.getElementById('sts1').style.display;
    btns.find(b => b.dataset.pace === '1').click();
    const back = JSON.parse(${VIS});
    return JSON.stringify({ std, light, back, note: note.slice(0, 30), sts2Shown, sts1Shown });
  })()`));
  const p = pace;
  expect('周计划 两档切换换表（30 ↔ 60 周）',
    p.std.n === 30 && p.light.n === 60 && p.back.n === 30 &&
    p.std.id === 'tb1' && p.light.id === 'tb2' && p.back.id === 'tb1',
    `标准 ${p.std.id} ${p.std.n} 行 → 轻量 ${p.light.id} ${p.light.n} 行 → 回 ${p.back.id} ${p.back.n} 行`);
  expect('周计划 轻量档阶段卡同步（周次按档位换算）',
    p.sts2Shown !== 'none' && p.sts1Shown === 'none',
    `轻量档 sts1=${p.sts1Shown || '显示'} sts2=${p.sts2Shown || '显示'} · ${p.note}`);

  // 进度联动：标记若干课节后，「你的位置」应出现补节建议
  await evaluate(`(() => {
    const d = {}; for (let i = 1; i <= 20; i++) d[i] = Date.now() - i * ${DAY};
    localStorage.setItem('lesson-done-v1', JSON.stringify(d));
  })()`);
  await open('web/plan.html');
  const you = await evaluate(`(document.getElementById('youBody')||{}).textContent || ''`);
  expect('周计划 进度联动（显示你的位置）', you.trim().length > 0 && !/统计中/.test(you),
    you.replace(/\s+/g, ' ').slice(0, 90));
  await evaluate(`localStorage.removeItem('lesson-done-v1')`);

  /* ───── 2. 首页 ETA 与偏差 ───── */
  // 落后场景：开课 20 天只学 5 节，且最近两周有记录（有速度才算得出 ETA）
  await open('index.html');
  await evaluate(`(() => {
    const d = {}, t0 = Date.now();
    for (let i = 0; i < 5; i++) d[i + 1] = t0 - (20 - i * 4) * ${DAY};  // 20/16/12/8/4 天前
    localStorage.setItem('lesson-done-v1', JSON.stringify(d));
  })()`);
  await open('index.html');
  const late = await evaluate(`(() => {
    const el = document.getElementById('stk') || document.querySelector('.pace, #pace, #stk');
    const t = document.body.innerText;
    const m = t.match(/落后约[^，。\\n]*/);
    const e = t.match(/按近期速度约[^（\\n]*/);
    return JSON.stringify({ late: m ? m[0].slice(0, 40) : '', eta: e ? e[0].slice(0, 40) : '' });
  })()`);
  const l = JSON.parse(late);
  expect('首页 ETA 给出剩余天数/完成日期', /按近期速度约/.test(l.eta), l.eta || '未出现');
  expect('首页 落后时明确报落后几周', /落后约/.test(l.late), l.late || '未出现');

  // 超前场景
  await evaluate(`(() => {
    const d = {}, t0 = Date.now();
    for (let i = 0; i < 60; i++) d[i + 1] = t0 - (i % 10) * ${DAY};
    localStorage.setItem('lesson-done-v1', JSON.stringify(d));
  })()`);
  await open('index.html');
  const ahead = await evaluate(`(() => {
    const t = document.body.innerText; const m = t.match(/比 \\d+ 周配速快约 \\d+ 周/);
    return m ? m[0] : '';
  })()`);
  expect('首页 超前时报配速领先', /配速快约/.test(ahead), ahead || '未出现');

  // 全学完
  await evaluate(`(() => {
    const d = {}, t0 = Date.now();
    for (let i = 1; i <= 111; i++) d[i] = t0 - (i % 30) * ${DAY};
    localStorage.setItem('lesson-done-v1', JSON.stringify(d));
  })()`);
  await open('index.html');
  const done = await evaluate(`(() => { const m = document.body.innerText.match(/全部 \\d+ 节学完/); return m ? m[0] : ''; })()`);
  expect('首页 全部学完有收尾提示', /全部 111 节学完/.test(done), done || '未出现');
  await evaluate(`localStorage.removeItem('lesson-done-v1')`);

  /* ───── 3. 题库按需加载 ───── */
  const sizeBank = fs.statSync(path.join(ROOT_DIR, 'web/bank.html')).size;
  const sizeAns = fs.statSync(path.join(ROOT_DIR, 'web/bank-ans.js')).size;
  const reqs = [];
  const onReq = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.method === 'Network.requestWillBeSent') reqs.push(m.params.request.url);
  };
  ws.addEventListener('message', onReq);
  await open('web/bank.html');
  await sleep(600);
  const beforeOpen = reqs.filter(u => /bank-ans\.js/.test(u)).length;
  expect('题库 首屏不加载答案文件', beforeOpen === 0,
    `bank.html ${(sizeBank / 1024).toFixed(0)} KB，答案 ${(sizeAns / 1024).toFixed(0)} KB，首屏请求 ${beforeOpen} 次`);

  // 必须模拟真实点击：加载器挂在 document 的 click 上，程序化 open = true 不会触发
  const box = JSON.parse(await evaluate(`(() => {
    const d = document.querySelector('details.ans');
    if (!d) return '{"err":"no-details"}';
    d.scrollIntoView({ block: 'center' });
    const s = d.querySelector('summary');
    const r = s.getBoundingClientRect();
    return JSON.stringify({ x: r.x + r.width / 2, y: r.y + r.height / 2 });
  })()`));
  await sleep(200);
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent',
      { type, x: box.x, y: box.y, button: 'left', clickCount: 1 });
  }
  await sleep(1200);
  const afterOpen = reqs.filter(u => /bank-ans\.js/.test(u)).length;
  const filled = await evaluate(`(() => {
    const ac = document.querySelector('details.ans .ac');
    if (!ac) return 'none';
    return JSON.stringify({ loading: !!ac.querySelector('.ld'), len: ac.textContent.trim().length,
      head: ac.textContent.trim().slice(0, 30) });
  })()`);
  const f = JSON.parse(filled);
  expect('题库 点开答案才拉取答案文件', afterOpen >= 1, `点击后请求 ${afterOpen} 次`);
  expect('题库 答案真正填进卡片', f.len > 20 && !f.loading,
    `${f.len} 字「${f.head}…」`);
  ws.removeEventListener('message', onReq);

  /* ───── 3b. file:// 下答案照样能加载（便携版就是这么开的）─────
     加载器刻意不用 fetch：file:// 下 fetch 会被当跨域拦掉。这里用真实协议验一遍。 */
  const fileUrl = 'file:///' + path.join(ROOT_DIR, 'web/bank.html').replace(/\\/g, '/');
  await send('Page.navigate', { url: fileUrl });
  await sleep(1200);
  const fbox = JSON.parse(await evaluate(`(() => {
    const d = document.querySelector('details.ans');
    if (!d) return '{"err":"no-details"}';
    d.scrollIntoView({ block: 'center' });
    const s = d.querySelector('summary'), r = s.getBoundingClientRect();
    return JSON.stringify({ x: r.x + r.width / 2, y: r.y + r.height / 2, proto: location.protocol });
  })()`));
  for (const type of ['mousePressed', 'mouseReleased']) {
    await send('Input.dispatchMouseEvent',
      { type, x: fbox.x, y: fbox.y, button: 'left', clickCount: 1 });
  }
  await sleep(1500);
  const fileFilled = JSON.parse(await evaluate(`(() => {
    const ac = document.querySelector('details.ans .ac');
    return JSON.stringify({ proto: location.protocol, len: ac ? ac.textContent.trim().length : -1,
      loading: ac ? !!ac.querySelector('.ld') : true,
      scripts: !!document.querySelector('script[src="bank-ans.js"]') });
  })()`));
  expect('题库 file:// 协议下答案可加载（便携版场景）',
    fileFilled.proto === 'file:' && fileFilled.len > 20 && !fileFilled.loading,
    `${fileFilled.proto} 填充 ${fileFilled.len} 字，script 注入 ${fileFilled.scripts}`);

  /* ───── 4. 打印时代码块浅底 ───── */
  const PRINT_PAGES = ['web/lessons/01.html', 'web/lessons/45.html', 'fluent/web/lessons/l01.html'];
  for (const rel of PRINT_PAGES) {
    await open(rel);
    await send('Emulation.setEmulatedMedia', { media: 'print' });
    await sleep(120);
    const r = JSON.parse(await evaluate(`(() => {
      const lum = (c) => { const a = c.map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
        return 0.2126*a[0] + 0.7152*a[1] + 0.0722*a[2]; };
      const parse = (s) => { const m = s.match(/rgba?\\(([^)]+)\\)/); if (!m) return null;
        const p = m[1].split(/[,/\\s]+/).filter(Boolean).map(Number); return p.slice(0,3); };
      const pres = [...document.querySelectorAll('.main pre, pre')].slice(0, 8);
      const out = [];
      for (const el of pres) {
        const cs = getComputedStyle(el);
        const bg = parse(cs.backgroundColor), fg = parse(cs.color);
        if (!bg || !fg) { out.push('unparsed'); continue; }
        out.push({ bgL: +lum(bg).toFixed(2), fgL: +lum(fg).toFixed(2), bg: cs.backgroundColor, fg: cs.color });
      }
      return JSON.stringify({ n: pres.length, out });
    })()`));
    const darkBg = r.out.filter(o => o !== 'unparsed' && o.bgL < 0.5);
    const darkFg = r.out.filter(o => o !== 'unparsed' && o.bgL >= 0.5 && o.fgL > 0.5);
    expect(`打印 ${rel} 代码块浅底深字`, r.n > 0 && darkBg.length === 0 && darkFg.length === 0,
      `${r.n} 块，深底 ${darkBg.length}，浅字 ${darkFg.length} ${darkBg[0] ? JSON.stringify(darkBg[0]) : ''}`);
    await send('Emulation.setEmulatedMedia', { media: 'screen' });
  }

  console.log('PASS ' + pass.length);
  for (const s of pass) console.log('  ✓ ' + s);
  if (fail.length) { console.log('\nFAIL ' + fail.length); for (const s of fail) console.log('  ✗ ' + s); }
  console.log(fail.length ? '\nEXTRAS_FAIL' : '\nEXTRAS_ALL_PASS');
  cleanup();
  process.exit(fail.length ? 1 : 0);
}
main().catch(e => { console.error(e); cleanup(); process.exit(1); });
