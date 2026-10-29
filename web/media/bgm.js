/* 全站背景音乐：8-bit 循环曲 + 每页开关 + 跨页续播。
 *
 * 为什么这样做：
 * 站点是纯静态页面，每次点链接都是整页刷新，音频元素会跟着销毁，
 * 静态站无法让「同一个 audio 元素」跨页存活（除非开弹窗或改 SPA）。
 * 这里用「记住播放位置 + 换页后 seek 回去」实现进度连续：
 *   - 播放位置每 1 秒写一次 localStorage（含时间戳）
 *   - 新页面加载后把「离开的这段耗时」补上，再对循环长度取模
 *   => 听感上是接着放的，页面上会看到极短的加载间隙。
 *
 * 开关状态存 bgm-on-v1；浏览器禁止自动播放有声内容，首次进入需一次点击/按键才响。
 */
(function () {
  if (window.__bgmLoaded) return;
  window.__bgmLoaded = true;

  var ON_KEY = 'bgm-on-v1';
  var POS_KEY = 'bgm-pos-v1';
  var LOOP_LEN = 16.0;          // 与 make_bgm.py 输出一致，仅作取模兜底

  // 用脚本自身地址定位音频，任意层级页面都能找到（file:// 与 http 都适用）
  var me = document.currentScript ||
           document.querySelector('script[src*="bgm.js"]');
  var base = (me && me.src) ? me.src.replace(/[^\/]*$/, '') : '';

  var on = true;
  try { on = localStorage.getItem(ON_KEY) !== '0'; } catch (e) {}

  var audio = new Audio(base + 'bgm-8bit.wav');
  audio.loop = true;
  audio.preload = 'auto';
  audio.volume = 0.34;

  window.__bgm = { audio: audio, on: on };   // 便于自检

  var lastSave = 0;
  function savePos(force) {
    var now = Date.now();
    if (!force && now - lastSave < 900) return;
    lastSave = now;
    try {
      localStorage.setItem(POS_KEY, JSON.stringify({
        t: audio.currentTime || 0, at: now
      }));
    } catch (e) {}
  }

  function restorePos() {
    var o = null;
    try { o = JSON.parse(localStorage.getItem(POS_KEY) || 'null'); } catch (e) {}
    if (!o || typeof o.t !== 'number') return;
    var t = o.t;
    var gap = (Date.now() - (o.at || 0)) / 1000;
    // 换页的这几百毫秒也算进去，听感才连贯；离开太久就从头放
    if (gap > 0 && gap < 8) t += gap;
    var dur = audio.duration && isFinite(audio.duration) ? audio.duration : LOOP_LEN;
    if (dur > 0) t = t % dur;
    try { audio.currentTime = t; } catch (e) {}
  }

  function tryPlay() {
    var p = audio.play();
    if (p && p.catch) {
      p.catch(function () {
        // 自动播放被拦（首次访问）：等第一次点击或按键再起
        armOnce();
      });
    }
  }

  var armed = false;
  function armOnce() {
    if (armed) return;
    armed = true;
    function go() {
      document.removeEventListener('pointerdown', go, true);
      document.removeEventListener('keydown', go, true);
      if (on) tryPlay();
    }
    document.addEventListener('pointerdown', go, true);
    document.addEventListener('keydown', go, true);
  }

  audio.addEventListener('loadedmetadata', function () {
    restorePos();
    if (on) tryPlay();
  });
  audio.addEventListener('timeupdate', function () { savePos(false); });
  audio.addEventListener('ended', function () { savePos(true); });
  window.addEventListener('pagehide', function () { savePos(true); });
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) savePos(true);
  });

  // ── 开关按钮 ──
  function paint() {
    if (!btn) return;            // loadedmetadata 可能早于按钮创建
    btn.classList.toggle('off', !on);
    btn.classList.toggle('playing', on && !audio.paused);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.querySelector('.txt').textContent = on ? '音乐 开' : '音乐 关';
    btn.title = on ? '背景音乐：开（点击关闭）' : '背景音乐：关（点击开启）';
  }

  var css = document.createElement('style');
  // 颜色一律走主题变量：写死浅色的话，深色模式下会在左下角留一块白底亮片
  css.textContent =
    '#bgmBtn{position:fixed;left:22px;bottom:22px;z-index:70;display:flex;align-items:center;' +
    'gap:6px;padding:8px 13px;border-radius:999px;border:1px solid var(--line,#d8e3ee);' +
    'background:var(--card,#fff);color:var(--p1,#1f5fa8);' +
    'font:600 12.5px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",' +
    '"Microsoft YaHei",sans-serif;cursor:pointer;box-shadow:0 4px 14px rgba(20,40,70,.14);' +
    'opacity:.9;transition:opacity .15s,color .15s}' +
    '#bgmBtn:hover{opacity:1}' +
    '#bgmBtn.off{color:var(--muted,#8a9aaa)}' +
    '#bgmBtn .note{font-size:15px;line-height:1}' +
    '#bgmBtn.playing .note{display:inline-block;animation:bgmBeat 1.2s ease-in-out infinite}' +
    '@keyframes bgmBeat{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}' +
    '@media print{#bgmBtn{display:none}}' +
    '@media(max-width:640px){#bgmBtn{left:14px;bottom:14px;padding:7px 11px;font-size:12px}}';
  document.head.appendChild(css);

  var btn = document.createElement('button');
  btn.id = 'bgmBtn';
  btn.type = 'button';
  btn.innerHTML = '<span class="note">♪</span><span class="txt">音乐</span>';
  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    on = !on;
    try { localStorage.setItem(ON_KEY, on ? '1' : '0'); } catch (e2) {}
    if (on) { tryPlay(); } else { audio.pause(); savePos(true); }
    paint();
  });
  audio.addEventListener('play', paint);
  audio.addEventListener('pause', paint);

  function mount() {
    if (!document.body.contains(btn)) document.body.appendChild(btn);
    paint();
  }
  if (document.body) mount();
  else document.addEventListener('DOMContentLoaded', mount);
})();
