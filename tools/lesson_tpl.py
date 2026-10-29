"""课程页模板（供 build_lessons.py 调用）。"""
import html
import re

CSS = """
/* 窄屏防溢出：flex 子项默认 min-width:auto，代码块会把整页撑宽 */
.main{min-width:0}
pre{max-width:100%}
.top-in{min-width:0}
.top-in h1{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
@media(max-width:1000px){
  .main{width:100%}
  pre{max-width:100%;overflow-x:auto}
}

:root{--bg:#f6f8fb;--card:#fff;--line:#e3e8ef;--text:#16232e;--muted:#55687a;
--p1:#1f5fa8;--p1bg:#eaf1fb;--p2:#0a7d63;--p2bg:#e6f6f0;--p3:#a06009;--p3bg:#fdf3e2;
--r:14px}

*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.75}
a{color:var(--p1);text-decoration:none}
a:hover{text-decoration:underline}

/* 顶栏 */
.top{position:sticky;top:0;z-index:40;background:rgba(246,248,251,.95);backdrop-filter:blur(10px);
border-bottom:1px solid var(--line)}
.top-in{max-width:1300px;margin:0 auto;padding:0 22px;height:58px;display:flex;align-items:center;gap:14px}
.top-in .sp{flex:1}
.top-in .ppt{font-size:12.5px;font-weight:700;color:#8a5a00;background:#fdf3e2;
border:1px solid #f0d8a8;border-radius:6px;padding:4px 10px;white-space:nowrap}
.top-in .ppt:hover{background:#fbe9cc;text-decoration:none}
.top-in .rv{font-size:12.5px;font-weight:700;color:#0b6e54;background:#e6f6f0;
border:1px solid #b8e0d0;border-radius:6px;padding:4px 10px;white-space:nowrap}
.top-in .rv:hover{background:#d3efe4;text-decoration:none}
.back{font-size:13.5px;color:var(--muted);white-space:nowrap}
.top-in .tno{font-size:11.5px;font-weight:700;color:var(--p1);background:var(--p1bg);
border-radius:20px;padding:3px 10px;white-space:nowrap;font-variant-numeric:tabular-nums}
.top h1{font-size:15.5px;margin:0;font-weight:700;flex:1;min-width:0;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* 课次进度条 */
.pbar{height:4px;background:#e8edf3;position:sticky;top:58px;z-index:39}
.pbar i{display:block;height:100%;background:linear-gradient(90deg,var(--p1),var(--p2))}

/* 布局 */
.layout{max-width:1300px;margin:0 auto;padding:24px 22px 80px;display:flex;gap:24px;align-items:flex-start}
.side{width:250px;flex-shrink:0;position:sticky;top:96px;max-height:calc(100vh - 120px);
overflow-y:auto}
.sblk{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 14px;margin-bottom:12px}
/* 侧栏底部：通向完整目录的那一条 */
.nall{display:flex;align-items:center;gap:6px;margin-top:8px;padding:8px 9px;
border-top:1px dashed var(--line);font-size:12px;font-weight:700;color:var(--p1);
text-decoration:none}
.nall .ar{margin-left:auto;transition:transform .15s}
.nall:hover{text-decoration:none;color:#18528f}
.nall:hover .ar{transform:translateX(3px)}
pre .cp{position:absolute;top:6px;right:10px;font:inherit;font-size:11.5px;
font-weight:700;color:var(--p1);background:#fff;border:1px solid var(--line);
border-radius:6px;padding:2px 9px;cursor:pointer;opacity:0;transition:opacity .12s}
pre:hover .cp{opacity:1}
pre .cp.ok{color:#fff;background:var(--p2);border-color:var(--p2)}
.gatebar{display:flex;align-items:center;gap:12px;background:#fdf3e2;
border:1px solid #f0d8a8;border-radius:12px;padding:12px 15px;margin:0 0 16px;
font-size:13.5px;color:#6b4700;flex-wrap:wrap}
.gatebar .gi{font-size:18px;color:var(--p3)}
.gatebar b{color:#8a5a00}
.gatebar span{color:#7a5c1e}
.gatebar a{margin-left:auto;font-weight:700;color:#fff;background:var(--p3);
border-radius:7px;padding:5px 12px;white-space:nowrap}
.pptbox{padding:12px}
.ppt-thumb{display:block;text-decoration:none;color:inherit}
.ppt-thumb img{display:block;width:100%;height:auto;border:1px solid var(--line);
border-radius:8px;background:#fff;transition:border-color .12s}
.ppt-thumb:hover img{border-color:var(--p1)}
.ppt-thumb .cap{display:block;margin-top:8px;font-size:12px;color:var(--text);line-height:1.5}
.ppt-thumb .cap b{color:var(--p3);font-variant-numeric:tabular-nums}
.rel{margin-top:11px;border-top:1px dashed var(--line);padding-top:9px;
display:flex;flex-direction:column;gap:2px}
.rel a{display:flex;gap:8px;align-items:baseline;padding:5px 6px;border-radius:7px;
text-decoration:none;color:inherit}
.rel a:hover{background:#f2f7fd}
.rel .k{flex:0 0 30px;font-size:11px;font-weight:700;color:#fff;background:var(--p1);
border-radius:4px;text-align:center;line-height:17px}
.rel a:nth-child(2) .k{background:var(--p3)}
.rel a:nth-child(3) .k{background:var(--p2)}
.rel a:nth-child(4) .k{background:#5e6f7e}
.rel .v{font-size:12px;color:var(--text);line-height:1.45}
.ppt-thumb .go{display:block;margin-top:5px;font-size:11.5px;font-weight:700;color:var(--p1)}
.sblk h4{margin:0 0 10px;font-size:11.5px;color:var(--muted);letter-spacing:1px;font-weight:700}
.toc a{display:block;padding:5px 7px;border-radius:6px;font-size:13px;color:#3d5063;
border-left:2px solid transparent;line-height:1.5}
.toc a:hover{background:#f2f5f9;text-decoration:none}
.toc a.lv3{padding-left:16px;font-size:12.5px;color:var(--muted)}
.nlist a{display:flex;gap:8px;align-items:flex-start;padding:6px 7px;border-radius:6px;font-size:12.5px;
color:#3d5063;line-height:1.5}
.nlist a:hover{background:#f2f5f9;text-decoration:none}
.nlist .no{font-size:10.5px;font-weight:700;color:var(--muted);min-width:19px;flex-shrink:0;
padding-top:1px;font-variant-numeric:tabular-nums}
.nlist a.cur{background:var(--p1bg);color:var(--p1);font-weight:600}
.nlist a.done .no{color:var(--p2)}
.nlist a.done::after{content:'✓';color:var(--p2);font-weight:700;margin-left:auto;font-size:12px}

.main{flex:1;min-width:0;background:var(--card);border:1px solid var(--line);
border-radius:var(--r);padding:32px 38px;overflow-wrap:anywhere}
.head{border-bottom:2px solid var(--line);padding-bottom:20px;margin-bottom:24px}
.kicker{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.kno{background:var(--p1);color:#fff;font-size:12.5px;font-weight:700;
padding:4px 12px;border-radius:20px;letter-spacing:.5px}
.kwk{background:#eef1f5;color:var(--muted);font-size:12.5px;font-weight:600;
padding:4px 11px;border-radius:20px}
.ku{background:var(--p2bg);color:#0a7a5f;font-size:12.5px;font-weight:600;
padding:4px 11px;border-radius:20px}
.head h1{font-size:29px;margin:0 0 12px;line-height:1.3}
.head .goal{font-size:15.5px;color:#40566b;margin:0;line-height:1.7}

/* 课堂区块 */
.blk{margin:22px 0;padding:20px 22px;border-radius:12px}
.blk.live{background:var(--p2bg);border:1px solid #bfe5d6}
.blk.hw{background:var(--p3bg);border:1px solid #ecd9b0}
.blk.recap{background:#f3f0fb;border:1px solid #ddd5f2}
.blk h3{margin:0 0 13px;font-size:16px;display:flex;align-items:center;gap:9px}
.blk.live h3{color:#0a7a5f}
.blk.hw h3{color:#8f5a0a}
.blk.recap h3{color:#5b46a8}
.blk.review{background:#fdf6ec;border:1px solid #f0dcb4}
.blk.review h3{color:#8f5a0a}
.rv-sum{margin-top:14px;padding:11px 15px;background:rgba(255,255,255,.7);
border-left:3px solid var(--p3);border-radius:0 8px 8px 0}
.rv-sum b{display:block;font-size:12px;color:#8f5a0a;letter-spacing:.5px;margin-bottom:3px}
.rv-sum span{font-size:14.5px;color:#33475a;line-height:1.7}
.blk ol{margin:0;padding-left:22px}
.blk ul{margin:0;padding-left:22px}
.blk li{margin:9px 0;font-size:14.5px;line-height:1.7;color:#33475a}
.blk.recap li{margin:8px 0}
.toc a.rc{color:#5b46a8;font-weight:600}
.toc a.rv{color:#8f5a0a;font-weight:600}
.blk code{background:rgba(255,255,255,.75);border:1px solid rgba(120,110,160,.22);
border-radius:4px;padding:1px 5px;font-size:12.8px}

/* 90 分钟 */
.sched{display:flex;gap:9px;margin:20px 0 4px}
.sc{flex:1;background:#f8fafc;border:1px solid var(--line);border-radius:9px;
padding:11px 8px;text-align:center;color:inherit;text-decoration:none}
a.sc:hover{background:#eef2f7;border-color:var(--p1)}
.sc b{display:block;font-size:20px;font-weight:700;color:var(--p1);line-height:1.2}
.sc span{font-size:11.5px;color:var(--muted)}
.sc.hi{background:var(--p2bg);border-color:#bfe5d6}
.sc.hi b{color:var(--p2)}

/* 正文 */
.main h2{font-size:21px;margin:34px 0 13px;padding-left:12px;border-left:4px solid var(--p1);line-height:1.4}
.main h3{font-size:16.5px;margin:24px 0 9px;color:var(--p1)}
.main h4{font-size:15px;margin:18px 0 8px;color:#33475a}
.main p{margin:11px 0}
.main ul,.main ol{margin:11px 0;padding-left:24px}
.main li{margin:6px 0}
.main strong{color:#0f4c8a}
.main hr{border:none;border-top:1px dashed var(--line);margin:26px 0}
.main blockquote{margin:14px 0;padding:12px 16px;background:var(--p1bg);
border-left:4px solid var(--p1);border-radius:0 8px 8px 0;color:#2c4a68;font-size:14px}
.main blockquote p{margin:4px 0}
.main code{background:#eef1f5;border-radius:4px;padding:2px 6px;font-size:.88em;
font-family:Consolas,"SFMono-Regular",monospace;color:#0f5a3d}
.main table{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}
.main th{background:#f1f4f8;padding:10px 13px;text-align:left;font-size:13px;
color:var(--muted);border:1px solid var(--line);font-weight:600}
.main td{padding:10px 13px;border:1px solid var(--line);vertical-align:top}
.main pre{background:#1e2a35;border-radius:10px;padding:0;margin:16px 0;position:relative;overflow:hidden}
.main pre code{display:block;padding:16px 18px;font-size:13.5px;line-height:1.65;
font-family:Consolas,"SFMono-Regular",monospace;background:none;overflow-x:auto;
/* 代码块底色在两种主题里都是深色终端，所以文字必须显式给浅色：
   否则会继承 .main code 的深绿，深底深字只剩 1.1:1（曾整站代码块都看不清） */
color:#e6edf5}
.main pre .cl{position:absolute;top:8px;right:12px;font-size:10.5px;color:#a8b6c4;
background:rgba(255,255,255,.07);padding:2px 8px;border-radius:4px}
.main pre.broken{border:2px dashed var(--p3)}
.badge-broken{display:inline-block;background:var(--p3bg);color:#8f5a0a;font-size:11.5px;
font-weight:700;padding:4px 11px;border-radius:5px;margin:4px 0 0}

/* 底部导航 */
.pn{display:flex;gap:12px;margin-top:36px;padding-top:22px;border-top:1px solid var(--line)}
.pn a{flex:1;background:#f8fafc;border:1px solid var(--line);border-radius:10px;padding:13px 17px}
.pn a:hover{background:#eef2f7;border-color:var(--p1);text-decoration:none}
.pn .nx{text-align:right}
.pn small{display:block;font-size:11.5px;color:var(--muted);margin-bottom:3px}
.pn b{font-size:14.5px}

.done-bar{display:flex;align-items:center;gap:12px;margin-top:26px;padding:15px 20px;
background:var(--card);border:1px solid var(--line);border-radius:12px;flex-wrap:wrap}
.done-bar label{display:flex;align-items:center;gap:9px;font-size:14.5px;cursor:pointer;font-weight:600}
.done-bar input{width:19px;height:19px;accent-color:var(--p2);cursor:pointer}
.done-bar a{margin-left:auto;font-size:13.5px}

/* ── 本节讲解视频（PIL 逐帧合成，深色底与站点深色模式同源）── */
.vidblk{padding:16px 18px 18px}
.vidblk h3{margin:0 0 12px}
.vidblk video{width:100%;max-width:860px;display:block;border-radius:12px;
background:#0b1220;box-shadow:0 8px 26px rgba(10,20,40,.26);
/* video 内的 fallback 文字：底色恒为深蓝，字色不能跟随主题，否则深底深字 */
color:#dce6f2}
.vidblk .vnote{margin:10px 0 0;font-size:13.5px;color:var(--muted,#5f7183)}

/* ── 打印：只留正文，去掉侧栏/导航/交互件 ── */
@media print{
  .top,.side,.done-bar,.pn,.lc-ck,.tools,.vidblk{display:none!important}
  body{background:#fff}
  .layout{display:block;padding:0}
  .main{padding:0;max-width:none}
  .head h1{font-size:24px}
  .blk{border:1px solid #ccc;background:#fff;break-inside:avoid}
  /* 代码块屏幕上一直是深色终端底，直接打印就是一片黑还费墨 → 打印翻白底深字。
     .main pre 优先级比 pre 高，不加 !important 翻不过来（原来就是这么漏的）。 */
  .main pre,pre{background:#fff!important;color:#16232e!important;
   border:1px solid #ccc;break-inside:avoid;font-size:10.5pt}
  .main pre code,pre code{color:#16232e!important;white-space:pre-wrap;word-break:break-all}
  .main pre .cl,pre .cl{color:#55687a!important;background:none!important}
  h2{break-after:avoid}
  a{color:#000;text-decoration:none}
  .tip{break-inside:avoid}
}
@page{margin:16mm 14mm}

@media(max-width:1000px){
 .layout{flex-direction:column-reverse;align-items:stretch;padding:16px 14px 60px}
 .side{position:static;width:100%;max-height:none;margin-top:16px}
 .main{padding:22px 16px}
 .head h1{font-size:22px}
 .sched{flex-wrap:wrap}.sc{min-width:80px}
 .pn{flex-direction:column}
}
/* 窄屏顶栏只留「返回 + 标题 + 课件」：课号与复习入口在正文/侧栏都有，避免挤掉标题 */
@media(max-width:620px){
 .top-in{gap:10px;padding:0 14px}
 .top-in .tno,.top-in .rv,.top-in .sp{display:none}
 /* 90 分钟四段改 2×2，避免 3+1 参差 */
 .sched{display:grid;grid-template-columns:1fr 1fr;gap:8px}
 .sc{min-width:0}
}

"""

