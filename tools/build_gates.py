"""生成关卡验收页：web/gate1.html、web/gate2.html。

内容直接取自讲义原文（单元 11 第六节 / 单元 21 第八节），不另写一份，
避免「关卡标准」出现两个版本。

- 关卡 1：4 条验收，每条带「自检清单」（可直接勾选）+ 参考实现（默认折叠）
- 关卡 2：5 条硬指标，每条带「怎么算达标 / 怎么验证 / 没过怎么办」+ 一条达标勾选
- 勾选状态存 localStorage（gate1-v1 / gate2-v1），顶部显示进度
"""

import glob
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import build_lectures as BL          # noqa: E402
import lesson_tpl as LT              # noqa: E402

OUT = os.path.join(ROOT, "web")

GATES = [
    {
        "n": 1,
        "file": "gate1.html",
        "key": "gate1-v1",
        "md_glob": "course/11-*.md",
        "sec": "## 六、关卡 1 验收标准",
        "head": "关卡 1 · 阶段 1 · 四条硬指标",
        "sub": "合上资料，2 小时内逐条自测。四条全部达标 = 具备「能独立做小项目」的基础。",
        "kind": "checklist",
        "lesson": 63,
        "unit": 11,
        "pass": ("进入阶段 2 · 外星人入侵", "12.html"),
        "pass_note": "四条全绿后进单元 12，开始用 pygame 写游戏。",
    },
    {
        "n": 2,
        "file": "gate2.html",
        "key": "gate2-v1",
        "md_glob": "course/21-*.md",
        "sec": "## 八、关卡 2 验收标准",
        "head": "关卡 2 · 阶段 2 · 五条硬指标",
        "sub": "五条全部达标 = 从「会写代码」到「能交付软件」。验收靠可验证的证据，不靠自我感觉。",
        "kind": "evidence",
        "lesson": 110,
        "unit": 21,
        "pass": ("阶段 3 · 继续进阶", "../python-learning-roadmap.html"),
        "pass_note": "五条全绿后按路线图继续，或直接拿三个项目去投简历。",
    },
]

