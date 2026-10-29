# -*- coding: utf-8 -*-
"""把 web/ppt/slide-NN.png 组装成可浏览器直接打开的 HTML 课件。

为什么需要它：.pptx 在浏览器/预览面板里打不开，而且无法被课程页深度链接。
HTML 版可以：浏览器直接看、支持键盘翻页、能被任意单元页链到指定页。

产出：web/ppt/index.html
"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PPT_DIR = os.path.join(ROOT, "web", "ppt")

# 课件页数据统一来自 tools/ppt_map.py（单一数据源）
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import ppt_map
SLIDES = ppt_map.SLIDES

PPTX = "Python阶段0-2课程大纲.pptx"
# web/ppt/index.html -> 项目根要退两级
PPTX_REL = "../../python-course-ppt/" + PPTX


def main():
    missing = [n for n, *_ in SLIDES
               if not os.path.exists(os.path.join(PPT_DIR, f"slide-{n:02d}.webp"))]
    if missing:
        raise SystemExit(f"缺少图片：{missing}")

    data = json.dumps(
        [{"n": n, "t": t, "r": r, "u": u} for n, t, r, u in SLIDES],
        ensure_ascii=False, indent=None)

    html = TEMPLATE.replace("__DATA__", data).replace("__PPTX__", PPTX_REL)
    out = os.path.join(PPT_DIR, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"生成 {out}（{len(SLIDES)} 页，{len(html)//1024} KB）")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>课程课件 · Python 阶段 0–2（23 页）</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\'%3E%3Crect width=\'32\' height=\'32\' rx=\'7\' fill=\'%231f5fa8\'/%3E%3Ctext x=\'16\' y=\'22\' font-size=\'15\' font-family=\'monospace\' fill=\'%23fff\' text-anchor=\'middle\'%3EPy%3C/text%3E%3C/svg%3E">
<style>
:root{--bg:#eef2f7;--card:#fff;--line:#d8e3ee;--text:#16232e;--muted:#55687a;
--p1:#1f5fa8;--p2:#0a7d63;--p3:#a06009}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);line-height:1.7;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}
a{color:var(--p1);text-decoration:none}
a:hover{text-decoration:underline}

/* 顶栏 */
.top{position:sticky;top:0;z-index:30;background:rgba(238,242,247,.94);
backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top-in{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;
align-items:center;gap:14px;flex-wrap:wrap}
.brand{font-size:17px;font-weight:700}
.badge{font-size:12.5px;font-weight:700;color:#fff;background:var(--p3);
border-radius:5px;padding:3px 10px}
.spacer{flex:1}
.btn{font-size:13.5px;border:1px solid var(--line);background:#fff;color:var(--p1);
border-radius:8px;padding:7px 13px;cursor:pointer;font-family:inherit;font-weight:600}
.btn:hover{background:#f2f7fd;text-decoration:none}
.btn.primary{background:var(--p1);color:#fff;border-color:var(--p1)}
.btn.primary:hover{background:#1a5192}

/* 主体 */
.wrap{max-width:1180px;margin:0 auto;padding:22px 22px 60px}
h1{font-size:24px;margin:6px 0 4px}
.sub{color:var(--muted);font-size:14.5px;margin:0 0 18px}

/* 舞台 */
.stage{background:var(--card);border:1px solid var(--line);border-radius:14px;
box-shadow:0 2px 12px rgba(22,35,46,.06);overflow:hidden}
.stage-img{display:block;width:100%;height:auto;background:#fff}
.bar{display:flex;align-items:center;gap:12px;padding:12px 16px;
border-top:1px solid var(--line);flex-wrap:wrap}
.bar .t{font-size:15px;font-weight:700}
.bar .u{font-size:12.5px;color:var(--muted)}
.bar .u a{font-weight:600}

/* 缩略图 */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));
gap:12px;margin-top:22px}
.cell{background:var(--card);border:2px solid var(--line);border-radius:10px;
padding:0;cursor:pointer;overflow:hidden;text-align:left;font-family:inherit;
transition:border-color .12s,transform .12s}
.cell:hover{border-color:var(--p1);transform:translateY(-2px)}
.cell.on{border-color:var(--p3);box-shadow:0 0 0 3px rgba(224,138,21,.16)}
.cell img{display:block;width:100%;height:auto}
.cell .cap{padding:8px 10px;font-size:12.5px;color:var(--text);display:flex;
gap:7px;align-items:baseline}
.cell .no{font-weight:700;color:var(--p1);font-variant-numeric:tabular-nums}

/* 说明条 */
.note{background:#fff;border:1px solid var(--line);border-left:4px solid var(--p2);
border-radius:10px;padding:14px 18px;margin-top:22px;font-size:14px;color:#3a4a58}
.note b{color:var(--p2)}
kbd{background:#f2f5f9;border:1px solid var(--line);border-bottom-width:2px;
border-radius:5px;padding:1px 6px;font-size:12.5px;font-family:inherit}

@media (max-width:640px){.top-in,.wrap{padding-left:14px;padding-right:14px}
h1{font-size:20px}.grid{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}}

/* 打印：一页一图 */
@media print{.top,.grid,.bar,.note{display:none}
.stage{border:0;box-shadow:none}.stage-img{page-break-after:always}}
</style>
</head>
<body>

<div class="top"><div class="top-in">
  <span class="brand">课程课件</span>
  <span class="badge">23 页 · 阶段 0–2</span>
  <span class="spacer"></span>
  <a class="btn" href="u/index.html">逐节版课件（22 份）</a>
  <a class="btn" href="../lessons/index.html">按课节学</a>
  <a class="btn" href="../../index.html">课程主页</a>
  <a class="btn primary" href="__PPTX__" download>下载 .pptx</a>
</div></div>

<div class="wrap">
  <h1>Python 阶段 0–2 · 课程课件</h1>
  <p class="sub">与课程一一对应：每个单元都能在课件里找到对应页。点缩略图跳转，或按
     <kbd>←</kbd> <kbd>→</kbd> 翻页。</p>

  <div class="stage">
    <img class="stage-img" id="img" alt="课件页">
    <div class="bar">
      <button class="btn" id="prev">← 上一页</button>
      <button class="btn" id="next">下一页 →</button>
      <span class="t" id="tt"></span>
      <span class="u" id="uu"></span>
      <span class="spacer"></span>
      <span class="u" id="pg"></span>
    </div>
  </div>

  <div class="note">
    <b>怎么配合课程用：</b>这一份是<b>课程大纲课件</b>，用来快速建立整体印象、做课程宣讲与排期。
    要<b>按节课讲</b>，请用 <a href="u/index.html">逐节版课件</a>——每个单元一份，
    每节课都有自己的课节页与知识点页。两份都能下载 <code>.pptx</code> 编辑。
  </div>

  <div class="grid" id="grid"></div>
</div>

<script>
var S = __DATA__;
var cur = 0;
var img = document.getElementById('img');
var tt  = document.getElementById('tt');
var uu  = document.getElementById('uu');
var pg  = document.getElementById('pg');
var grid= document.getElementById('grid');

function pad(n){ return (n<10?'0':'')+n; }
function src(n){ return 'slide-'+pad(n)+'.webp'; }

function show(i, push){
  if(i<0) i=0; if(i>=S.length) i=S.length-1;
  cur=i; var s=S[i];
  img.src=src(s.n);
  tt.textContent=s.t;
  if(s.u){
    var us=s.u.split(',');
    uu.innerHTML='对应单元 '+us.map(function(x){
      return '<a href="../lessons/index.html#u'+x+'">'+x+'</a>';
    }).join(' / ');
  } else { uu.textContent=''; }
  pg.textContent=(i+1)+' / '+S.length;
  var cells=grid.children;
  for(var k=0;k<cells.length;k++) cells[k].className='cell'+(k===i?' on':'');
  if(push!==false) history.replaceState(null,'','#s'+s.n);
}

S.forEach(function(s,i){
  var b=document.createElement('button');
  b.className='cell'; b.type='button';
  b.innerHTML='<img loading="lazy" src="'+src(s.n)+'" alt=""><span class="cap">'+
    '<span class="no">'+pad(s.n)+'</span><span>'+s.t+'</span></span>';
  b.onclick=function(){ show(i); window.scrollTo({top:0,behavior:'smooth'}); };
  grid.appendChild(b);
});

document.getElementById('prev').onclick=function(){ show(cur-1); };
document.getElementById('next').onclick=function(){ show(cur+1); };

document.addEventListener('keydown',function(e){
  if(e.key==='ArrowLeft'||e.key==='PageUp'){ show(cur-1); e.preventDefault(); }
  else if(e.key==='ArrowRight'||e.key==='PageDown'||e.key===' '){ show(cur+1); e.preventDefault(); }
  else if(e.key==='Home'){ show(0); }
  else if(e.key==='End'){ show(S.length-1); }
});

// 支持 #s14 深链
function fromHash(){
  var m=/^#s(\d+)$/.exec(location.hash||'');
  if(!m) return 0;
  var n=parseInt(m[1],10);
  for(var i=0;i<S.length;i++) if(S[i].n===n) return i;
  return 0;
}
window.addEventListener('hashchange',function(){ show(fromHash(), false); });
show(fromHash(), false);
</script>
<script src="../media/bgm.js" defer></script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
    import theme  # 主题派生：把浅色样式表翻成深色表并注入切换按钮
    theme.sweep([os.path.join(ROOT, "python-course-ppt")])