# 复习计划页（web/review.html）专用样式：跟着 unit.css 一起用
REVIEW_CSS = """
:root{--p4:#c8443c;--p4bg:#fbeceb}
.dash{background:#fff;border:1px solid var(--line);border-radius:14px;
padding:16px 18px;margin:0 0 16px}
.dhead{display:flex;align-items:baseline;gap:12px;margin-bottom:12px}
.dhead b{font-size:15px}
.dhead span{font-size:12px;color:var(--muted)}
.drow{display:flex;align-items:center;gap:12px;margin:8px 0}
.dlab{flex:0 0 34px;font-size:12.5px;font-weight:700;color:var(--muted)}
.dbar{flex:1;height:9px;background:#e6ecf3;border-radius:99px;overflow:hidden}
.dbar i{display:block;height:100%;width:0;border-radius:99px;
background:linear-gradient(90deg,#2f6df6,#22a06b);transition:width .25s}
.dbar.b2 i{background:linear-gradient(90deg,#1f5fa8,#0a7d63)}
.dbar.b3 i{background:linear-gradient(90deg,#a06009,#c46f00)}
.dval{flex:0 0 auto;min-width:110px;text-align:right;font-size:12.5px;
font-weight:700;white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--text)}
.top-in .sp{flex:1}
.rv-hero{background:linear-gradient(135deg,#1f5fa8,#0a7d63);border-radius:16px;
padding:30px 34px;color:#fff;margin:0 0 20px}
.rv-hero h1{margin:0 0 8px;font-size:27px;line-height:1.3}
.rv-hero p{margin:0;font-size:14px;color:#dbe8f5;line-height:1.85;max-width:760px}
.rv-hero .st{display:flex;gap:34px;flex-wrap:wrap;margin-top:16px}
.rv-hero .st b{display:block;font-size:24px;font-weight:700;line-height:1.2}
.rv-hero .st span{font-size:12px;color:#c9dcf0}
.rv-sec{display:flex;align-items:baseline;gap:12px;margin:32px 0 14px}
.rv-sec h2{font-size:20px;margin:0}
.rv-sec span{font-size:12.5px;color:var(--muted)}
.rv-item{display:flex;gap:14px;background:var(--card);border:1px solid var(--line);
border-radius:13px;padding:14px 16px;margin:0 0 10px}
.rv-item.over{border-color:#ecc9c6;background:#fdf7f6}
.rv-no{flex:0 0 40px;height:40px;border-radius:10px;background:var(--p1bg);color:var(--p1);
display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;
font-variant-numeric:tabular-nums}
.rv-item.over .rv-no{background:var(--p4bg);color:var(--p4)}
.rv-bd{flex:1;min-width:0}
.rv-t{font-size:15px;font-weight:700;line-height:1.45}
.rv-m{font-size:12px;color:var(--muted);margin-top:2px}
.rv-m .od{color:var(--p4);font-weight:700}
.rv-task{font-size:13px;color:#33475a;line-height:1.7;margin-top:6px;
background:#f4f7fb;border-radius:8px;padding:8px 12px}
.rv-act{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px;align-items:center}
.rv-act a{font-size:12px;font-weight:700;color:var(--p1);background:#fff;
border:1px solid var(--line);border-radius:7px;padding:4px 11px}
.rv-act a:hover{background:var(--p1bg);text-decoration:none}
.rv-act button{font:inherit;font-size:12px;font-weight:700;color:#fff;background:var(--p2);
border:none;border-radius:7px;padding:5px 12px;cursor:pointer}
.rv-act button:hover{background:#0a7d61}
.rv-day{display:flex;align-items:baseline;gap:10px;margin:20px 0 9px}
.rv-day b{font-size:14px}
.rv-day b::before{content:'';display:inline-block;width:4px;height:13px;background:var(--p1);
border-radius:2px;margin-right:8px;vertical-align:-1px}
.rv-c{display:flex;align-items:center;gap:11px;padding:8px 4px;
border-bottom:1px dashed var(--line);font-size:13px}
.rv-c:last-child{border-bottom:none}
.rv-cn{flex:0 0 26px;font-size:12px;font-weight:800;color:var(--muted);
font-variant-numeric:tabular-nums;text-align:right}
.rv-cb{flex:1;height:8px;background:#e8edf3;border-radius:99px;overflow:hidden;min-width:40px}
.rv-cb i{display:block;height:100%;border-radius:99px;background:var(--p2)}
.rv-cb i.mid{background:var(--p3)}
.rv-cb i.low{background:var(--p4)}
.rv-cv{flex:0 0 44px;font-size:12px;font-weight:700;text-align:right;
font-variant-numeric:tabular-nums}
.rv-ct{flex:0 0 auto;font-size:12.5px;color:#3d5063;min-width:0;overflow:hidden;
text-overflow:ellipsis;white-space:nowrap}
.rv-rule{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:20px 24px;margin-top:34px;font-size:13.5px;line-height:1.9;color:#33475a}
.rv-rule h3{margin:0 0 8px;font-size:15.5px;color:var(--p1)}
.rv-rule table{width:100%;border-collapse:collapse;font-size:13px;margin:10px 0}
.rv-rule th{background:#f1f4f8;padding:8px 11px;text-align:left;font-size:12.5px;
color:var(--muted);border:1px solid var(--line);font-weight:600}
.rv-rule td{padding:8px 11px;border:1px solid var(--line);vertical-align:top}
.rv-empty{background:var(--card);border:1px dashed var(--line);border-radius:13px;
padding:30px 22px;text-align:center;font-size:13.5px;color:var(--muted);line-height:1.9}
.rv-empty a{font-weight:700}
.rv-foot{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:26px;
font-size:12px;color:var(--muted)}
.rv-foot button{font:inherit;font-size:12px;font-weight:600;color:var(--p4);background:#fff;
border:1px solid #ecc9c6;border-radius:7px;padding:5px 11px;cursor:pointer}
.rv-foot button:hover{background:var(--p4bg)}
.rv-wrap{max-width:1080px;margin:0 auto;padding:24px 22px 80px}
@media(max-width:620px){
 .rv-item{flex-direction:column;gap:9px}
 .rv-hero{padding:24px 20px}
 .rv-hero h1{font-size:22px}
 .rv-ct{flex:1 1 auto;white-space:normal}
 .rv-c{flex-wrap:wrap}
 .rv-rule{padding:16px}
 .rv-rule table{font-size:12px}
}
"""