CSS = """
:root{--bg:#f6f8fb;--card:#fff;--line:#e3e8ef;--text:#16232e;--muted:#5f7183;
--p1:#1f5fa8;--p1bg:#eaf1fb;--p2:#0e9b78;--p2bg:#e8f6f1;--p3:#e08a15;--p3bg:#fdf3e2}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);line-height:1.75;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;
overflow-wrap:anywhere}
a{color:var(--p1);text-decoration:none}a:hover{text-decoration:underline}
code{background:#eef2f7;border-radius:4px;padding:1px 5px;font-size:.92em;
font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
pre{background:#f7f9fc;border:1px solid var(--line);border-radius:9px;padding:12px 14px;
overflow:auto;position:relative;margin:10px 0}
pre code{background:none;padding:0;font-size:13px;line-height:1.62}
.cl{position:absolute;top:6px;right:10px;font-size:11px;color:#8a9aaa;background:#fff;
border:1px solid var(--line);border-radius:5px;padding:1px 7px}
.top{position:sticky;top:0;z-index:40;background:rgba(246,248,251,.96);
backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top-in{max-width:1000px;margin:0 auto;padding:0 22px;height:58px;display:flex;
align-items:center;gap:14px}
.back{font-size:13.5px;color:var(--muted);white-space:nowrap}
.top-in h1{font-size:16px;margin:0;font-weight:700}
.sp{flex:1}
.btn{font-size:12.5px;font-weight:600;color:var(--p1);background:#fff;
border:1px solid var(--line);border-radius:7px;padding:5px 11px}

.hero{max-width:1000px;margin:22px auto 0;padding:0 22px}
.hero h2{font-size:26px;margin:0 0 6px}
.hero p{margin:0;color:var(--muted);font-size:14.5px}
.prog{max-width:1000px;margin:16px auto 0;padding:0 22px;display:flex;gap:14px;
align-items:center}
.track{flex:1;height:9px;background:#e6ecf3;border-radius:99px;overflow:hidden}
.fill{height:100%;width:0;background:linear-gradient(90deg,var(--p1),var(--p2));
border-radius:99px;transition:width .2s}
.pnum{font-size:13.5px;font-weight:700;font-variant-numeric:tabular-nums;
color:var(--p1);white-space:nowrap}

.wrap{max-width:1000px;margin:16px auto 70px;padding:0 22px;display:flex;
flex-direction:column;gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;
padding:18px 20px}
.card.ok{border-color:#bfe3d6;background:#fbfefd}
.ch{display:flex;align-items:flex-start;gap:12px}
.cn{flex:0 0 auto;width:30px;height:30px;border-radius:50%;background:var(--p1);
color:#fff;font-weight:700;font-size:14px;display:flex;align-items:center;
justify-content:center;margin-top:3px}
.card.ok .cn{background:var(--p2)}
.ch h3{font-size:17px;margin:0;line-height:1.5}
.ck{display:flex;gap:10px;align-items:flex-start;margin:9px 0;font-size:14px;
cursor:pointer;padding:7px 10px;border-radius:8px;background:#f7f9fc;
border:1px solid transparent}
.ck:hover{background:#eef4fb}
.ck input{width:17px;height:17px;margin-top:4px;accent-color:var(--p2);cursor:pointer;
flex:0 0 auto}
.ck.on{background:var(--p2bg);border-color:#c8e8dc}
.ck.on span{color:#3b6b5c}
.det{margin:10px 0 0;border-top:1px dashed var(--line);padding-top:8px}
.det summary{cursor:pointer;font-size:13.5px;font-weight:700;color:var(--p1);
list-style:none}
.det summary::-webkit-details-marker{display:none}
.det summary::before{content:"▸ ";font-size:12px}
.det[open] summary::before{content:"▾ "}
.fld{display:flex;gap:10px;margin:8px 0;font-size:14px;align-items:baseline}
.fld b{flex:0 0 84px;font-size:12.5px;color:#fff;background:var(--p1);
border-radius:5px;text-align:center;padding:2px 0;font-weight:700}
.fld.warn b{background:var(--p3)}
.fld.ok b{background:var(--p2)}
.fld p{margin:0}

.after{max-width:1000px;margin:0 auto 60px;padding:0 22px;display:grid;
grid-template-columns:1fr 1fr;gap:14px}
.box{border-radius:14px;padding:16px 18px;border:1px solid var(--line);background:#fff}
.box h4{margin:0 0 6px;font-size:15px}
.box p{margin:0;font-size:13.5px;color:var(--muted)}
.box.pass{background:var(--p2bg);border-color:#c8e8dc}
.box.fail{background:var(--p3bg);border-color:#f0d8a8}

#toTop{position:fixed;right:22px;bottom:22px;width:42px;height:42px;border-radius:50%;
background:#1f5fa8;color:#fff;border:none;font-size:18px;line-height:1;cursor:pointer;
box-shadow:0 6px 18px rgba(20,40,70,.22);opacity:0;pointer-events:none;
transition:opacity .18s;z-index:60}
#toTop.on{opacity:1;pointer-events:auto}
@media print{#toTop{display:none}}
@media(max-width:720px){.after{grid-template-columns:1fr}.top-in{height:auto;padding:10px 14px;
flex-wrap:wrap;gap:8px}.hero,.prog,.wrap,.after{padding:0 14px}}
"""

