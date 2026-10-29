#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""全站神经元背景：固定层 canvas 上的节点 + 近邻连线，鼠标附近会连出高亮线。

和 theme.py 同构：用标记块内联注入，可重复执行（先剥旧段再写）。
之所以内联而不是拆成 media/neuron.js：
  1. 页面分布在根目录 / web / fluent / android/www 四层，相对路径各不相同；
  2. 内联不新增静态资源，SW 预缓存清单不用跟着改，file:// 便携版也照跑。

CSS 在脚本里用 createElement('style') 注入，不放静态 <style>——
否则会被 theme.py 的 _process_styles 当成待派生样式再处理一遍。

用法：
  python tools/neuron.py            # 全站注入
  python tools/neuron.py --check    # 只统计覆盖情况
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BEGIN = "<!-- neuron:begin -->"
END = "<!-- neuron:end -->"

JS = """<script>(function(){
var KEY='py-neuron-v1';
var DEF={on:1,dense:'mid',follow:1,speed:'mid'};
var DENSE={low:.55,mid:1,high:1.75};
var SPEED={slow:.35,mid:1,fast:1.9};
var raw=null,cfg={};
try{raw=localStorage.getItem(KEY)}catch(e){}
try{cfg=raw?JSON.parse(raw):{}}catch(e){cfg={}}
for(var k in DEF){if(typeof cfg[k]!==typeof DEF[k])cfg[k]=DEF[k]}
if(!DENSE[cfg.dense])cfg.dense='mid';
if(!SPEED[cfg.speed])cfg.speed='mid';
// 系统开了「减少动效」且用户没自己选过：默认不铺背景，别跟系统设置对着干
var rm=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)');
if(!raw&&rm&&rm.matches)cfg.on=0;
function save(){try{localStorage.setItem(KEY,JSON.stringify(cfg))}catch(e){}}

var CSS=
'#neuronCv{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;'+
'pointer-events:none;opacity:.62}'+
'#nrBtn{position:fixed;right:18px;bottom:22px;z-index:70;display:inline-flex;'+
'align-items:center;gap:6px;height:32px;padding:0 12px;border-radius:999px;'+
'border:1px solid var(--line,#e3e8ef);background:var(--card,#fff);'+
'color:var(--muted,#5f7183);font:inherit;font-size:12.5px;font-weight:700;'+
'line-height:1;cursor:pointer;box-shadow:0 4px 14px rgba(20,40,70,.13);'+
'opacity:.92;transition:opacity .15s,color .15s}'+
'#nrBtn:hover{opacity:1;color:var(--text,#16232e);border-color:var(--p1,#1f5fa8)}'+
'#nrBtn.on{color:var(--p1,#1f5fa8)}'+
'#nrBtn svg{width:15px;height:15px;display:block}'+
'#nrPanel{position:fixed;right:18px;bottom:62px;z-index:71;width:224px;'+
'background:var(--card,#fff);border:1px solid var(--line,#e3e8ef);'+
'border-radius:12px;padding:12px 14px;box-shadow:0 10px 30px rgba(20,40,70,.18);'+
'font:inherit;font-size:13px;color:var(--text,#16232e);display:none}'+
'#nrPanel.open{display:block}'+
'#nrPanel .row{display:flex;align-items:center;justify-content:space-between;'+
'gap:10px;padding:6px 0}'+
'#nrPanel .row+.row{border-top:1px solid var(--line,#e3e8ef)}'+
'#nrPanel .lb{font-size:12.5px;color:var(--muted,#5f7183);white-space:nowrap}'+
'#nrPanel .seg{display:flex;gap:4px}'+
'#nrPanel button{font:inherit;font-size:12px;font-weight:700;cursor:pointer;'+
'border:1px solid var(--line,#e3e8ef);background:transparent;'+
'color:var(--muted,#5f7183);border-radius:7px;padding:4px 8px;line-height:1}'+
'#nrPanel button.sel{background:var(--p1s,var(--p1,#1f5fa8));'+
'border-color:var(--p1s,var(--p1,#1f5fa8));color:#fff}'+
'#nrPanel .sw{min-width:44px}'+
'#nrPanel .sw.on{background:var(--p1s,var(--p1,#1f5fa8));'+
'border-color:var(--p1s,var(--p1,#1f5fa8));color:#fff}'+
'@media print{#neuronCv,#nrBtn,#nrPanel{display:none!important}}'+
'@media(max-width:640px){#nrBtn{right:14px;bottom:14px;height:30px;padding:0 10px}'+
'#nrPanel{right:14px;bottom:52px;width:calc(100vw - 28px);max-width:250px}}';
var st=document.createElement('style');st.textContent=CSS;document.head.appendChild(st);

var cv=document.createElement('canvas');
cv.id='neuronCv';cv.setAttribute('aria-hidden','true');
if(document.body)document.body.insertBefore(cv,document.body.firstChild);
else document.addEventListener('DOMContentLoaded',function(){
  document.body.insertBefore(cv,document.body.firstChild);});
var ctx=cv.getContext('2d');
var W=0,H=0,nodes=[],mx=-1,my=-1,hasM=false,raf=0;

function target(){
  var n=Math.round(W*H/17000*DENSE[cfg.dense]);
  return Math.max(16,Math.min(150,n));
}
function seed(){
  var n=target(),i;
  while(nodes.length>n)nodes.pop();
  while(nodes.length<n)nodes.push({x:Math.random()*W,y:Math.random()*H,
    vx:(Math.random()-.5)*.24,vy:(Math.random()-.5)*.24,r:Math.random()*1.3+1.1});
  for(i=0;i<nodes.length;i++){
    if(nodes[i].x>W)nodes[i].x=Math.random()*W;
    if(nodes[i].y>H)nodes[i].y=Math.random()*H;
  }
}
function resize(){
  var dpr=Math.min(window.devicePixelRatio||1,2);
  W=window.innerWidth;H=window.innerHeight;
  if(!W||!H)return;
  cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);
  cv.style.width=W+'px';cv.style.height=H+'px';
  ctx.setTransform(dpr,0,0,dpr,0,0);
  seed();
}
function frame(){
  raf=requestAnimationFrame(frame);
  var dark=document.documentElement.getAttribute('data-theme')==='dark';
  var dot=dark?'150,196,240':'31,95,168';
  var lin=dark?'99,169,238':'72,106,140';
  ctx.clearRect(0,0,W,H);
  var sp=SPEED[cfg.speed],i,j,a,b,dx,dy,d2,s;
  // 密度越高连线越短：否则节点一多就糊成一片网，看不出「神经元」
  var LINK=132/Math.sqrt(DENSE[cfg.dense]),L2=LINK*LINK;
  var MR=150,MR2=MR*MR;
  for(i=0;i<nodes.length;i++){
    a=nodes[i];
    a.x+=a.vx*sp;a.y+=a.vy*sp;
    if(a.x<-24)a.x=W+24;else if(a.x>W+24)a.x=-24;
    if(a.y<-24)a.y=H+24;else if(a.y>H+24)a.y=-24;
    if(hasM&&cfg.follow){
      dx=mx-a.x;dy=my-a.y;d2=dx*dx+dy*dy;
      if(d2<MR2&&d2>1){
        s=Math.sqrt(d2);
        a.vx+=dx/s*(1-s/MR)*.03;a.vy+=dy/s*(1-s/MR)*.03;
      }
    }
    // 限速：鼠标一直吸着会让节点越飞越快，最后整屏乱窜
    s=a.vx*a.vx+a.vy*a.vy;
    if(s>.36){s=Math.sqrt(s);a.vx=a.vx/s*.6;a.vy=a.vy/s*.6;}
  }
  ctx.lineWidth=1;
  for(i=0;i<nodes.length;i++){
    a=nodes[i];
    for(j=i+1;j<nodes.length;j++){
      b=nodes[j];dx=a.x-b.x;dy=a.y-b.y;d2=dx*dx+dy*dy;
      if(d2>L2)continue;
      ctx.strokeStyle='rgba('+lin+','+((1-Math.sqrt(d2)/LINK)*.4).toFixed(3)+')';
      ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
    }
  }
  if(hasM&&cfg.follow){
    for(i=0;i<nodes.length;i++){
      a=nodes[i];dx=a.x-mx;dy=a.y-my;d2=dx*dx+dy*dy;
      if(d2>MR2)continue;
      ctx.strokeStyle='rgba('+dot+','+((1-Math.sqrt(d2)/MR)*.45).toFixed(3)+')';
      ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(mx,my);ctx.stroke();
    }
    ctx.fillStyle='rgba('+dot+',.5)';
    ctx.beginPath();ctx.arc(mx,my,2.6,0,6.284);ctx.fill();
  }
  for(i=0;i<nodes.length;i++){
    a=nodes[i];
    ctx.fillStyle='rgba('+dot+',.5)';
    ctx.beginPath();ctx.arc(a.x,a.y,a.r,0,6.284);ctx.fill();
  }
}
function start(){if(!raf){raf=requestAnimationFrame(frame)}}
function stop(){if(raf){cancelAnimationFrame(raf);raf=0}ctx.clearRect(0,0,W,H)}

var ICON='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"'+
 'stroke-linecap="round"><circle cx="5" cy="6.5" r="1.9"/><circle cx="19" cy="8.5" r="1.9"/>'+
 '<circle cx="9" cy="18" r="1.9"/><circle cx="17.5" cy="17.5" r="1.4"/>'+
 '<path d="M5 6.5 19 8.5 9 18 5 6.5M19 8.5 17.5 17.5 9 18"/></svg>';
var btn=document.createElement('button');
btn.type='button';btn.id='nrBtn';
btn.innerHTML=ICON+'<span class="nrbt"></span>';
btn.setAttribute('aria-haspopup','true');
btn.setAttribute('aria-expanded','false');
var panel=document.createElement('div');
panel.id='nrPanel';
panel.setAttribute('role','group');
panel.setAttribute('aria-label','神经元背景设置');
panel.innerHTML=
 '<div class="row"><span class="lb">神经元背景</span>'+
 '<button type="button" class="sw" data-k="on"></button></div>'+
 '<div class="row"><span class="lb">密度</span><span class="seg" data-k="dense">'+
 '<button type="button" data-v="low">低</button>'+
 '<button type="button" data-v="mid">中</button>'+
 '<button type="button" data-v="high">高</button></span></div>'+
 '<div class="row"><span class="lb">鼠标跟随</span>'+
 '<button type="button" class="sw" data-k="follow"></button></div>'+
 '<div class="row"><span class="lb">动效</span><span class="seg" data-k="speed">'+
 '<button type="button" data-v="slow">静</button>'+
 '<button type="button" data-v="mid">缓</button>'+
 '<button type="button" data-v="fast">快</button></span></div>';
document.body.appendChild(btn);document.body.appendChild(panel);

function paint(){
  btn.classList.toggle('on',!!cfg.on);
  btn.querySelector('.nrbt').textContent=cfg.on?'背景 开':'背景 关';
  btn.setAttribute('aria-pressed',cfg.on?'true':'false');
  btn.title=cfg.on?'神经元背景：开（点击调整）':'神经元背景：关（点击调整）';
  var sw=panel.querySelectorAll('.sw');
  for(var i=0;i<sw.length;i++){
    var k=sw[i].getAttribute('data-k');
    sw[i].classList.toggle('on',!!cfg[k]);
    sw[i].textContent=cfg[k]?'开':'关';
    sw[i].setAttribute('aria-pressed',cfg[k]?'true':'false');
  }
  var sg=panel.querySelectorAll('.seg');
  for(i=0;i<sg.length;i++){
    var kk=sg[i].getAttribute('data-k'),bs=sg[i].querySelectorAll('button');
    for(var j=0;j<bs.length;j++)
      bs[j].classList.toggle('sel',bs[j].getAttribute('data-v')===cfg[kk]);
  }
}
function apply(){
  if(!W||!H)resize();
  cv.style.display=cfg.on?'':'none';
  if(cfg.on&&!document.hidden){seed();start()}else stop();
  paint();
}
btn.addEventListener('click',function(e){
  e.stopPropagation();
  panel.classList.toggle('open');
  btn.setAttribute('aria-expanded',panel.classList.contains('open')?'true':'false');
});
panel.addEventListener('click',function(e){
  var t=e.target;
  while(t&&t!==panel){
    if(t.getAttribute){
      var v=t.getAttribute('data-v');
      if(v){cfg[t.parentNode.getAttribute('data-k')]=v;save();apply();return}
      var k=t.getAttribute('data-k');
      if(k&&t.className.indexOf('sw')>=0){cfg[k]=cfg[k]?0:1;save();apply();return}
    }
    t=t.parentNode;
  }
});
document.addEventListener('click',function(e){
  if(!panel.classList.contains('open'))return;
  if(panel.contains(e.target)||btn.contains(e.target))return;
  panel.classList.remove('open');btn.setAttribute('aria-expanded','false');
});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'&&panel.classList.contains('open')){
    panel.classList.remove('open');btn.setAttribute('aria-expanded','false');
    btn.focus();
  }
});
window.addEventListener('mousemove',function(e){mx=e.clientX;my=e.clientY;hasM=true},{passive:true});
document.addEventListener('mouseleave',function(){hasM=false});
window.addEventListener('blur',function(){hasM=false});
window.addEventListener('touchmove',function(e){
  var t=e.touches&&e.touches[0];if(t){mx=t.clientX;my=t.clientY;hasM=true}},{passive:true});
window.addEventListener('touchend',function(){hasM=false});
var rt=0;
window.addEventListener('resize',function(){
  clearTimeout(rt);rt=setTimeout(function(){if(cfg.on)resize()},180)});
document.addEventListener('visibilitychange',function(){
  if(document.hidden)stop();else if(cfg.on)start()});

resize();apply();
window.__neuron={get cfg(){return cfg},set:function(k,v){cfg[k]=v;save();apply()},
  count:function(){return nodes.length}};
})();</script>"""