JS = """
var K='lesson-done-v1';
function getAll(){try{return JSON.parse(localStorage.getItem(K)||'{}');}catch(e){return {};}}
function saveAll(o){try{localStorage.setItem(K,JSON.stringify(o));}catch(e){}}
function init(){
  var n=document.body.dataset.lesson, all=getAll();
  var pct=Object.keys(all).filter(function(k){return all[k];}).length;
  document.getElementById('pbar').style.width=(pct/ TOTAL *100)+'%';
  // 侧栏勾号
  document.querySelectorAll('.nlist a[data-n]').forEach(function(a){
    if(all[a.dataset.n]) a.classList.add('done');
    if(a.dataset.n===n) a.classList.add('cur');
  });
  var box=document.getElementById('doneBox');
  if(box){
    // 迁移：旧版只存布尔 true，没有完成时间；复习排程需要时间戳
    if(all[n]===true){ all[n]=Date.now(); saveAll(all); }
    box.checked=!!all[n];
    if(box.checked) document.getElementById('doneTxt').textContent='本节课已完成';
    box.addEventListener('change',function(){
      var o=getAll();
      if(box.checked){ if(o[n]===true) o[n]=Date.now(); if(!o[n]) o[n]=Date.now(); }
      else delete o[n];
      saveAll(o);
      document.getElementById('doneTxt').textContent=box.checked?'本节课已完成':'标记本节课已完成';
      document.querySelector('.nlist a[data-n="'+n+'"]').classList.toggle('done',box.checked);
      document.getElementById('pbar').style.width=(Object.keys(o).filter(function(k){return o[k];}).length/TOTAL*100)+'%';
    });
  }
  // 目录高亮
  var links=[].slice.call(document.querySelectorAll('.toc a'));
  var tg=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));});
  function on(){var y=scrollY+150,cur=0;tg.forEach(function(t,i){if(t&&t.offsetTop<=y)cur=i;});
    links.forEach(function(a,i){a.style.background=(i===cur)?'var(--p1bg)':'';
      a.style.borderLeftColor=(i===cur)?'var(--p1)':'transparent';});}
  on(); addEventListener('scroll',on,{passive:true});
  document.querySelectorAll('.main pre').forEach(function(p){});
}
document.addEventListener('DOMContentLoaded',function(){
  // 代码块角标由生成期已写入，仅补 tooltip
  document.querySelectorAll('.main pre').forEach(function(p){
    var c=p.querySelector('code'), lang=(c.className.match(/language-([\\w-]+)/)||[])[1];
    var lbl=(lang==='python'?'Python':(lang||'代码'));
    var s=document.createElement('span'); s.className='cl'; s.textContent=lbl;
    if(!p.querySelector('.cl')) p.insertBefore(s,c);
  });
  init();

  // 键盘翻页：← 上一节、→ 下一节（不在输入框里时才生效）
  document.addEventListener('keydown', function(e){
    var t=e.target.tagName;
    if(t==='INPUT'||t==='TEXTAREA'||e.metaKey||e.ctrlKey||e.altKey) return;
    if(e.key==='ArrowLeft'){var a=document.getElementById('prevLink'); if(a){location.href=a.href;}}
    if(e.key==='ArrowRight'){var b=document.getElementById('nextLink'); if(b){location.href=b.href;}}
  });
});
"""

COPY_JS = """
/* 长页回到顶部 */
(function(){
  var b=document.createElement('button');
  b.id='toTop'; b.type='button'; b.title='回到顶部'; b.textContent='↑';
  document.body.appendChild(b);
  function sync(){ b.classList.toggle('on', window.scrollY>500); }
  window.addEventListener('scroll',sync,{passive:true}); sync();
  b.addEventListener('click',function(){ window.scrollTo({top:0,behavior:'smooth'}); });
})();

/* 代码块一键复制 */
(function(){
  document.querySelectorAll('pre').forEach(function(pre){
    if(pre.querySelector('.cp')) return;
    var b=document.createElement('button');
    b.className='cp'; b.type='button'; b.textContent='复制';
    b.addEventListener('click', function(){
      var code=pre.querySelector('code')||pre, txt=code.innerText;
      function ok(){b.textContent='已复制 ✓';b.classList.add('ok');
        setTimeout(function(){b.textContent='复制';b.classList.remove('ok')},1500);}
      function fallback(){
        var t=document.createElement('textarea'); t.value=txt;
        t.style.position='fixed'; t.style.opacity='0';
        document.body.appendChild(t); t.select();
        try{document.execCommand('copy');ok();}catch(e){}
        document.body.removeChild(t);
      }
      if(navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(txt).then(ok, fallback);
      } else fallback();
    });
    pre.appendChild(b);
  });
})();
"""

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import ppt_map
import bank_map
UNIT_SLIDE = ppt_map.UNIT_SLIDE

# 关卡课节 -> 独立验收页（web/gate1.html、gate2.html）
GATE_OF = {
    63: ("../gate1.html", "关卡 1", "4 条验收 · 19 项自测"),
    110: ("../gate2.html", "关卡 2", "5 条硬指标 · 逐条验证"),
}

UNIT_TITLE = {
    0: "环境与工具链", 1: "变量与简单数据类型", 2: "列表简介", 3: "操作列表",
    4: "if 语句", 5: "字典", 6: "用户输入与 while 循环", 7: "函数", 8: "类",
    9: "文件与异常", 10: "测试代码", 11: "阶段 1 总复习 + 关卡验收",
    12: "Pygame 起步与飞船驾驶", 13: "射击与外星舰队", 14: "Play 按钮与记分",
    15: "Matplotlib 生成数据", 16: "下载真实数据", 17: "使用 API 与 Plotly",
    18: "Django 入门", 19: "用户账户", 20: "样式与部署",
    21: "阶段 2 综合 + 关卡 2 验收",
}

