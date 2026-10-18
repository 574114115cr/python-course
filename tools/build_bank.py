"""生成 web/bank.html —— 练习题库（可练的那种）。

改造要点：
1. **答案与解析默认折叠**。原先把答案和题目并排显示，而题库开头自己写着
   「先独立写 → 卡 15 分钟再看答案」——实现和教学法自相矛盾。
2. **每题打标签**：档位（L1–L5）+ 关联单元，支持按档位/单元筛选，
   课节页可以深链到「本单元相关题」（bank.html#u5）。
3. **独立锚点**（#L2-5），题号可直达、可分享。
4. **掌握度记录**（localStorage: bank-v1），显示「已掌握 x/52」。

题目内容仍来自 exercises/题库-从入门到实践.md（唯一内容源）。
"""

import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import build_lectures as BL          # noqa: E402  convert() 复用同一套渲染
import lesson_tpl as LT              # noqa: E402  UNIT_TITLE
import bank_map                       # noqa: E402  题目→单元映射

MD = os.path.join(ROOT, "exercises", "题库-从入门到实践.md")
OUT = os.path.join(ROOT, "web", "bank.html")

LV_NAME = {1: "基础语法", 2: "循环与条件", 3: "函数", 4: "类",
           5: "文件·异常·测试", 6: "项目与工程"}


def parse(md_text):
    """把 md 拆成 [{id, title, body}]，body 内含 题目/答案/解析 三段。"""
    # 先按 `## Lx-y 标题` 切
    parts = re.split(r"^## (L\d-\d+)[\s　]+(.+)$", md_text, flags=re.M)
    out = []
    for i in range(1, len(parts), 3):
        qid, title, body = parts[i], parts[i + 1].strip(), parts[i + 2]
        # 去掉尾部串进来的下一档 h1（如 "# L2 循环与条件"）与分隔线
        # 只切「档位小标题」（# L2 循环与条件…），不能切任意 `# `——
        # 代码块里的 `# views.py` 这类注释也以 # 开头，会把答案和解析一起切掉。
        cut = re.search(r"^#\s+L\d+\s", body, flags=re.M)
        if cut:
            body = body[:cut.start()]
        body = body.replace("---", "\n")
        out.append({"id": qid, "title": title, "body": body.strip()})
    return out


def split_parts(body):
    """拆出 题目 / 答案 / 解析 三段原文。"""
    keys = re.split(r"\*\*(题目|答案|解析)\*\*\s*[:：]?", body)
    seg = {}
    for i in range(1, len(keys), 2):
        seg[keys[i]] = keys[i + 1].strip()
    if "题目" not in seg:                      # 兜底：整段当题目
        seg["题目"] = body
    return seg