JS = """
var KEY='__KEY__';
function read(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){return {}}}
var st=read();
var boxes=[].slice.call(document.querySelectorAll('.ck input'));

function paint(){
  var n=0;
  boxes.forEach(function(b){
    var on=!!st[b.dataset.k];
    b.checked=on;
    b.closest('.ck').classList.toggle('on',on);
    if(on) n++;
  });
  document.getElementById('fill').style.width=(boxes.length?n/boxes.length*100:0)+'%';
  document.getElementById('pnum').textContent='已达标 '+n+' / '+boxes.length+' 条';
  // 整卡达标：该卡下所有勾都打上
  document.querySelectorAll('.card').forEach(function(c){
    var all=[].slice.call(c.querySelectorAll('.ck input'));
    var ok=all.length && all.every(function(b){return b.checked});
    c.classList.toggle('ok',!!ok);
  });
}
boxes.forEach(function(b){
  b.addEventListener('change',function(){
    if(this.checked) st[this.dataset.k]=1; else delete st[this.dataset.k];
    try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}
    paint();
  });
});

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


def section(md, start_marker):
    i = md.index(start_marker)
    rest = md[i:]
    m = re.search(r"^##\s+\S", rest[3:], flags=re.M)
    if m:
        return rest[:m.start() + 3]
    return rest


def blocks(sec):
    """按 ### 切块，返回 [(标题, 正文)]。"""
    parts = re.split(r"^###\s+(.+)$", sec, flags=re.M)[1:]
    return [(parts[i].strip(), parts[i + 1]) for i in range(0, len(parts), 2)]


def clean_title(t):
    t = re.sub(r"^[✅☑✔]\s*", "", t)
    return re.sub(r"^(验收|硬指标)\s*\d+[：:]\s*", "", t).strip()


def inline(md_text):
    """单段行内 markdown → HTML（去 <p> 外壳）。"""
    h = BL.convert(md_text.strip())
    h = re.sub(r"^\s*<p>|</p>\s*$", "", h, flags=re.S)
    return h.strip()


def checklist_to_inputs(md_text):
    """把 `- [ ] xxx` 变成可勾选的条目。"""
    items = re.findall(r"^-\s*\[\s*\]\s*(.+)$", md_text, flags=re.M)
    return items


def card_checklist(idx, title, body, key, gate):
    """关卡 1：要求 + 必须包含 + 参考实现（折叠）+ 自检清单（可勾选）。"""
    checks = checklist_to_inputs(body)
    # 去掉自检清单段落，剩下的正文单独渲染
    main = re.split(r"\*\*自检清单\*\*", body)[0]
    code_at = main.find("**参考实现**")
    if code_at > 0:
        prose_md = main[:code_at]
        code_md = main[code_at + len("**参考实现**"):].lstrip("：: \n")
    else:
        prose_md, code_md = main, ""

    prose_md = re.sub(r"[：:]\n(?=[-*]\s)", "：\n\n", prose_md)
    prose = BL.convert(prose_md)
    code = ("<details class='det'><summary>参考实现（先自己写，写完再对照）</summary>"
            + BL.convert(code_md) + "</details>") if code_md.strip() else ""

    ck = "".join(
        f'<label class="ck"><input type="checkbox" data-k="{key}-{idx}-{j}">'
        f'<span>{inline(t)}</span></label>'
        for j, t in enumerate(checks))
    return f"""<section class="card">
  <div class="ch"><span class="cn">{idx}</span><h3>{inline(title)}</h3></div>
  <div class="bd">{prose}</div>
  {code}
  {('<div class="cks">' + ck + '</div>') if checks else ''}
</section>"""