# 每单元属于哪个阶段（用于目录页分组标题）
STAGE_OF = {u: (1 if u <= 11 else 2) for u in UNIT_TITLE}

# 带讲解视频的课节：课节号 -> (视频, 封面)，路径相对 web/lessons/。
# 视频由 tools/make_lesson_video.py 生成（PIL 逐帧合成 → libx264）。
# 不进 SW 预缓存：1.6 MB 的视频按需加载就好，别占离线配额。
LESSON_VIDEOS = {1: ("../media/lesson01.mp4", "../media/lesson01-poster.jpg")}
STAGE_NAME = {
    1: "阶段 1 · 语法基础（教材第 1–11 章）",
    2: "阶段 2 · 项目实践（教材第 12–20 章）",
}

def toc_html(body):
    items = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body, re.S):
        lvl, aid, txt = m.group(1), m.group(2), re.sub(r"<[^>]+>", "", m.group(3))
        items.append(f'<a class="lv{lvl}" href="#{aid}">{html.escape(txt)}</a>')
    return "\n".join(items)

def nav_list(meta, cur):
    """右侧整册 38 节列表。"""
    out = []
    for m in meta:
        out.append(
            f'<a href="{m["file"]}" data-n="{m["no"]}">'
            f'<span class="no">{m["no"]:02d}</span>'
            f'<span>{m["title"]}</span></a>')
    return "\n".join(out)