def plain(md):
    """粗略去格式，用于搜索索引与字数统计。"""
    t = re.sub(r"```.*?```", " ", md, flags=re.S)
    t = re.sub(r"[#*`>|_\-\[\]()]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def card(q):
    qid, title = q["id"], q["title"]
    lv = int(qid[1])
    unit = bank_map.UNIT_OF.get(qid)
    seg = split_parts(q["body"])

    stem = BL.convert(seg["题目"])
    ans_src = seg.get("答案", "")
    exp_src = seg.get("解析", "")
    ans = BL.convert(ans_src) if ans_src else ""
    exp = ("<div class='exp'><b>解析</b>" + BL.convert(exp_src) + "</div>"
           if exp_src else "")

    ut = html.escape(LT.UNIT_TITLE[unit]) if unit is not None else ""
    key = plain(q["title"] + " " + seg["题目"] + " " + exp_src)[:180].lower()

    return f"""
<article class="q" id="{qid}" data-lv="{lv}" data-u="{unit if unit is not None else ''}"
         data-k="{html.escape(key, quote=True)}">
  <header class="qh">
    <span class="qn">L{lv}</span>
    <h2>{html.escape(title)}</h2>
    <a class="qu" href="{unit:02d}.html" title="回到本单元讲义">单元 {unit} · {ut}</a>
    <div class="st">
      <button type="button" class="sb" data-id="{qid}" data-s="1"
              aria-pressed="false">已掌握</button>
      <button type="button" class="sb" data-id="{qid}" data-s="2"
              aria-pressed="false">待复习</button>
    </div>
  </header>
  <div class="stem">{stem}</div>
  <details class="ans"><summary>看答案与解析 <i>（先自己写，卡住 15 分钟再看）</i></summary>
    <div class="ac">{ans}{exp}</div>
  </details>
</article>""".strip()


CSS = """
:root{--bg:#f6f8fb;--card:#fff;--line:#e3e8ef;--text:#16232e;--muted:#5f7183;
--p1:#1f5fa8;--p1bg:#eaf1fb;--p2:#0e9b78;--p2bg:#e8f6f1;--p3:#e08a15;--p3bg:#fdf3e2}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);line-height:1.75;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}
a{color:var(--p1);text-decoration:none}a:hover{text-decoration:underline}
code{background:#eef2f7;border-radius:4px;padding:1px 5px;font-size:.92em;
font-family:ui-monospace,SFMono-Regular,Consolas,"Courier New",monospace}
pre{background:#f7f9fc;border:1px solid var(--line);border-radius:9px;padding:12px 14px;
overflow:auto;position:relative;margin:10px 0}
pre code{background:none;padding:0;font-size:13px;line-height:1.62}
.cl{position:absolute;top:6px;right:10px;font-size:11px;color:#8a9aaa;
background:#fff;border:1px solid var(--line);border-radius:5px;padding:1px 7px}
pre.broken{border-color:#e8b4b4;background:#fdf6f6}
.badge-broken{margin:-4px 0 10px;padding:7px 11px;border-radius:7px;background:#fdecec;
border:1px solid #f0cccc;font-size:13px;color:#8a3b3b}

/* 顶栏 */
.top{position:sticky;top:0;z-index:40;background:rgba(246,248,251,.96);
backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top-in{max-width:1080px;margin:0 auto;padding:0 22px;height:58px;display:flex;
align-items:center;gap:16px}
.back{font-size:13.5px;color:var(--muted);white-space:nowrap}
.top-in h1{font-size:16px;margin:0;font-weight:700}
.sp{flex:1}
.btn{font-size:12.5px;font-weight:600;color:var(--p1);background:#fff;
border:1px solid var(--line);border-radius:7px;padding:5px 11px}
.btn:hover{background:var(--p1bg);text-decoration:none}

/* 工具条 */
.bar{max-width:1080px;margin:18px auto 0;padding:0 22px;display:flex;flex-wrap:wrap;
gap:10px;align-items:center}
.pills{display:flex;gap:6px;flex-wrap:wrap}
.pills button{font:inherit;font-size:13px;font-weight:600;color:var(--muted);background:#fff;
border:1px solid var(--line);border-radius:999px;padding:5px 13px;cursor:pointer}
.pills button.on{background:var(--p1);border-color:var(--p1);color:#fff}
select,input[type=search]{font:inherit;font-size:13.5px;padding:6px 10px;border-radius:8px;
border:1px solid var(--line);background:#fff;color:var(--text)}
input[type=search]{flex:1;min-width:200px}
.meta{font-size:13px;color:var(--muted);white-space:nowrap}
.meta b{color:var(--p2);font-variant-numeric:tabular-nums}

/* 题目卡 */
.list{max-width:1080px;margin:14px auto 60px;padding:0 22px;display:flex;
flex-direction:column;gap:12px}
.q{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;
scroll-margin-top:80px}
.q.hit{border-color:var(--p3);box-shadow:0 0 0 3px var(--p3bg)}
.q.off{display:none}
.qh{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.qn{font-size:12px;font-weight:700;color:#fff;background:var(--p1);border-radius:5px;
padding:2px 8px;font-variant-numeric:tabular-nums}
.qh h2{font-size:16px;margin:0;font-weight:700}
.qu{font-size:12px;color:var(--muted);background:#f2f6fb;border-radius:6px;padding:2px 8px}
/* 两个状态按钮：已掌握 / 待复习（互斥，再点一次取消） */
.st{margin-left:auto;display:flex;gap:6px;white-space:nowrap}
.sb{font:inherit;font-size:12px;font-weight:700;color:var(--muted);background:#fff;
border:1px solid var(--line);border-radius:999px;padding:3px 11px;cursor:pointer;
transition:all .12s}
.sb:hover{border-color:var(--p1);color:var(--p1)}
.sb[data-s="1"].on{background:var(--p2);border-color:var(--p2);color:#fff}
.sb[data-s="2"].on{background:var(--p3);border-color:var(--p3);color:#fff}
.q.done{border-color:#c8e8dc}
.q.done .qh h2{color:var(--muted)}
.q.review{border-color:#f0d8a8;background:#fffdf8}
.meta .rv{color:var(--p3)}
/* 打印：只留题目与答案，去掉工具栏和按钮 */

#toTop{position:fixed;right:22px;bottom:22px;width:42px;height:42px;border-radius:50%;
background:#1f5fa8;color:#fff;border:none;font-size:18px;line-height:1;cursor:pointer;
box-shadow:0 6px 18px rgba(20,40,70,.22);opacity:0;pointer-events:none;
transition:opacity .18s;z-index:60}
#toTop.on{opacity:1;pointer-events:auto}
@media print{#toTop{display:none}}
@media print{
  .top,.bar,.st,.foot{display:none!important}
  body{background:#fff}
  .list{padding:0;gap:8px}
  .q{break-inside:avoid;page-break-inside:avoid;border:1px solid #ccc;box-shadow:none}
  .ans{display:block}
}
.stem{margin-top:8px}
.stem p{margin:6px 0}
.ans{margin-top:10px;border-top:1px dashed var(--line);padding-top:8px}
.ans summary{cursor:pointer;font-size:13.5px;font-weight:700;color:var(--p1);
list-style:none;display:flex;align-items:center;gap:7px}
.ans summary::-webkit-details-marker{display:none}
.ans summary::before{content:"▸";font-size:12px;color:var(--p1);transition:transform .15s}
.ans[open] summary::before{transform:rotate(90deg)}
.ans summary i{font-style:normal;font-weight:400;color:var(--muted);font-size:12px}
.ac{margin-top:8px}
.exp{margin-top:10px;padding:10px 12px;background:var(--p3bg);border-radius:8px;
font-size:13.5px}
.exp b{color:#8a5a00;margin-right:8px}
.empty{max-width:1080px;margin:40px auto;padding:0 22px;color:var(--muted);display:none}
.foot{max-width:1080px;margin:0 auto 50px;padding:0 22px;font-size:12.5px;color:var(--muted)}
@media(max-width:640px){.top-in{height:auto;padding:10px 14px;flex-wrap:wrap;gap:8px}
.bar,.list,.foot{padding:0 14px}.st{margin-left:0;width:100%}}
"""

JS = r"""
var KEY='bank-v1';
var qs=[].slice.call(document.querySelectorAll('.q'));
var lv='all', unit='all', kw='', only='all';

function readD(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){return {}}}
var st=readD();
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}

/* 状态：1=已掌握，2=待复习，无值=未做 */
/* 旧数据可能是 true / "1" / "2"，统一成 1 / 2 */
function norm(v){
  if(v===true||v===1||v==="1") return 1;
  if(v===2||v==="2"||v==="review") return 2;
  return 0;
}

function paint(){
  var d=0,r=0,u=0;
  qs.forEach(function(q){
    var v=norm(st[q.id]);
    q.classList.toggle('done', v===1);
    q.classList.toggle('review', v===2);
    q.querySelectorAll('.sb').forEach(function(b){
      var on=String(v)===b.getAttribute('data-s');
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on?'true':'false');
    });
    if(v===1) d++; else if(v===2) r++; else u++;
  });
  document.getElementById('mst').innerHTML=
    '已掌握 <b>'+d+'</b> · 待复习 <b class="rv">'+r+'</b> · 未做 '+u;
  document.getElementById('rv').textContent='待复习 '+r;
  apply();
}

function apply(){
  var shown=0;
  qs.forEach(function(q){
    var v=norm(st[q.id]);
    var okL=(lv==='all'||q.dataset.lv===lv);
    var okU=(unit==='all'||q.dataset.u===unit);
    var okK=(!kw||q.dataset.k.indexOf(kw)>-1||q.id.toLowerCase().indexOf(kw)>-1);
    var okS=(only==='all'||(only==='review'&&v===2)||(only==='todo'&&!v));
    var ok=okL&&okU&&okK&&okS;
    q.classList.toggle('off',!ok);
    if(ok) shown++;
  });
  document.getElementById('cnt').textContent=shown+' 题';
  document.getElementById('empty').style.display=shown?'none':'block';
}

document.getElementById('lv').addEventListener('click',function(e){
  var b=e.target.closest('button'); if(!b) return;
  [].slice.call(this.children).forEach(function(x){x.classList.remove('on')});
  b.classList.add('on'); lv=b.dataset.lv; paint();
});
document.getElementById('only').addEventListener('click',function(e){
  var b=e.target.closest('button'); if(!b) return;
  [].slice.call(this.children).forEach(function(x){x.classList.remove('on')});
  b.classList.add('on'); only=b.dataset.only; paint();
});
document.getElementById('unit').addEventListener('change',function(){
  unit=this.value; apply();
});
document.getElementById('q').addEventListener('input',function(){
  kw=this.value.trim().toLowerCase(); apply();
});

document.querySelectorAll('.sb').forEach(function(b){
  b.addEventListener('click',function(){
    var id=this.dataset.id, s=Number(this.dataset.s);
    if(st[id]===s) delete st[id]; else st[id]=s;   // 再点一次取消
    save(); paint();
  });
});

/* 深链：#u5 只看单元 5；#review 只看待复习；#L2-5 定位并展开 */
(function(){
  var h=decodeURIComponent(location.hash.slice(1));
  if(!h) return;
  var m=h.match(/^u(\d+)$/);
  if(m){
    unit=m[1];
    document.getElementById('unit').value=unit;
  } else if(h==='review'){
    only='review';
    var btn=document.querySelector('#only button[data-only="review"]');
    if(btn){ [].slice.call(btn.parentNode.children).forEach(function(x){x.classList.remove('on')});
      btn.classList.add('on'); }
  }
  paint();
  if(!m && h!=='review'){
    var t=document.getElementById(h);
    if(t){
      // 不用 scrollIntoView：原生 hash 跳转 + JS 滚动会互相覆盖，
      // 显式算一次目标位置更稳（留 90px 给吸顶栏）。
      var y=t.getBoundingClientRect().top+window.scrollY-90;
      window.scrollTo({top:y, behavior:'auto'});
      t.classList.add('hit');
      var d=t.querySelector('details'); if(d) d.open=true;
      setTimeout(function(){t.classList.remove('hit')},2200);
    }
  }
})();


/* 长页回到顶部 */
(function(){
  var b=document.createElement('button');
  b.id='toTop'; b.type='button'; b.title='回到顶部'; b.textContent='↑';
  document.body.appendChild(b);
  function sync(){ b.classList.toggle('on', window.scrollY>500); }
  window.addEventListener('scroll',sync,{passive:true}); sync();
  b.addEventListener('click',function(){ window.scrollTo({top:0,behavior:'smooth'}); });
})();

paint();
"""


def build():
    md = open(MD, encoding="utf-8").read()
    qs = parse(md)
    assert len(qs) == bank_map.TOTAL, f"题目数变了：{len(qs)}（预期 %d）" % bank_map.TOTAL + ""
    miss = [q["id"] for q in qs if q["id"] not in bank_map.UNIT_OF]
    assert not miss, f"有题没归到单元：{miss}"

    cards = "\n".join(card(q) for q in qs)

    lv_cnt = {}
    for q in qs:
        lv_cnt[q["id"][1]] = lv_cnt.get(q["id"][1], 0) + 1
    pills = ['<button data-lv="all" class="on">全部 %d</button>' % len(qs)]
    for k in sorted(lv_cnt):
        pills.append(f'<button data-lv="{k}">L{k} {LV_NAME[int(k)]} {lv_cnt[k]}</button>')

    units_used = sorted({bank_map.UNIT_OF[q["id"]] for q in qs})
    opts = ['<option value="all">全部单元</option>']
    for u in units_used:
        n = sum(1 for q in qs if bank_map.UNIT_OF[q["id"]] == u)
        opts.append(f'<option value="{u}">单元 {u} · {html.escape(LT.UNIT_TITLE[u])}'
                    f'（{n} 题）</option>')

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>练习题库 · {len(qs)} 题</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f5fa8'/%3E%3Ctext x='16' y='22' font-size='15' font-family='monospace' fill='%23fff' text-anchor='middle'%3EPy%3C/text%3E%3C/svg%3E">
<style>{CSS}</style>
</head>
<body>
<div class="top"><div class="top-in">
  <a class="back" href="../index.html">← 主页</a>
  <h1>练习题库 · {len(qs)} 题</h1>
  <span class="sp"></span>
  <a class="btn" href="lessons/index.html">按课节学</a>
  <a class="btn" href="ppt/u/index.html">逐节课件</a>
  <a class="btn" href="bank.html">重置筛选</a>
</div></div>

<div class="bar">
  <div class="pills" id="lv">{''.join(pills)}</div>
  <div class="pills" id="only">
    <button data-only="all" class="on">全部状态</button>
    <button data-only="review" id="rv">待复习 0</button>
    <button data-only="todo">未做</button>
  </div>
  <select id="unit">{''.join(opts)}</select>
  <input id="q" type="search" placeholder="搜关键词，如 切片 / 字典 / 异常 / 装饰器">
  <span class="meta" id="cnt">{len(qs)} 题</span>
  <span class="meta" id="mst">已掌握 <b>0</b> · 待复习 <b class="rv">0</b> · 未做 {len(qs)}</span>
</div>

<main class="list">
{cards}
</main>
<div class="empty" id="empty">没有匹配的题目，换个关键词或把筛选调回「全部」。</div>
<div class="foot">
  答案默认折叠：先自己写，卡住 15 分钟再看；看完关掉重写一遍。<br>
  做题时用「待复习」标记卡住的题，下次点这里只看待复习 ·
  <a href="bank.html#review">只看待复习</a> ·
  <a href="../index.html">回主页</a> · <a href="lessons/index.html">课节</a> ·
  <a href="bank.html">题库首页</a>
</div>
<script>{JS}</script>
<script src="media/bgm.js" defer></script>
</body>
</html>
"""
    open(OUT, "w", encoding="utf-8").write(page)
    return len(qs), len(page)


if __name__ == "__main__":
    n, size = build()
    print(f"题库已生成：{n} 题，{size} 字节 -> {os.path.relpath(OUT, ROOT)}")