def strip(html):
    return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?",
                  "", html, flags=re.S)


def inject(html):
    """给一个页面接上神经元背景（可重复执行）。"""
    if "<html" not in html or "</body>" not in html:
        return html
    if "id='nrBtn'" in html or 'id="nrBtn"' in html:
        html = strip(html)
    block = BEGIN + "\n" + JS + "\n" + END + "\n"
    # 不用 html.lower().rfind()：lower() 对个别字符（如 U+0130）会变长，位置错位
    # 会把块插进 </body> 标签内部写坏文件，必须用 re.I 在原串上找。
    m = re.search(r"</body>", html, re.I)
    if m:
        idx = m.start()
        html = html[:idx] + block + html[idx:]
    else:
        html = html + block
    return html


def sweep(dirs=None, verbose=False):
    targets = dirs or [os.path.join(ROOT, p) for p in
                       ("web", "fluent", "python-course-ppt", ".", "android/www")]
    done = 0
    seen = set()
    for d in targets:
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames
                           if x not in (".git", ".cache", "node_modules")]
            for fn in filenames:
                if not fn.endswith(".html"):
                    continue
                p = os.path.join(dirpath, fn)
                rp = os.path.realpath(p)
                if rp in seen:
                    continue
                seen.add(rp)
                with open(p, encoding="utf-8") as f:
                    src = f.read()
                out = inject(src)
                if out != src:
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(out)
                done += 1
    if verbose:
        print(f"神经元背景已注入 {done} 个页面")
    return done


def main(argv):
    if "--check" in argv:
        miss = 0
        total = 0
        for d in ("web", "fluent", "python-course-ppt", ".", "android/www"):
            p = os.path.join(ROOT, d)
            if not os.path.isdir(p):
                continue
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [x for x in dirnames
                               if x not in (".git", ".cache", "node_modules")]
                for fn in filenames:
                    if not fn.endswith(".html"):
                        continue
                    total += 1
                    with open(os.path.join(dirpath, fn), encoding="utf-8") as f:
                        if "neuron:begin" not in f.read():
                            miss += 1
        print(f"页面 {total} 个，缺神经元背景 {miss} 个")
        return 1 if miss else 0
    n = sweep(verbose=True)
    print("覆盖目录：web / fluent / python-course-ppt / . / android/www")
    return 0 if n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