def lesson_page(no, total, unit, week, title, goal, live, hw, body,
                prev_link, next_link, all_meta, recap_head=None, recap_items=None,
                review_items=None, review_summary=None):
    left = []
    if prev_link:
        p, pn = prev_link
        left.append(f'<a class="pn" id="prevLink" href="{pn:02d}.html"><small>← 上一节</small>'
                    f'<b>第 {pn} 节 · {html.escape(p[3])}</b></a>')
    else:
        left.append('<div class="pn" style="background:none;border:none"></div>')

    if next_link:
        nx, nn = next_link
        left.append(f'<a class="pn nx" id="nextLink" href="{nn:02d}.html"><small>下一节 →</small>'
                    f'<b>第 {nn} 节 · {html.escape(nx[3])}</b></a>')
    else:
        left.append('<a class="pn nx" id="nextLink" href="index.html"><small>全部课程 →</small>'
                    '<b>回到课程目录</b></a>')

    # 课件入口：优先指向「逐节版」单元课件里属于本课节的那两页
    _du, _ds = ppt_map.lesson_deck(no)          # 逐节版：单元号 + 页码
    _sn = ppt_map.slide_for_lesson(no, unit, title)   # 大纲版回落
    if _du is not None:
        _href = f'../ppt/u/{_du:02d}.html#s{_ds}'
        _label = f'本课课件 u{_du}·p{_ds}'
    elif _sn:
        _href = f'../ppt/index.html#s{_sn}'
        _label = f'课件 p{_sn}'
    else:
        _href, _label = '', ''
    ppt_link = (f'<a class="ppt" href="{_href}" title="本课节对应的课件">{_label}</a>'
                if _href else '')
    # 配套资料：本单元的讲义 / 课件 / 课节 / 题库，全部指向「本节对应的那一份」
    _ut = UNIT_TITLE.get(unit, "")
    _scope = ("本节对应页" if _sn and
              ppt_map.slide_for_lesson(no, unit, title)
              != ppt_map.UNIT_SLIDE.get(unit) else "本单元概览")
    _thumb = ""
    if _du is not None:
        _st = "本课节课件"
        _thumb = f'''<a class="ppt-thumb" href="../ppt/u/{_du:02d}.html#s{_ds}">
        <img loading="lazy" src="../ppt/u/{_du:02d}/slide-{_ds:02d}.webp" alt="{_st}">
        <span class="cap"><b>单元 {_du} · p{_ds}</b> 课节页与知识点页</span>
        <span class="go">打开本课课件 →</span>
      </a>'''
    elif _sn:
        _st = ppt_map.TITLE_BY_NO.get(_sn, "")
        _thumb = f'''<a class="ppt-thumb" href="../ppt/index.html#s{_sn}">
        <img loading="lazy" src="../ppt/slide-{_sn:02d}.webp" alt="{_st}">
        <span class="cap"><b>p{_sn}</b> {_st}</span>
        <span class="go">打开课件看这一页 →</span>
      </a>'''
    # 关卡课节：正文前插一条醒目的验收入口
    _g = GATE_OF.get(no)
    gate_banner = (f'''<div class="gatebar">
      <span class="gi">★</span>
      <div><b>这节课是 {_g[1]}的现场测评。</b>
        <span>别只看讲义——打开验收清单逐条勾，全绿才算过。</span></div>
      <a href="{_g[0]}">打开验收清单 →</a>
    </div>''' if _g else "")

    ppt_box = f'''<div class="sblk pptbox">
      <h4>配套资料 · 单元 {unit}</h4>
      {_thumb}
      <div class="rel">
        <a href="../{unit:02d}.html"><span class="k">讲义</span>
          <span class="v">单元 {unit} · {_ut}</span></a>
        <a href="{_href or "../ppt/index.html"}"><span class="k">课件</span>
          <span class="v">本课节逐节课件</span></a>
        <a href="index.html#u{unit}"><span class="k">课节</span>
          <span class="v">本单元全部课节</span></a>
        <a href="../bank.html{("#u%d" % unit) if bank_map.count(unit) else ""}"><span class="k">题库</span>
          <span class="v">{("本单元 %d 题 · 共 %d 题" % (bank_map.count(unit), bank_map.TOTAL))
                            if bank_map.count(unit) else
                            ("题库暂未覆盖本单元 · 共 %d 题" % bank_map.TOTAL)}</span></a>
        <a href="../review.html"><span class="k">复习</span>
          <span class="v">艾宾浩斯复习计划 · 6 轮</span></a>
      </div>
    </div>
'''

    toc = toc_html(body)
    # 侧栏只列本单元的课节：整册 111 条太长，完整目录给一条直达链接
    unit_meta = [m for m in all_meta if m["unit"] == unit]
    # 侧栏目录：复盘置顶、讲评收尾，两个环节都能一键跳回
    toc_label = "开课准备" if no == 1 else "复盘上一节"
    toc = (f'<a class="lv2 rc" href="#recap">◆ {toc_label}</a>\n' + toc
           + '\n<a class="lv2 rv" href="#review">◆ 讲评与本节总结</a>')

    # 复盘块：内容自带 <b>/<code> 等标签，故意不转义
    if recap_items:
        recap_html = ('<div class="blk recap" id="recap">'
                      f'<h3>◆ {recap_head}</h3>'
                      '<ul>' + ''.join(f'<li>{x}</li>' for x in recap_items) + '</ul>'
                      '</div>')
    else:
        recap_html = ''

    # 讲评块：内容自带 <b>/<code> 等标签，故意不转义
    if review_items:
        review_html = ('<div class="blk review" id="review">'
                       '<h3>◆ 讲评（20 分钟）｜对照检查你刚写的代码</h3>'
                       '<ul>' + ''.join(f'<li>{x}</li>' for x in review_items) + '</ul>'
                       + (f'<div class="rv-sum"><b>本节一句话总结</b>'
                          f'<span>{review_summary}</span></div>' if review_summary else '')
                       + '</div>')
    else:
        review_html = ''

    # 讲解视频块（目前只有第 1 节有；有视频的课节自动带上）
    vid = LESSON_VIDEOS.get(no)
    video_html = ''
    if vid:
        video_html = (f'<div class="blk vidblk" id="video">'
                      f'<h3>◆ 本节讲解视频（约 1 分钟 · 无声带字幕）</h3>'
                      f'<video controls preload="metadata" playsinline '
                      f'poster="{vid[1]}"><source src="{vid[0]}" type="video/mp4">'
                      f'你的浏览器不支持 video 标签，请直接看下面的图文讲解。</video>'
                      f'<p class="vnote">节奏与正文一致：先分清解释器、终端、编辑器三个角色，'
                      f'再跟着敲 hello.py。声音版以后会补。</p></div>')

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>第 {no} 节 · {html.escape(title)}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f5fa8'/%3E%3Ctext x='16' y='22' font-size='15' font-family='monospace' fill='%23fff' text-anchor='middle'%3EPy%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="lessons.css">
<style>
#toTop{{position:fixed;right:22px;bottom:22px;width:42px;height:42px;border-radius:50%;
background:#1f5fa8;color:#fff;border:none;font-size:18px;line-height:1;cursor:pointer;
box-shadow:0 6px 18px rgba(20,40,70,.22);opacity:0;pointer-events:none;
transition:opacity .18s;z-index:60}}
#toTop.on{{opacity:1;pointer-events:auto}}
@media print{{#toTop{{display:none}}}}
</style>
</head>
<body data-lesson="{no}">
<div class="top"><div class="top-in">
  <a class="back" href="index.html">← 课程目录</a>
  <span class="tno">第 {no} 节</span>
  <h1>{html.escape(title)}</h1>
  <span class="sp"></span>
  <a class="rv" href="../review.html">复习</a>
  {ppt_link}
</div></div>
<div class="pbar"><i id="pbar"></i></div>

<div class="layout">
  <aside class="side">
    <div class="sblk">
      <h4>本节内容</h4>
      <nav class="toc">{toc}</nav>
    </div>
    <div class="sblk">
      <h4>单元 {unit} · 共 {len(unit_meta)} 节</h4>
      <nav class="nlist">{nav_list(unit_meta, no)}</nav>
      <a class="nall" href="index.html#u{unit}">
        <span>全部 {total} 节目录</span><span class="ar">→</span></a>
    </div>
    {ppt_box}
  </aside>

  <main class="main">
    <div class="head">
      <div class="kicker">
        <span class="kno">第 {no} 节 / {total}</span>
        <span class="kwk">{html.escape(week)}</span>
        <span class="ku">单元 {unit} · {html.escape(UNIT_TITLE[unit])}</span>
      </div>
      <h1>{html.escape(title)}</h1>
      <p class="goal">{html.escape(goal)}</p>
    </div>
    {gate_banner}

    {video_html}

    <div class="sched">
      <a class="sc" href="#recap"><b>10</b><span>复盘 min</span></a>
      <div class="sc"><b>30</b><span>讲解 min</span></div>
      <div class="sc hi"><b>40</b><span>实操 min</span></div>
      <a class="sc hi" href="#review"><b>20</b><span>讲评 min</span></a>
    </div>

    {recap_html}

    <div class="blk live">
      <h3>◆ 课堂实操（40 分钟，全程不许看答案）</h3>
      <ol>{''.join(f'<li>{html.escape(x)}</li>' for x in live)}</ol>
    </div>

    {body}

    <div class="blk hw">
      <h3>◆ 课后作业</h3>
      <ol>{''.join(f'<li>{html.escape(x)}</li>' for x in hw)}</ol>
    </div>

    {review_html}

    <div class="done-bar">
      <label><input type="checkbox" id="doneBox"><span id="doneTxt">标记本节课已完成</span></label>
      <a href="../review.html">复习计划 →</a>
      <a href="../{unit:02d}.html">查看单元 {unit} 完整讲义 →</a>
      <a href="../bank.html">打开练习题库 →</a>
    </div>

    <div class="pn">{''.join(left)}</div>
  </main>
</div>

<script>var TOTAL={total};</script>
<script>{JS}{COPY_JS}</script>
<script src="../media/bgm.js" defer></script>
</body>
</html>"""

# 艾宾浩斯复习间隔（学完后的天数）：当天 → 2 → 4 → 8 → 16 → 31 天
REVIEW_STAGES = [
    (0,  "当天复盘", "合上讲义，凭记忆写下本节课 3 个要点，再把「课堂实操」的代码重敲一遍"),
    (1,  "第 2 天",  "重读讲义本小节，然后独立完成「课后作业」，全程不许看答案"),
    (3,  "第 4 天",  "把本节课的代码故意改错 3 处，试着只凭报错信息定位问题"),
    (7,  "第 8 天",  "做题库里本单元对应的题，做错的在题库里标成「待复习」"),
    (15, "第 16 天", "给别人讲一遍这节课（费曼技巧），卡住的地方记下来回看"),
    (30, "第 31 天", "只看目录复述本节结构，并回顾「讲评」里列出的常见错误"),
]

def review_page(meta):
    """复习计划页（web/review.html）：按艾宾浩斯曲线给 111 节课排 6 轮复习。"""
    import json
    lessons = [{"n": m["no"], "t": m["title"], "u": m["unit"]} for m in meta]
    n_lessons = len(lessons)
    n_rounds = n_lessons * len(REVIEW_STAGES)
    stage_rows = "".join(
        f"<tr><td>{i}</td><td>{html.escape(lab)}</td><td>学完第 {off} 天</td>"
        f"<td>{html.escape(task)}</td></tr>"
        for i, (off, lab, task) in enumerate(REVIEW_STAGES, 1))

    body = """<div class="rv-wrap">
  <div class="rv-hero">
    <h1>复习计划 · 艾宾浩斯遗忘曲线</h1>
    <p>每学完一节课，自动排 6 轮复习：当天 → 第 2 天 → 第 4 天 → 第 8 天 → 第 16 天 → 第 31 天。
    每轮只花 5–15 分钟，做完点「标记完成」，后面的轮次自动接上；错过时间会标成逾期，越早补上越省力。
    进度只存本机浏览器，不联网。</p>
    <div class="st">
      <div><b>__NR__</b><span>轮复习</span></div>
      <div><b>__NL__</b><span>节课</span></div>
      <div><b>__NA__</b><span>个复习点</span></div>
    </div>
  </div>

  <div class="dash" id="lprog">
    <div class="dhead"><b>复习看板</b><span id="rvSum">统计中…</span></div>
    <div class="drow"><span class="dlab">今日</span><div class="dbar"><i id="rvPT"></i></div>
      <span class="dval" id="rvTT">0 项</span></div>
    <div class="drow"><span class="dlab">逾期</span><div class="dbar b3"><i id="rvPO"></i></div>
      <span class="dval" id="rvTO">0 项</span></div>
    <div class="drow"><span class="dlab">轮次</span><div class="dbar b2"><i id="rvPR"></i></div>
      <span class="dval" id="rvTR">0 / __NA__</span></div>
    <div class="drow"><span class="dlab">掌握</span><div class="dbar"><i id="rvPM"></i></div>
      <span class="dval" id="rvTM">0 / __NL__ 课</span></div>
  </div>

  <div class="rv-sec"><h2>今日待复习</h2><span id="nowSub">含逾期未补的</span></div>
  <div id="rvNow"></div>

  <div class="rv-sec"><h2>未来安排</h2><span>按到期日分组</span></div>
  <div id="rvPlan"></div>

  <div class="rv-sec"><h2>记忆保持率</h2><span>估算值，越靠前越该先复习</span></div>
  <div class="dash" style="padding:8px 18px"><div id="rvCurve"></div></div>

  <div class="rv-rule">
    <h3>为什么是这几个时间点</h3>
    <p>艾宾浩斯遗忘曲线描述的是「学完后记忆保持率随时间下降」的规律：记住的内容在最初几小时
    掉得最快，随后趋于平缓。在快要忘掉的时点做一次主动回忆，遗忘速度会明显变慢，这就是间隔重复
    （spaced repetition）。下表是本课程采用的时间点，来自曲线上「掉得快」与「快掉完」两段密集区。</p>
    <table>
      <thead><tr><th>轮次</th><th>时点</th><th>距学完</th><th>做什么（5–15 分钟）</th></tr></thead>
      <tbody>__ROWS__</tbody>
    </table>
    <p><b>记忆保持率怎么算：</b>用指数衰减 R = e<sup>-t/S</sup> 估算。基础稳定期 S = 2 天，
    每完成一轮复习 S ×2，所以复习得越及时，同一节课后面越难忘。这里的数字只是提醒工具，
    真正的标准是「合上资料能不能讲出来」。</p>
    <p><b>使用建议：</b>① 今天排的任务今天清，逾期超过 3 轮建议直接重学该课；
    ② 复习时先自己回忆再看资料，效果远好过重读；③ 与题库配合：标记「待复习」的题优先做。</p>
  </div>

  <div class="rv-foot">
    <a href="lessons/index.html">课程目录</a> ·
    <a href="bank.html">题库</a> ·
    <a href="gate1.html">关卡 1</a> ·
    <a href="../index.html">回主页</a>
    <span style="flex:1"></span>
    <button id="rvClear" type="button">清空复习记录</button>
  </div>
</div>"""

    body = (body.replace("__NR__", str(len(REVIEW_STAGES)))
                .replace("__NL__", str(n_lessons))
                .replace("__NA__", str(n_rounds))
                .replace("__ROWS__", stage_rows))

    js = """(function(){
  var LESSONS = __LESSONS__, STAGES = __STAGES__;
  var LKEY = 'lesson-done-v1', RKEY = 'lesson-review-v1';
  var DAY = 86400000, WEEK = ['日','一','二','三','四','五','六'];

  function read(k){ try{ var v = JSON.parse(localStorage.getItem(k)); return v == null ? {} : v }catch(e){ return {} } }
  function write(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)) }catch(e){} }
  function mid(t){ var d = new Date(t); d.setHours(0,0,0,0); return d.getTime(); }
  function pad(n){ return (n < 10 ? '0' : '') + n; }
  function lp(n){ return (n < 10 ? '0' : '') + n; }
  function dlabel(t){ var d = new Date(t); return pad(d.getMonth()+1) + '-' + pad(d.getDate()) + ' 周' + WEEK[d.getDay()]; }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  var TODAY = mid(Date.now());
  var L = read(LKEY), R = read(RKEY), moved = false, pruned = false;
  for (var k in L) if (L[k] === true) { L[k] = Date.now(); moved = true; }
  if (moved) write(LKEY, L);
  for (var k2 in R) if (!L[k2]) { delete R[k2]; pruned = true; }
  if (pruned) write(RKEY, R);

  function collect(){
    var due = [], plan = [], rows = [], totalDone = 0, mastered = 0;
    LESSONS.forEach(function(x){
      var t = L[x.n];
      if (!t) return;
      var learned = mid(t), rs = R[x.n] || [], done = 0, last = t;
      STAGES.forEach(function(s, i){
        if (rs[i]) { done++; if (rs[i] > last) last = rs[i]; }
      });
      totalDone += done;
      if (done === STAGES.length) mastered++;
      var S = 2;
      for (var i = 0; i < done; i++) S *= 2;
      var ret = Math.exp(-((TODAY - mid(last)) / DAY) / S);
      rows.push({ x: x, done: done, ret: ret, last: last });
      STAGES.forEach(function(s, i){
        if (rs[i]) return;
        var d = learned + s[0] * DAY;
        var item = { x: x, i: i, lab: s[1], task: s[2], due: d,
                     od: Math.round((TODAY - d) / DAY) };
        if (d <= TODAY) due.push(item); else plan.push(item);
      });
    });
    due.sort(function(a, b){ return a.due - b.due; });
    plan.sort(function(a, b){ return a.due - b.due; });
    rows.sort(function(a, b){ return a.ret - b.ret; });
    return { due: due, plan: plan, rows: rows, totalDone: totalDone, mastered: mastered };
  }

  function itemHtml(it, overdue){
    var when;
    if (it.od > 0) when = '原定 ' + dlabel(it.due);
    else if (it.od === 0) when = '今天到期';
    else when = dlabel(it.due) + ' 到期';
    var meta = '单元 ' + it.x.u + ' · 第 ' + (it.i + 1) + ' / ' + STAGES.length + ' 轮 · ' + it.lab + ' · ' + when;
    return '<div class="rv-item' + (overdue ? ' over' : '') + '">'
      + '<div class="rv-no">' + lp(it.x.n) + '</div><div class="rv-bd">'
      + '<div class="rv-t">第 ' + it.x.n + ' 节 · ' + esc(it.x.t) + '</div>'
      + '<div class="rv-m">' + esc(meta)
      + (it.od > 0 ? ' · <span class="od">逾期 ' + it.od + ' 天</span>' : '') + '</div>'
      + '<div class="rv-task">任务：' + esc(it.task) + '</div>'
      + '<div class="rv-act">'
      + '<a href="lessons/l' + lp(it.x.n) + '.html">去复习</a>'
      + '<a href="' + lp(it.x.u) + '.html">看讲义</a>'
      + '<a href="bank.html#u' + it.x.u + '">做本题</a>'
      + '<button type="button" data-g="' + it.x.n + '" data-i="' + it.i + '">标记完成</button>'
      + '</div></div></div>';
  }

  function render(){
    var d = collect();
    var todayN = 0, overN = 0;
    d.due.forEach(function(it){ if (it.od > 0) overN++; else todayN++; });

    document.getElementById('rvTT').textContent = todayN + ' 项';
    document.getElementById('rvTO').textContent = overN + ' 项';
    document.getElementById('rvTR').textContent = d.totalDone + ' / ' + (LESSONS.length * STAGES.length);
    document.getElementById('rvTM').textContent = d.mastered + ' / ' + LESSONS.length + ' 节';
    document.getElementById('rvPT').style.width = (todayN / Math.max(1, LESSONS.length) * 100) + '%';
    document.getElementById('rvPO').style.width = (overN / Math.max(1, LESSONS.length) * 100) + '%';
    document.getElementById('rvPR').style.width = (d.totalDone / (LESSONS.length * STAGES.length) * 100) + '%';
    document.getElementById('rvPM').style.width = (d.mastered / LESSONS.length * 100) + '%';
    document.getElementById('rvSum').textContent = d.rows.length
      ? ('已学 ' + d.rows.length + ' 节 · 待复习 ' + (d.due.length + d.plan.length) + ' 项')
      : '还没有已学完的课节';

    var now = document.getElementById('rvNow');
    if (!d.rows.length) {
      now.innerHTML = '<div class="rv-empty">还没有已学完的课节。去完成'
        + ' <a href="lessons/01.html">第 1 节</a>，当天就会生成第一轮复习任务。</div>';
    } else if (!d.due.length) {
      now.innerHTML = '<div class="rv-empty">今天没有待复习的课，保持住 👍<br>'
        + '下一批安排见下方「未来安排」。</div>';
    } else {
      now.innerHTML = d.due.map(function(it){ return itemHtml(it, it.od > 0); }).join('');
    }

    var pl = document.getElementById('rvPlan');
    if (!d.plan.length) {
      pl.innerHTML = '<div class="rv-empty">未来两周没有新的复习点——要么都复习完了，要么还没开始学。</div>';
    } else {
      var html = '', cur = '', shown = 0;
      d.plan.forEach(function(it){
        if (shown >= 60) return;
        var lab = dlabel(it.due);
        if (lab !== cur) {
          cur = lab;
          html += '<div class="rv-day"><b>' + lab + '</b></div>';
        }
        html += itemHtml(it, false);
        shown++;
      });
      if (d.plan.length > shown) {
        html += '<div class="rv-empty">其余 ' + (d.plan.length - shown) + ' 项在更远的日期，学完后面的课再来看。</div>';
      }
      pl.innerHTML = html;
    }

    var cv = document.getElementById('rvCurve');
    if (!d.rows.length) {
      cv.innerHTML = '<div class="rv-empty" style="border:none">学完第一节课后，这里会显示每节课的记忆保持率。</div>';
    } else {
      cv.innerHTML = d.rows.map(function(r){
        var pct = Math.round(r.ret * 100);
        var cls = pct >= 80 ? '' : (pct >= 50 ? ' mid' : ' low');
        var days = Math.round((TODAY - mid(r.last)) / DAY);
        return '<div class="rv-c"><div class="rv-cn">' + lp(r.x.n) + '</div>'
          + '<div class="rv-cb"><i class="' + cls + '" style="width:' + Math.max(3, pct) + '%"></i></div>'
          + '<div class="rv-cv">' + pct + '%</div>'
          + '<div class="rv-ct">第 ' + r.x.n + ' 节 · ' + esc(r.x.t)
          + ' · 已复习 ' + r.done + ' 轮 · 距上次 ' + days + ' 天</div></div>';
      }).join('');
    }
  }

  document.addEventListener('click', function(e){
    var b = e.target.closest('button[data-g]');
    if (!b) return;
    var g = +b.dataset.g, i = +b.dataset.i;
    var r = read(RKEY), a = r[g] || (r[g] = []);
    a[i] = Date.now();
    write(RKEY, r);
    R = r;
    render();
  });
  document.getElementById('rvClear').addEventListener('click', function(){
    if (!confirm('清空全部复习记录？课节进度不受影响，复习轮次会重新排。')) return;
    write(RKEY, {});
    R = {};
    render();
  });
  window.addEventListener('focus', render);
  document.addEventListener('visibilitychange', function(){
    if (!document.hidden) render();
  });
  render();
})();
""".replace("__LESSONS__", json.dumps(lessons, ensure_ascii=False)) \
   .replace("__STAGES__", json.dumps([[o, l, t] for o, l, t in REVIEW_STAGES],
                                     ensure_ascii=False))

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>复习计划 · 艾宾浩斯遗忘曲线</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f5fa8'/%3E%3Ctext x='16' y='22' font-size='15' font-family='monospace' fill='%23fff' text-anchor='middle'%3EPy%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="css/unit.css">
<style>__CSS__</style>
</head>
<body>
<div class="top"><div class="top-in">
  <a class="back" href="../index.html">← 主页</a>
  <h1>复习计划 · 艾宾浩斯遗忘曲线</h1>
  <span class="sp"></span>
  <a class="ppt" href="lessons/index.html">课程目录</a>
</div></div>
__BODY__
<script>__JS__</script>
<script src="media/bgm.js" defer></script>
</body>
</html>""".replace("__CSS__", REVIEW_CSS).replace("__BODY__", body).replace("__JS__", js)

