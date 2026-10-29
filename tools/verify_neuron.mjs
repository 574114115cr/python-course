/* 神经元背景实测（CDP，不靠肉眼）。
 *
 * 查九件事：
 *  1. 各类页面都注入了 canvas + 按钮，且 canvas 真的在画（有非透明像素）；
 *  2. 开关：关掉 → canvas 隐藏 + 持久化 + 刷新后仍关；
 *  3. 密度三档：低 < 中 < 高 的节点数；
 *  4. 鼠标跟随：开 → 鼠标处出现圆盘；关 → 同位置消失；
 *  5. 动效/密度选项的选中态与持久化；
 *  6. 面板：按钮开合、Esc 关闭、点外部关闭；
 *  7. 打印时 canvas/按钮/面板全部隐藏；
 *  8. 390px 窄屏：按钮不溢出、不与主题悬浮按钮重叠；
 *  9. file:// 协议下照常工作（便携版场景）。
 *
 * 用法：node tools/verify_neuron.mjs
 */
import { spawn } from 'node:child_process';
import { setTimeout as sleep } from 'node:timers/promises';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PYTHON = 'C:/Users/57411/.workbuddy/binaries/python/envs/default/Scripts/python.exe';
const ROOT_DIR = path.resolve(import.meta.dirname, '..');
const PORT = 8094;
const CDP_PORT = 9789;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'neuron-verify-'));

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
  await send('Emulation.setDeviceMetricsOverride',
    { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });

  async function open(rel) {
    const url = rel.startsWith('file:')
      ? rel : `http://127.0.0.1:${PORT}/${rel}`;
    const loaded = new Promise((res) => {
      const t = setInterval(() => { if (events.includes('Page.loadEventFired')) { clearInterval(t); res(); } }, 40);
      setTimeout(() => { clearInterval(t); res(); }, 15000);
    });
    events.length = 0;
    await send('Page.navigate', { url });
    await loaded;
    await sleep(500);
  }
  const mouse = async (x, y) => {
    for (const type of ['mouseMoved']) {
      await send('Input.dispatchMouseEvent', { type, x, y, button: 'none' });
    }
  };

  const pass = [], fail = [];
  const expect = (name, ok, extra) => { (ok ? pass : fail).push(name + (extra ? ' → ' + extra : '')); };

  /* ───── 1. 各类页面都注入且真的在画 ───── */
  const PAGES = ['index.html', 'web/lessons/45.html', 'web/bank.html', 'web/plan.html',
    'fluent/web/01.html', 'web/ppt/u/01.html'];
  for (const rel of PAGES) {
    await open(rel);
    const r = JSON.parse(await evaluate(`(() => {
      const c = document.getElementById('neuronCv'), b = document.getElementById('nrBtn');
      if (!c || !b) return JSON.stringify({ miss: !c ? 'canvas' : 'button' });
      const x = c.getContext('2d');
      const d = x.getImageData(0, 0, c.width, c.height).data;
      let n = 0;
      for (let i = 3; i < d.length; i += 4) if (d[i] > 8) n++;
      return JSON.stringify({ painted: n, pe: getComputedStyle(c).pointerEvents,
        nodes: window.__neuron ? window.__neuron.count() : -1 });
    })()`));
    expect(`${rel} 注入完整`, !r.miss && r.pe === 'none' && r.nodes > 0,
      r.miss || `${r.nodes} 节点 / 绘制 ${r.painted} px / pointer-events:${r.pe}`);
    expect(`${rel} 动画在跑`, r.painted > 200, `${r.painted} px`);
  }

  /* ───── 2. 开关 + 持久化 ───── */
  await open('index.html');
  await evaluate(`window.__neuron.set('on',0)`);
  const offState = JSON.parse(await evaluate(`(() => {
    const c = document.getElementById('neuronCv');
    return JSON.stringify({ disp: getComputedStyle(c).display,
      saved: localStorage.getItem('py-neuron-v1') });
  })()`));
  await open('index.html');
  const offAfter = await evaluate(`getComputedStyle(document.getElementById('neuronCv')).display`);
  expect('开关 关掉后 canvas 隐藏并落盘', offState.disp === 'none' && /"on":0/.test(offState.saved),
    offState.saved);
  expect('开关 刷新后仍是关', offAfter === 'none', offAfter);
  await evaluate(`window.__neuron.set('on',1)`);
  await sleep(300);
  const onBack = await evaluate(`(() => {
    const c = document.getElementById('neuronCv');
    const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
    let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 8) n++;
    return n;
  })()`);
  expect('开关 重新打开恢复绘制', onBack > 200, `${onBack} px`);

  /* ───── 3. 密度四档（多视口）───── */
  // 只在单一尺寸验过会漏事：节点数 = 面积/17000×密度，大屏基数大，
  // 撞上性能上限后高档与极档会被压平，档位看着有、实际没差别。
  const viewport = (w, h, mob = false) =>
    send('Emulation.setDeviceMetricsOverride',
      { width: w, height: h, deviceScaleFactor: 1, mobile: mob });

  const VIEWS = [
    { name: '1920×1080', w: 1920, h: 1080, mob: false, inc: true },
    { name: '1440×900', w: 1440, h: 900, mob: false, inc: true },
    { name: '390×844', w: 390, h: 844, mob: true, inc: true },
    // 超大屏允许撞上限，但至少不能出现极档反而比高档少
    { name: '2560×1440', w: 2560, h: 1440, mob: false, inc: false },
  ];
  const counts = {};
  for (const v of VIEWS) {
    await viewport(v.w, v.h, v.mob);
    await open('index.html');
    const c = {};
    for (const d of ['low', 'mid', 'high', 'ultra']) {
      await evaluate(`window.__neuron.set('dense','${d}')`);
      await sleep(200);
      c[d] = await evaluate(`window.__neuron.count()`);
    }
    counts[v.name] = c;
    if (v.inc) {
      expect(`密度 ${v.name} 低<中<高<极`,
        c.low < c.mid && c.mid < c.high && c.high < c.ultra,
        `${c.low} / ${c.mid} / ${c.high} / ${c.ultra}`);
      expect(`密度 ${v.name} 高档→极档增幅 ≥30%`,
        c.ultra / c.high - 1 >= 0.3,
        `+${((c.ultra / c.high - 1) * 100).toFixed(0)}%`);
    } else {
      expect(`密度 ${v.name} 极档不倒挂`, c.ultra >= c.high, `${c.high} / ${c.ultra}`);
    }
  }
  await viewport(1440, 900, false);
  await evaluate(`window.__neuron.set('dense','mid')`);

  /* ───── 3b. 动效四档（速度真的递增） ───── */
  // 采样同一节点两帧之间的位移：只比对档位名没意义，要验速度值真的分档
  const spd = {};
  for (const s of ['slow', 'mid', 'fast', 'rush']) {
    await evaluate(`window.__neuron.set('speed','${s}')`);
    await sleep(200);
    // 固定墙钟间隔内量节点平均位移，比对比档位名有意义
    spd[s] = Number(await evaluate(`(() => {
      const p0 = window.__neuron.pos().split(';');
      return new Promise(res => setTimeout(() => {
        const p1 = window.__neuron.pos().split(';');
        let sum = 0, n = 0;
        for (let i = 0; i < Math.min(p0.length, p1.length); i++) {
          const a = p0[i].split(','), b = p1[i].split(',');
          const dx = +b[0] - +a[0], dy = +b[1] - +a[1];
          if (Math.abs(dx) > 100 || Math.abs(dy) > 100) continue;   // 跳过环绕跳变
          sum += Math.sqrt(dx * dx + dy * dy); n++;
        }
        res(n ? (sum / n).toFixed(3) : '0');
      }, 400));
    })()`, true));
  }
  expect('动效 静 < 缓 < 快 < 疾（位移递增）',
    spd.slow < spd.mid && spd.mid < spd.fast && spd.fast < spd.rush,
    `${spd.slow} / ${spd.mid} / ${spd.fast} / ${spd.rush} px`);
  await evaluate(`window.__neuron.set('speed','mid')`);

  /* ───── 4. 鼠标跟随 ───── */
  await evaluate(`window.__neuron.set('speed','slow')`);
  await mouse(700, 400);
  await sleep(400);
  const disk = (await evaluate(`(() => {
    const c = document.getElementById('neuronCv');
    const x = c.getContext('2d');
    const d = x.getImageData(695, 395, 10, 10).data;
    let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 30) n++;
    return n;
  })()`));
  await evaluate(`window.__neuron.set('follow',0)`);
  await mouse(700, 400);
  await sleep(400);
  const noDisk = (await evaluate(`(() => {
    const c = document.getElementById('neuronCv');
    const d = c.getContext('2d').getImageData(695, 395, 10, 10).data;
    let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 30) n++;
    return n;
  })()`));
  expect('鼠标跟随 开 → 鼠标处出现圆盘', disk >= 12, `${disk} px`);
  expect('鼠标跟随 关 → 同位置圆盘消失', noDisk < disk, `${noDisk} px（开时 ${disk}）`);
  await evaluate(`window.__neuron.set('follow',1)`);

  /* ───── 4b. 配色 多彩/单色 + 绘制性能 ───── */
  // 色相按 30° 分桶，只统计 alpha≥40 的明显像素（光晕 alpha≈0.1，不会混进来）
  const HUES = `(() => {
    const c = document.getElementById('neuronCv');
    const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
    const hues = {};
    for (let i = 0; i < d.length; i += 4) {
      if (d[i + 3] < 40) continue;
      const r = d[i] / 255, g = d[i + 1] / 255, b = d[i + 2] / 255;
      const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
      if (mx - mn < 0.06) continue;           // 近灰白（单色蓝也会被排除，改在下面兜底）
      let h;
      if (mx === r) h = ((g - b) / (mx - mn)) % 6;
      else if (mx === g) h = (b - r) / (mx - mn) + 2;
      else h = (r - g) / (mx - mn) + 4;
      h = Math.round(((h * 60) + 360) % 360 / 30);
      hues[h] = (hues[h] || 0) + 1;
    }
    return Object.keys(hues).length;
  })()`;
  const fps = `(() => new Promise(res => {
    let n = 0; const t0 = performance.now();
    (function loop() {
      n++;
      if (performance.now() - t0 < 1000) requestAnimationFrame(loop);
      else res(n);
    })();
  }))()`;
  // 拿最坏情况测：最高档 221 个节点 + 每条线一次渐变
  await evaluate(`window.__neuron.set('dense','ultra')`);
  await evaluate(`window.__theme.set('light')`);
  await evaluate(`window.__neuron.set('color','multi')`);
  await sleep(700);
  const huL = Number(await evaluate(HUES));
  const fpsMulti = Number(await evaluate(fps, true));
  await evaluate(`window.__neuron.set('color','mono')`);
  await sleep(700);
  const huM = Number(await evaluate(HUES));
  const fpsMono = Number(await evaluate(fps, true));
  expect('配色 浅色多彩色相 ≥4 种', huL >= 4, `${huL} 个色相桶`);
  expect('配色 单色色相远少于多彩', huM <= 3 && huM < huL, `${huM} 个色相桶`);
  expect('性能 多彩渐变不掉帧（≥40fps）', fpsMulti >= 40, `${fpsMulti} fps`);
  expect('性能 多彩不比单色慢太多（≥60%）', fpsMulti >= fpsMono * 0.6,
    `多彩 ${fpsMulti} / 单色 ${fpsMono}`);
  await evaluate(`window.__theme.set('dark')`);
  await evaluate(`window.__neuron.set('color','multi')`);
  await sleep(700);
  const huD = Number(await evaluate(HUES));
  expect('配色 深色多彩色相 ≥4 种', huD >= 4, `${huD} 个色相桶`);
  await evaluate(`window.__theme.set('light')`);
  await evaluate(`window.__neuron.set('dense','mid')`);

  /* ───── 5. 选项选中态 + 持久化 ───── */
  await evaluate(`window.__neuron.set('speed','fast')`);
  await evaluate(`window.__neuron.set('dense','high')`);
  const sel = JSON.parse(await evaluate(`(() => {
    const sel = [...document.querySelectorAll('#nrPanel button.sel')].map(b => b.getAttribute('data-v'));
    const sw = [...document.querySelectorAll('#nrPanel .sw')].map(b =>
      b.getAttribute('data-k') + ':' + b.textContent);
    return JSON.stringify({ sel, sw, saved: localStorage.getItem('py-neuron-v1') });
  })()`));
  expect('选项选中态与面板同步', sel.sel.includes('fast') && sel.sel.includes('high') &&
    sel.sw.includes('on:开'), sel.sel.join(',') + ' | ' + sel.sw.join(' '));
  expect('选项落盘', /"dense":"high"/.test(sel.saved) && /"speed":"fast"/.test(sel.saved),
    sel.saved);
  await evaluate(`window.__neuron.set('speed','mid')`);
  await evaluate(`window.__neuron.set('dense','mid')`);

  /* ───── 6. 面板交互 ───── */
  await evaluate(`document.getElementById('nrPanel').classList.add('open')`);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: 60, y: 60, button: 'left', clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: 60, y: 60, button: 'left', clickCount: 1 });
  await sleep(150);
  const outClosed = await evaluate(`!document.getElementById('nrPanel').classList.contains('open')`);
  expect('面板 点外部关闭', outClosed);
  await evaluate(`document.getElementById('nrBtn').click()`);
  await sleep(120);
  const opened = await evaluate(`document.getElementById('nrPanel').classList.contains('open')`);
  await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
  await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
  await sleep(120);
  const escClosed = await evaluate(`!document.getElementById('nrPanel').classList.contains('open')`);
  expect('面板 按钮打开 / Esc 关闭', opened && escClosed, `open=${opened} escClosed=${escClosed}`);

  /* ───── 7. 打印时全部隐藏 ───── */
  await open('web/lessons/45.html');
  await send('Emulation.setEmulatedMedia', { media: 'print' });
  await sleep(150);
  const pr = JSON.parse(await evaluate(`(() => {
    const g = id => getComputedStyle(document.getElementById(id)).display;
    return JSON.stringify({ cv: g('neuronCv'), btn: g('nrBtn'), panel: g('nrPanel') });
  })()`));
  expect('打印时 canvas/按钮/面板全隐藏', pr.cv === 'none' && pr.btn === 'none' && pr.panel === 'none',
    JSON.stringify(pr));
  await send('Emulation.setEmulatedMedia', { media: 'screen' });

  /* ───── 8. 390px 窄屏 ───── */
  await send('Emulation.setDeviceMetricsOverride',
    { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await open('web/lessons/45.html');
  const mob = JSON.parse(await evaluate(`(() => {
    const box = id => { const el = document.getElementById(id); if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: r.x, y: r.y, w: r.width, h: r.height, right: r.right, bottom: r.bottom }; };
    const nr = box('nrBtn'), th = box('thBtn'), bg = box('bgmBtn');
    const overlap = (a, b) => a && b && !(a.right < b.x || b.right < a.x || a.bottom < b.y || b.bottom < a.y);
    return JSON.stringify({ nr, th, bg, docW: document.documentElement.scrollWidth,
      innerW: window.innerWidth, ovTh: overlap(nr, th), ovBg: overlap(nr, bg) });
  })()`));
  expect('390px 按钮在屏内不溢出', mob.nr && mob.nr.right <= mob.innerW + 1 && mob.nr.x >= 0,
    `right=${mob.nr.right}/${mob.innerW}`);
  expect('390px 与主题/音乐按钮不重叠', !mob.ovTh && !mob.ovBg,
    `th=${JSON.stringify(mob.th)} bg=${JSON.stringify(mob.bg)}`);
  // 档位变多后按钮组不能被挤出面板：任何 seg 的右边缘都不能越过 panel 内容区
  await evaluate(`document.getElementById('nrPanel').classList.add('open')`);
  await sleep(120);
  const segFit = JSON.parse(await evaluate(`(() => {
    const p = document.getElementById('nrPanel').getBoundingClientRect();
    const cs = getComputedStyle(document.getElementById('nrPanel'));
    const padR = parseFloat(cs.paddingRight) || 0;
    let worst = 0, who = '';
    for (const s of document.querySelectorAll('#nrPanel .seg')) {
      const r = s.getBoundingClientRect();
      const over = r.right - (p.right - padR);
      if (over > worst) { worst = over; who = s.getAttribute('data-k'); }
    }
    return JSON.stringify({ worst: +worst.toFixed(1), who,
      rows: document.querySelectorAll('#nrPanel .row').length });
  })()`));
  expect('面板 按钮组不溢出（四档挤得下）', segFit.worst <= 0.5,
    `最大越界 ${segFit.worst}px（${segFit.who || '无'}）`);
  expect('面板 五行选项齐全', segFit.rows === 5, `${segFit.rows} 行`);
  await evaluate(`document.getElementById('nrPanel').classList.remove('open')`);
  await send('Emulation.setDeviceMetricsOverride',
    { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });

  /* ───── 9. file:// 协议（便携版）───── */
  const fileUrl = 'file:///' + path.join(ROOT_DIR, 'web', 'lessons', '45.html').replace(/\\/g, '/');
  await open(fileUrl);
  await sleep(700);
  const fileState = JSON.parse(await evaluate(`(() => {
    const c = document.getElementById('neuronCv');
    if (!c) return JSON.stringify({ miss: 1, proto: location.protocol });
    const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
    let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 8) n++;
    return JSON.stringify({ proto: location.protocol, painted: n, nodes: window.__neuron.count() });
  })()`));
  expect('file:// 下照常工作', fileState.proto === 'file:' && fileState.painted > 200,
    `${fileState.proto} ${fileState.painted} px / ${fileState.nodes} 节点`);

  /* 清理测试数据，别把开关状态留给用户 */
  await open('index.html');
  await evaluate(`localStorage.removeItem('py-neuron-v1')`);

  console.log('PASS ' + pass.length);
  for (const s of pass) console.log('  ✓ ' + s);
  if (fail.length) { console.log('\nFAIL ' + fail.length); for (const s of fail) console.log('  ✗ ' + s); }
  console.log(fail.length ? '\nNEURON_FAIL' : '\nNEURON_ALL_PASS');
  cleanup();
  process.exit(fail.length ? 1 : 0);
}
main().catch(e => { console.error(e); cleanup(); process.exit(1); });