def card_evidence(idx, title, body, key, gate):
    """关卡 2：怎么算达标 / 怎么验证 / 没过怎么办 + 一条达标勾选。"""
    fields = [("怎么算达标", "ok"), ("怎么验证", ""), ("没过怎么办", "warn")]
    rows, rest = [], body
    for name, cls in fields:
        m = re.search(r"\*\*" + name + r"\*\*\s*[：:]\s*(.+?)(?=\*\*(?:怎么算达标|怎么验证|"
                      r"没过怎么办|注意)\*\*|$)", body, flags=re.S)
        if m:
            val = BL.convert(m.group(1).strip())
            rows.append(f'<div class="fld {cls}"><b>{name}</b><div>{val}</div></div>')
            rest = rest.replace(m.group(0), "")
    note = re.search(r"\*\*注意\*\*\s*[：:]\s*(.+?)$", body, flags=re.S)
    if note:
        rows.append(f'<div class="fld warn"><b>注意</b>'
                    f'<div>{BL.convert(note.group(1).strip())}</div></div>')
        rest = rest.replace(note.group(0), "")
    rest = rest.strip()
    tail = BL.convert(rest) if len(re.sub(r"\s", "", rest)) > 4 else ""
    ck = (f'<label class="ck"><input type="checkbox" data-k="{key}-{idx}-0">'
          f'<span>这条已达标（按「怎么验证」实测过，不是凭感觉）</span></label>')
    return f"""<section class="card">
  <div class="ch"><span class="cn">{idx}</span><h3>{inline(title)}</h3></div>
  <div class="bd">{tail}</div>
  {''.join(rows)}
  <div class="cks">{ck}</div>
</section>"""


def build_one(g):
    md = open(glob.glob(os.path.join(ROOT, g["md_glob"]))[0], encoding="utf-8").read()
    sec = section(md, g["sec"])
    bl = blocks(sec)
    assert bl, f"关卡 {g['n']} 没解析到验收条目"

    cards = []
    for i, (t, body) in enumerate(bl, 1):
        title = clean_title(t)
        if g["kind"] == "checklist":
            cards.append(card_checklist(i, title, body, g["key"], g))
        else:
            cards.append(card_evidence(i, title, body, g["key"], g))

    total = len(re.findall(r'data-k="', "".join(cards)))
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(g['head'])}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23e08a15'/%3E%3Ctext x='16' y='22' font-size='15' font-family='monospace' fill='%23fff' text-anchor='middle'%3E★%3C/text%3E%3C/svg%3E">
<style>{CSS}</style>
</head>
<body>
<div class="top"><div class="top-in">
  <a class="back" href="../index.html">← 主页</a>
  <h1>{html.escape(g['head'])}</h1>
  <span class="sp"></span>
  <a class="btn" href="{g['unit']:02d}.html">单元 {g['unit']} 讲义</a>
  <a class="btn" href="lessons/{g['lesson']:02d}.html">第 {g['lesson']} 节课节</a>
  <a class="btn" href="bank.html">题库</a>
</div></div>

<div class="hero">
  <h2>{html.escape(g['head'])}</h2>
  <p>{html.escape(g['sub'])}</p>
</div>

<div class="prog">
  <div class="track"><div class="fill" id="fill"></div></div>
  <span class="pnum" id="pnum">已达标 0 / {total} 条</span>
</div>

<main class="wrap">
{''.join(cards)}
</main>

<div class="after">
  <div class="box pass">
    <h4>全部达标后</h4>
    <p>{html.escape(g['pass_note'])}<br><a href="{g['pass'][1]}">{g['pass'][0]} →</a></p>
  </div>
  <div class="box fail">
    <h4>有条没过怎么办</h4>
    <p>别往下走。回到对应单元把那一条练到能闭卷复现，再回来重测——关卡的意义就是拦住
       「差不多会了」。<a href="../python-learning-roadmap.html">看路线图定位是哪一环</a></p>
  </div>
</div>

<script>{JS.replace('__KEY__', g['key'])}</script>
<script src="media/bgm.js" defer></script>
</body>
</html>
"""
    out = os.path.join(OUT, g["file"])
    open(out, "w", encoding="utf-8").write(page)
    return g["file"], total, len(page)


def build():
    res = []
    for g in GATES:
        res.append(build_one(g))
    return res


if __name__ == "__main__":
    for f, n, size in build():
        print(f"{f}: {n} 条验收勾选，{size} 字节")