def index_page(meta):
    """课程总目录：按单元分组，按周标注。"""
    by_unit = {}
    for m in meta:
        by_unit.setdefault(m["unit"], []).append(m)

    groups = []
    prev_stage = None
    for u in sorted(by_unit):
        stage = STAGE_OF.get(u, 1)
        if stage != prev_stage:
            n_units = len([k for k in by_unit if STAGE_OF.get(k, 1) == stage])
            n_less = sum(len(by_unit[k]) for k in by_unit
                         if STAGE_OF.get(k, 1) == stage)
            groups.append(
                '<div class="stage-sep" id="s' + str(stage) + '">'
                + '<span class="ss-no">阶段 ' + str(stage) + '</span>'
                + '<h2>' + html.escape(STAGE_NAME[stage]) + '</h2>'
                + '<span class="ss-m">' + str(n_units) + ' 个单元 · '
                + str(n_less) + ' 节课</span></div>')
            prev_stage = stage
        ls = by_unit[u]
        cards = []
        for m in ls:
            hw_short = html.escape(re.sub(r"★\s*", "", m["hw"][0]))
            hw_more = f' · 另有 {len(m["hw"])-1} 项' if len(m["hw"]) > 1 else ""
            # 搜索索引 = 标题 + 目标 + 小节标题，便于按内容（如 parametrize）定位
            search_blob = " ".join([m["title"], m["goal"]] + m.get("sections", []))
            search_blob = re.sub(r"\s+", " ", search_blob)
            cards.append(f"""
        <div class="lc" data-no="{m['no']}" data-t="{html.escape(search_blob, quote=True)}">
          <a class="lc-a" href="{m['file']}">
          <div class="lc-h">
            <span class="lc-n">{m['no']:02d}</span>
            <div style="flex:1;min-width:0">
              <h4>{html.escape(m['title'])}</h4>
              <p>{html.escape(m['goal'])}</p>
            </div>
            <span class="lc-w">{html.escape(m['week'])}</span>
          </div>
          <div class="lc-f"><b>实操</b> {html.escape(m['live'][0])}{' …' if len(m['live'])>1 else ''}</div>
          <div class="lc-f"><b>作业</b> {hw_short}{hw_more}</div>
          </a>
          <button class="lc-ck" type="button" data-no="{m['no']}"
                  aria-label="标记第 {m['no']} 节课完成">标记完成</button>
        </div>""")
        weeks = "、".join(sorted(set(l["week"] for l in ls)))
        _sn = ppt_map.slide_for_unit(u)
        _ppt = (f'<a class="ug-l" href="../ppt/u/{u:02d}.html">课件</a>'
                if _sn else '')
        groups.append(f"""
      <div class="ug" id="u{u}">
        <div class="ug-h">
          <span class="ug-n">{u}</span>
          <h3>{html.escape(UNIT_TITLE[u])}</h3>
          <span class="ug-m">{len(ls)} 节 · {html.escape(weeks)}</span>
          <span class="ug-ls">
            <a class="ug-l" href="../{u:02d}.html">讲义</a>
            {_ppt}
          </span>
        </div>
        <div class="lg">{''.join(cards)}</div>
      </div>""")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>课程目录 · {len(meta)} 节课</title>
<meta name="theme-color" content="#1f5fa8">
<link rel="manifest" href="../manifest.webmanifest">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f5fa8'/%3E%3Ctext x='16' y='22' font-size='15' font-family='monospace' fill='%23fff' text-anchor='middle'%3EPy%3C/text%3E%3C/svg%3E">
<style>
:root{{--bg:#f6f8fb;--card:#fff;--line:#e3e8ef;--text:#16232e;--muted:#55687a;
--p1:#1f5fa8;--p1bg:#eaf1fb;--p2:#0a7d63;--p2bg:#e6f6f0;--p3:#a06009;--p3bg:#fdf3e2}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.7}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:1160px;margin:0 auto;padding:0 24px 80px}}
.top{{position:sticky;top:0;z-index:40;background:rgba(246,248,251,.95);backdrop-filter:blur(10px);
border-bottom:1px solid var(--line)}}
.top-in{{max-width:1160px;margin:0 auto;padding:0 24px;height:58px;display:flex;align-items:center;gap:16px}}
.top h1{{font-size:16px;margin:0;font-weight:700;flex:1}}
.back{{font-size:13.5px;color:var(--muted)}}

.hero{{position:relative;overflow:hidden;border-radius:20px;margin:26px 0 30px;
background:linear-gradient(135deg,#1f5fa8 0%,#0a7d63 100%);padding:44px 46px;color:#fff}}
.hero::after{{content:'';position:absolute;right:-80px;bottom:-130px;width:400px;height:400px;
border-radius:50%;background:rgba(255,255,255,.08)}}
.hero>*{{position:relative;z-index:1}}
.hero .bdg{{display:inline-block;background:var(--p3);border-radius:6px;padding:5px 14px;
font-size:12.5px;font-weight:700;letter-spacing:1.5px;margin-bottom:18px}}
.hero h1{{font-size:38px;margin:0 0 12px;line-height:1.25}}
.hero p{{font-size:16px;color:#dcebf7;margin:0 0 26px;max-width:660px}}
.st{{display:flex;gap:40px;flex-wrap:wrap}}
.st b{{display:block;font-size:30px;font-weight:700;line-height:1.2}}
.st span{{font-size:12.5px;color:#b9d5ea}}

.pg{{display:flex;align-items:center;gap:14px;margin-bottom:28px;padding:16px 20px;
background:var(--card);border:1px solid var(--line);border-radius:12px;flex-wrap:wrap}}
.pg b{{font-size:14px;color:var(--muted);font-weight:600}}
.pg .tr{{flex:1;min-width:180px;height:8px;background:#e8edf3;border-radius:8px;overflow:hidden}}
.pg .tr i{{display:block;height:100%;background:linear-gradient(90deg,var(--p1),var(--p2));width:0;transition:width .25s}}
.pg .ct{{font-size:13px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}}

h2{{font-size:21px;margin:36px 0 6px;display:flex;align-items:center;gap:10px}}
h2 i{{width:9px;height:9px;border-radius:50%;background:var(--p1);display:block}}
.sub{{font-size:13.5px;color:var(--muted);margin:0 0 18px}}

.ug{{margin-bottom:26px}}
.ug-h{{display:flex;align-items:center;gap:11px;margin-bottom:12px;flex-wrap:wrap}}
.ug-n{{width:32px;height:32px;border-radius:8px;background:var(--p1);color:#fff;
display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0}}
.ug-h h3{{margin:0;font-size:17px}}
.ug-ls{{display:flex;gap:7px;flex-wrap:wrap}}
.ug-l{{font-size:12px;font-weight:700;color:var(--p1);background:#fff;
border:1px solid var(--line);border-radius:6px;padding:3px 9px;text-decoration:none;
white-space:nowrap}}
.ug-l:hover{{background:var(--p1bg);border-color:var(--p1);text-decoration:none}}
.ug-m{{font-size:12.5px;color:var(--muted);margin-left:auto}}
.lg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px}}
.lc{{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:16px 18px;transition:border-color .15s}}
.lc:hover{{border-color:var(--p1);box-shadow:0 2px 12px rgba(31,95,168,.08)}}
.lc.done{{border-color:#b8e0d0;background:#f8fcfa}}
.lc-h{{display:flex;gap:12px;align-items:flex-start;margin-bottom:11px}}
.lc-n{{width:36px;height:36px;border-radius:9px;background:var(--p1bg);color:var(--p1);
display:flex;align-items:center;justify-content:center;font-size:13.5px;font-weight:700;flex-shrink:0}}
.lc.done .lc-n{{background:var(--p2bg);color:var(--p2)}}
.lc-h h4{{margin:0 0 3px;font-size:15.5px;line-height:1.4}}
.lc-h p{{margin:0;font-size:12.5px;color:var(--muted);line-height:1.6}}
.lc-w{{font-size:11.5px;color:var(--muted);font-weight:600;background:#f1f4f8;
padding:3px 9px;border-radius:20px;flex-shrink:0}}
.lc-f{{font-size:12.5px;color:#40566b;line-height:1.6;margin-top:5px}}
.lc-f b{{color:var(--p2);font-weight:700}}

/* 阶段分隔条 */
.stage-sep{{display:flex;align-items:center;gap:14px;margin:44px 0 18px;padding:16px 20px;
background:linear-gradient(90deg,var(--p1bg),#f8fafc);border:1px solid var(--line);
border-left:4px solid var(--p1);border-radius:0 12px 12px 0}}
.stage-sep .ss-no{{background:var(--p1);color:#fff;font-size:12px;font-weight:700;
padding:4px 12px;border-radius:20px;white-space:nowrap}}
.stage-sep h2{{margin:0;font-size:19px;color:var(--text)}}
.stage-sep .ss-m{{margin-left:auto;font-size:12.5px;color:var(--muted);white-space:nowrap}}

/* 单元快捷跳转 */
.ujump{{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 14px}}
.ujump a{{padding:5px 12px;border:1px solid var(--line);border-radius:16px;background:var(--card);
font-size:12px;color:var(--muted);text-decoration:none}}
.ujump a:hover{{border-color:var(--p1);color:var(--p1);background:var(--p1bg)}}

/* 搜索与筛选 */
.tools{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:16px}}
.tools .q{{flex:1;min-width:240px;padding:9px 14px;border:1px solid var(--line);border-radius:10px;
font-size:13.5px;font-family:inherit;background:var(--card);color:var(--text)}}
.tools .q:focus{{outline:none;border-color:var(--p1);box-shadow:0 0 0 3px rgba(31,95,168,.1)}}
.tools .fl{{display:flex;gap:6px}}
.tools .fb{{padding:7px 14px;border:1px solid var(--line);border-radius:20px;background:var(--card);
font-size:12.5px;color:var(--muted);cursor:pointer;font-family:inherit}}
.tools .fb:hover{{border-color:var(--p1);color:var(--p1)}}
.tools .fb.on{{background:var(--p1);border-color:var(--p1);color:#fff}}
.tools .cnt{{font-size:12px;color:var(--muted);white-space:nowrap}}
.pg .resume{{padding:7px 15px;border-radius:20px;background:var(--p1);color:#fff;
font-size:12.5px;font-weight:600;white-space:nowrap;text-decoration:none}}
.pg .resume:hover{{background:#1a5296}}
.pg .resume.all-done{{background:var(--p2)}}
.pg .rvgo{{padding:7px 15px;border-radius:20px;background:var(--p2bg);color:#0b6e54;
border:1px solid #b8e0d0;font-size:12.5px;font-weight:600;white-space:nowrap;text-decoration:none}}
.pg .rvgo:hover{{background:#d3efe4}}

/* 卡片：链接占主体，完成按钮独立，点链接只跳转不标记 */
.lc{{position:relative}}
.lc-a{{display:block;color:inherit;text-decoration:none}}
.lc-ck{{margin-top:11px;padding:6px 14px;border:1px solid var(--line);border-radius:8px;
background:#fff;font-size:12px;color:var(--muted);cursor:pointer;font-family:inherit;width:100%}}
.lc-ck:hover{{border-color:var(--p2);color:var(--p2)}}
.lc-ck.on{{background:var(--p2bg);border-color:#b8e0d0;color:var(--p2);font-weight:600}}

.tip{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:24px 26px;
margin-top:34px;display:flex;gap:14px;align-items:flex-start}}
.tip i{{width:4px;align-self:stretch;background:var(--p3);border-radius:2px;flex-shrink:0}}
.tip h4{{margin:0 0 8px;font-size:16px}}
.tip ul{{margin:0;padding-left:20px;font-size:14px;color:#40566b}}
.tip li{{margin:5px 0}}
footer{{border-top:1px solid var(--line);padding-top:20px;margin-top:36px;font-size:13px;color:var(--muted)}}
@media print{{
  .tools,.top{{display:none!important}}
  body{{background:#fff}}
  .hero{{padding:20px 0}}
  .lc{{break-inside:avoid;border-color:#ccc}}
  .lc-ck{{display:none!important}}
  a{{color:#000;text-decoration:none}}
}}
@page{{margin:14mm}}

@media(max-width:700px){{.wrap{{padding:0 14px 60px}}.hero{{padding:30px 22px}}.hero h1{{font-size:27px}}}}
</style>
</head>
<body>
<div class="top"><div class="top-in">
  <a class="back" href="../../index.html">← 学习主页</a>
  <h1>课程目录 · {len(meta)} 节课</h1>
  <span class="sp"></span>
  <a class="rv" href="../terms.html">术语索引</a>
  <a class="rv" href="../coverage.html">覆盖对照</a>
  <a class="rv" href="../review.html">复习计划</a>
  <a class="ppt" href="../ppt/index.html">课程课件 23 页</a>
</div></div>

<div class="wrap">
  <header class="hero">
    <span class="bdg">每次课 90 分钟 · 共 {len(meta)} 节</span>
    <h1>一节一节地上<br>而不是一章一章地啃</h1>
    <p>每个单元按 90 分钟课节切开，四段都有内容：
       <b>复盘 10</b> 回顾上一节要点 · <b>讲解 30</b> 知识点与示例 ·
       <b>实操 40</b> 跟着敲不许看答案 · <b>讲评 20</b> 对照自查你刚写的代码。
       每节还带明确目标、课后作业和一句话总结。</p>
    <div class="st">
      <div><b>{len(meta)}</b><span>节课</span></div>
      <div><b>{len(set(m["unit"] for m in meta))}</b><span>个单元</span></div>
      <div><b>29</b><span>周（每周 6–8 h）</span></div>
      <div><b>90</b><span>分钟 / 节</span></div>
    </div>
  </header>

  <div class="pg">
    <b>学习进度</b>
    <div class="tr"><i id="tr"></i></div>
    <span class="ct" id="ct">0 / {len(meta)} 节</span>
    <a class="rvgo" href="../review.html">今日复习 →</a>
    <a class="resume" id="resume" href="01.html">继续学习 →</a>
  </div>

  <h2><i></i>全部课程</h2>
  <p class="sub">按单元分组，点任意一节课进入。完成一节课后点卡片上的「标记完成」。
     搜索支持课节标题、学习目标和小节标题（试试「parametrize」「切片」「get()」）。</p>

  <div class="ujump">
    {''.join(f'<a href="#u{u}">单元 {u}</a>' for u in sorted(by_unit))}
  </div>

  <div class="tools">
    <input class="q" type="search" id="q" placeholder="搜课程标题或目标，如：继承 / 异常 / 函数"
           aria-label="搜索课程">
    <div class="fl" id="fl">
      <button class="fb on" data-f="all">全部</button>
      <button class="fb" data-f="todo">未完成</button>
      <button class="fb" data-f="done">已完成</button>
    </div>
    <span class="cnt" id="cnt"></span>
  </div>

  {''.join(groups)}

  <div class="tip"><i></i><div>
    <h4>怎么用这套课</h4>
    <ul>
      <li><b>不要跳课。</b>上一节的作业没做完就别开下一节，否则后面全是补课。</li>
      <li><b>实操环节必须动手敲。</b>看懂不等于会写，从空文件敲出来才算。</li>
      <li><b>卡住超过一周就降难度。</b>回到题库对应档位重做，别硬啃。</li>
      <li>每节课都能从底部跳回单元完整讲义或题库，需要查细节时随时回看。</li>
      <li><b>学完一节课，顺手去「复习计划」页。</b>当天、第 2 天、第 4 天、第 8 天、第 16 天、第 31 天
          各有一轮 5–15 分钟的复习，页面会按遗忘曲线排好，逾期会标红。</li>
      <li><b>讲评环节不要跳过。</b>那 20 分钟是给你自己检查代码的，对照每一条问句过一遍，
          比多写一小时更有用。</li>
    </ul>
  </div></div>

  <footer>
    依据《Python 编程：从入门到实践（第 3 版）》中文版上篇第 1–11 章 · 12 单元切分为 {len(meta)} 节课
  </footer>
</div>

<script>
var K='lesson-done-v1', TOTAL={len(meta)};
function getAll(){{try{{return JSON.parse(localStorage.getItem(K)||'{{}}');}}catch(e){{return {{}};}}}}
function doneCount(){{var o=getAll();return Object.keys(o).filter(function(k){{return o[k];}}).length;}}
var FILTER='all', QUERY='';

function render(){{  // 进度条、数字、继续学习入口
  var n=doneCount(), o=getAll();
  document.getElementById('tr').style.width=(n/TOTAL*100)+'%';
  document.getElementById('ct').textContent=n+' / '+TOTAL+' 节';
  var rs=document.getElementById('resume');
  if(rs){{
    var next=0;
    for(var i=1;i<=TOTAL;i++){{ if(!o[String(i)]){{ next=i; break; }} }}
    if(next===0){{
      rs.textContent='全部完成 ✓'; rs.classList.add('all-done');
      rs.href='index.html';
    }} else {{
      rs.textContent='继续学习：第 '+next+' 节 →';
      rs.href=(next<10?'0':'')+next+'.html';
    }}
  }}
}}

function paint(){{  // 卡片完成态 + 搜索 + 筛选
  var o=getAll();
  var cards=document.querySelectorAll('.lc');
  var shown=0;
  cards.forEach(function(el){{
    var no=el.dataset.no, isDone=!!o[no];
    el.classList.toggle('done', isDone);
    var ck=el.querySelector('.lc-ck');
    if(ck){{ ck.textContent=isDone?'已完成 ✓':'标记完成'; ck.classList.toggle('on', isDone); }}
    // 搜索
    var okQ = !QUERY || (el.dataset.t||'').toLowerCase().indexOf(QUERY)>=0;
    // 筛选
    var okF = FILTER==='all' || (FILTER==='done'? isDone : !isDone);
    var vis = okQ && okF;
    el.style.display = vis ? '' : 'none';
    if(vis) shown++;
    // 单元分组整组隐藏
    var grp=el.closest('.ug');
    if(grp){{
      var anyVis=false;
      grp.querySelectorAll('.lc').forEach(function(c){{ if(c.style.display!=='none') anyVis=true; }});
      grp.style.display = anyVis ? '' : 'none';
    }}
  }});
  document.getElementById('cnt').textContent = shown ? '显示 '+shown+' / '+TOTAL+' 节' : '没有匹配的课程';
}}

function apply(){{ render(); paint(); }}

document.getElementById('q').addEventListener('input', function(e){{
  QUERY=e.target.value.trim().toLowerCase(); paint();
}});

document.getElementById('fl').addEventListener('click', function(e){{
  var b=e.target.closest('.fb'); if(!b) return;
  FILTER=b.dataset.f;
  this.querySelectorAll('.fb').forEach(function(x){{ x.classList.toggle('on', x===b); }});
  paint();
}});

// 完成标记：只认按钮，点击卡片本身仅跳转，不再误标完成
document.querySelectorAll('.lc-ck').forEach(function(btn){{
  btn.addEventListener('click', function(e){{
    e.preventDefault(); e.stopPropagation();
    var no=btn.dataset.no, o=getAll();
    o[no]=!o[no];
    try{{localStorage.setItem(K,JSON.stringify(o));}}catch(err){{}}
    apply();
  }});
}});

apply();
</script>
<script src="../media/bgm.js" defer></script>
</body>
</html>"""