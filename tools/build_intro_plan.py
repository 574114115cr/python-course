"""入门课周计划页 web/plan.html。

为什么要有它：进阶课有 fluent/web/syllabus.html（标准 14 周 / 轻量 28 周），
入门课却只有一份静态大纲——22 单元 111 节只写「约 29 周」，没有「第 N 周学什么」，
也没有「你现在在第几周、有没有落后」。周次其实早就写在课节数据里（LESSONS 的
W0–W29 字段），只是从没做成页面，所以这里直接复用它，保证数字和课节页一致。

产物：web/plan.html（30 周 × 每周课节直达 + 三阶段 + 进度偏差 + ETA）
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import build_intro_pages as IP          # 复用 SHELL / page() / 样式基线
import lesson_tpl
import site_data

WEB = os.path.join(ROOT, "web")
PER_LESSON_H = 1.5                      # 每节 90 分钟
DAY = 86400000

# 阶段划分：单元 0 环境准备 / 1–11 阶段 1（关卡 1）/ 12–21 阶段 2（关卡 2）
STAGES = [
    (0, 0, "环境准备", "把工具链装好、跑通第一个脚本、学会给代码拍快照（git）。"
     "这一段不产出项目，但没有它后面每一节都卡在环境上。"),
    (1, 11, "阶段 1 · 语言地基", "变量到测试，把 Python 的骨架过一遍。"
     "结束时有<b>关卡 1</b>：过不了就别进项目段，回头补这一段的验收清单。"),
    (12, 21, "阶段 2 · 三个项目", "Pygame 外星人入侵 → 数据可视化 → Django 学习笔记，"
     "最后一个单元是<b>关卡 2</b>综合验收。这一段靠项目把前面的零散知识串起来。"),
]
# 三个大项目落在哪些单元（用于周表上的里程碑标记）
PROJECTS = {
    12: "项目一 · 外星人入侵", 15: "项目二 · 数据可视化", 18: "项目三 · 学习笔记网站",
}


def week_no(label):
    """'W7–W8' → 7（主周次）；跨周的课节算在起始周。"""
    m = re.findall(r"\d+", label or "")
    return int(m[0]) if m else 0


def week_span(label):
    """'W7–W8' → [7, 8]；'W9' → [9]。跨周课节同时占用两个周次。"""
    m = [int(x) for x in re.findall(r"\d+", label or "")]
    if not m:
        return [0]
    return list(range(m[0], m[-1] + 1))


def build_plan():
    lessons = site_data.lessons()          # (unit, span, wk, title, goal, acts, crit)
    rows = []
    for i, (unit, span, wk, title, goal, acts, crit) in enumerate(lessons, 1):
        rows.append({"no": i, "pad": f"{i:02d}", "unit": unit, "wk": week_no(wk),
                     "wk_raw": wk, "title": title, "goal": goal})
    weeks = {}
    for r in rows:
        weeks.setdefault(r["wk"], []).append(r)
    # 周次必须连续：第 8 周只有「W7–W8」这类跨周课节，没有任何以自己的 W8 开头的课，
    # 直接按出现的周次建表会整个漏掉它（漏一行，整张表就少一周）。
    max_wk = max([r["wk"] for r in rows] + [max(week_span(r["wk_raw"])) for r in rows])
    wk_list = list(range(0, max_wk + 1))
    total_weeks = len(wk_list)

    # ── 三阶段统计（节数 / 小时 / 覆盖周次）─────────────────────────
    stage_html = []
    for lo, hi, name, desc in STAGES:
        rs = [r for r in rows if lo <= r["unit"] <= hi]
        ws = sorted({r["wk"] for r in rs})
        h = len(rs) * PER_LESSON_H
        gate = ""
        if hi == 11:
            gate = '<div class="gate">结束接 <a href="gate1.html">关卡 1 验收</a></div>'
        elif hi == 21:
            gate = '<div class="gate">结束接 <a href="gate2.html">关卡 2 验收</a></div>'
        stage_html.append(
            f'<div class="st">'
            f'<div class="sth"><span class="stn">{html.escape(name)}</span>'
            f'<span class="stw">第 {ws[0]}–{ws[-1]} 周</span></div>'
            f'<div class="stm">{len(rs)} 节 · 约 {h:.0f} 小时 · 单元 {lo}–{hi}</div>'
            f'<p class="std">{desc}</p>{gate}</div>')
    stages = "".join(stage_html)

    # ── 每周表 ────────────────────────────────────────────────────
    trs = []
    for w in wk_list:
        rs = weeks.get(w, [])
        # 空周（只有跨周课节）：显示它承接的上周内容，不能留空行
        carry = []
        if not rs:
            carry = [r for r in rows if w in week_span(r["wk_raw"]) and r["wk"] != w]
        shown = rs or carry
        units = sorted({r["unit"] for r in shown})
        unames = " / ".join(f'单元 {u} · {html.escape(lesson_tpl.UNIT_TITLE.get(u, ""))}'
                            for u in units)
        links = "".join(
            f'<a class="lk" href="lessons/{r["pad"]}.html" data-n="{r["no"]}">'
            f'<span class="n">{r["no"]}</span>{html.escape(r["title"])}</a>'
            for r in shown)
        marks = []
        for u in units:
            if u in PROJECTS and PROJECTS[u] not in marks:
                marks.append(PROJECTS[u])
        if 11 in units:
            marks.append("关卡 1")
        if 21 in units:
            marks.append("关卡 2")
        cross = any("–" in (r["wk_raw"] or "") for r in shown)
        mhtml = "".join(f'<span class="mk">{html.escape(m)}</span>' for m in marks)
        note = '<span class="cr">接着上周的跨周内容</span>' if carry else \
            ('<span class="cr">跨周</span>' if cross else "")
        trs.append(
            f'<tr id="w{w}" data-w="{w}"{" class=carry" if carry else ""}>'
            f'<td class="cw"><b>第 {w} 周</b>{note}</td>'
            f'<td class="cu">{unames}</td>'
            f'<td class="cl">{links}</td>'
            f'<td class="cn">{len(shown)} 节</td>'
            f'<td class="ch">{len(shown) * PER_LESSON_H:.1f} h</td>'
            f'<td class="cm">{mhtml}</td></tr>')
    table = "".join(trs)

    body = f"""
<div class="wrap">
  <p class="lead">入门课 <b>{len(rows)} 节课</b>按每周一节一节往下排，共
    <b>{total_weeks} 周</b>（第 0 周是环境准备）。周次直接来自每节课的排期，
    和课节页、讲义页是同一份数据，不会各说各话。</p>

  <div class="you" id="you">
    <div class="yh">你的位置</div>
    <div class="yb" id="youBody">统计中…</div>
  </div>

  <div class="pac">
    <button class="pb on" data-pace="1" type="button">标准 · {total_weeks} 周</button>
    <button class="pb" data-pace="2" type="button">轻量 · {total_weeks * 2} 周</button>
    <span class="pn" id="paceNote"></span>
  </div>

  <h2>三个阶段</h2>
  <div class="sts">{stages}</div>

  <h2>每周安排</h2>
  <div class="tblwrap"><table class="wk">
    <thead><tr><th>周次</th><th>单元</th><th>课节（点进去直接学）</th>
    <th>节数</th><th>课时</th><th>里程碑</th></tr></thead>
    <tbody>{table}</tbody>
  </table></div>

  <div class="foot">
    <a href="review.html">今日复习计划 →</a>
    <a href="lessons/index.html">全部 {len(rows)} 节目录 →</a>
    <a href="../python-course-syllabus.html">课程大纲 →</a>
  </div>
</div>"""

    js = f"""
var TOTAL={len(rows)}, WEEKS={total_weeks}, DAY={DAY};
var WKOF={{{",".join(f'{r["no"]}:{r["wk"]}' for r in rows)}}};
var TITLE={{{",".join(f'{r["no"]}:{json_str(r["title"])}' for r in rows)}}};
var PACE={{1:{total_weeks},2:{total_weeks * 2}}};
var pace=1;
function read(k){{try{{return JSON.parse(localStorage.getItem(k)||'{{}}')}}catch(e){{return {{}}}}}}
function mid(t){{var d=new Date(t);d.setHours(0,0,0,0);return d.getTime()}}
function wkOf(n){{return WKOF[n]||0}}
function done(){{var L=read('lesson-done-v1'),a=[],k;for(k in L){{if(L[k])a.push([+k,L[k]===true?Date.now():L[k]])}}return a}}
function pad(n){{return (n<10?'0':'')+n}}
function fmt(d){{return d.getFullYear()+'-'+(d.getMonth()+1<10?'0':'')+(d.getMonth()+1)+'-'+(d.getDate()<10?'0':'')+d.getDate()}}

function render(){{
  var a=done(), n=a.length, box=document.getElementById('youBody');
  var today=mid(Date.now());
  if(!n){{
    box.innerHTML='<p class="y0">还没有开始。第 1 节是「'+esc(TITLE[1]||'')+
      '」——<a href="lessons/01.html">从第 1 节开始 →</a></p>'+
      '<p class="yt">选一档配速再开工：标准是每周 3–4 节，轻量是每周 1–2 节。'+
      '先选能坚持的那条，再谈进度。</p>';
    paceNote(); return;
  }}
  var wks=PACE[pace];
  // 开课日 = 最早一次完成的时间；用它算「应该到第几周」
  var first=today, last=0, i;
  for(i=0;i<a.length;i++){{var t=a[i][1];if(t<first)first=t;if(t>last)last=t}}
  first=mid(first);
  var days=Math.max(1,Math.round((today-first)/DAY)+1);
  var perWeek=TOTAL/wks;
  var should=Math.min(TOTAL,Math.round(days/7*perWeek));   // 按日历应完成的节数
  var curW=wkOf(n), shouldW=wkOf(should)||0;
  // 近 14 天速度 → ETA
  var cut=today-13*DAY, recent=0, sum=0;
  for(i=0;i<a.length;i++){{if(mid(a[i][1])>=cut){{recent++;}}}}
  var speed=recent/14;
  var left=TOTAL-n, eta='';
  if(speed>0 && left>0){{
    var need=Math.ceil(left/speed);
    eta='<span class="ye">按最近两周的速度（'+speed.toFixed(1)+' 节/天），还剩 '+left+
      ' 节 ≈ '+need+' 天，预计 <b>'+fmt(new Date(today+need*DAY))+'</b> 学完</span>';
  }} else if(left===0){{
    eta='<span class="ye">全部 '+TOTAL+' 节已完成 ✓ 去做 <a href="gate2.html">关卡 2 验收</a></span>';
  }} else {{
    eta='<span class="ye">最近两周没有学习记录，算不出预计完成日期——先补一节再来看</span>';
  }}
  var diff=curW-shouldW, dev='';
  if(diff>=1) dev='<span class="ok">比 '+wks+' 周配速快约 '+diff+' 周</span>';
  else if(diff<=-1) dev='<span class="bad">落后约 '+(-diff)+' 周：本周多补 '+Math.min(left,Math.ceil((-diff)*perWeek))+
    ' 节就能追回</span>';
  else dev='<span class="ok">正好卡在配速上</span>';
  var next=0; for(i=1;i<=TOTAL;i++){{if(!read('lesson-done-v1')[String(i)]){{next=i;break}}}}
  box.innerHTML=
    '<div class="yrow"><span>已学 <b>'+n+'</b> / '+TOTAL+' 节</span>'+
    '<span>实际第 <b>'+curW+'</b> 周</span>'+
    '<span>开课第 '+days+' 天 · 配速应到第 '+shouldW+' 周</span></div>'+
    '<div class="yrow2">'+dev+eta+'</div>'+
    (next?'<p class="yg"><a href="lessons/'+pad(next)+'.html">继续学习：第 '+next+' 节 →</a></p>':'');
  paceNote();
}}
function paceNote(){{
  var wks=PACE[pace], el=document.getElementById('paceNote');
  el.textContent=(pace===1? ('每周 '+(TOTAL/wks).toFixed(1)+' 节 · 约 '+((TOTAL/wks)*1.5).toFixed(1)+' 小时')
                          : ('每周 '+(TOTAL/wks).toFixed(1)+' 节 · 约 '+((TOTAL/wks)*1.5).toFixed(1)+' 小时，配速减半'));
}}
function esc(s){{return String(s).replace(/[&<>]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]}})}}
var bs=document.querySelectorAll('.pb');
for(var i=0;i<bs.length;i++){{bs[i].onclick=function(){{
  for(var j=0;j<bs.length;j++)bs[j].classList.remove('on');
  this.classList.add('on'); pace=+this.getAttribute('data-pace'); render();
}}}}
render();
window.addEventListener('storage',render);"""

    return IP.SHELL.format(title="总课表 · 30 周", css=IP.CSS + PLAN_CSS,
                          body=body, js=js)


def json_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


PLAN_CSS = """
/* 周计划页样式（和 terms/coverage 同壳，只补这一页要用的） */
.wrap{max-width:1180px;margin:0 auto;padding:22px 22px 60px}
.lead{color:var(--muted);font-size:14.5px;line-height:1.8;margin:0 0 18px}
.you{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--p1);
border-radius:12px;padding:16px 18px;margin-bottom:20px}
.yh{font-weight:700;font-size:15px;margin-bottom:8px}
.yrow{display:flex;flex-wrap:wrap;gap:18px;font-size:14px;margin-bottom:8px}
.yrow b{color:var(--p1);font-size:16px}
.yrow2{display:flex;flex-wrap:wrap;gap:14px;font-size:13.5px;margin-top:6px}
.yrow2 .ok{color:var(--p2);font-weight:700}
.yrow2 .bad{color:var(--danger);font-weight:700}
.yrow2 .ye{color:var(--muted)}
.yg{margin:10px 0 0}.yg a{font-weight:700}
.y0{font-size:14px;margin:0 0 6px}.yt{font-size:13.5px;color:var(--muted);margin:0}
.pac{margin:0 0 22px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.pb{font:inherit;font-size:13px;font-weight:700;border:1px solid var(--line);
background:var(--card);color:var(--muted);border-radius:999px;padding:6px 14px;cursor:pointer}
.pb.on{background:var(--p1s);border-color:var(--p1s);color:#fff}
.pn{font-size:12.5px;color:var(--muted)}
h2{font-size:18px;margin:26px 0 12px}
.sts{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.st{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.sth{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.stn{font-weight:700;font-size:15px}
.stw{font-size:12.5px;color:var(--p1);font-weight:700}
.stm{font-size:12.5px;color:var(--muted);margin-top:4px}
.std{font-size:13.5px;line-height:1.75;margin:8px 0 0}
.gate{margin-top:10px;font-size:13px}
.gate a{font-weight:700}
.tblwrap{overflow-x:auto}
.wk{width:100%;border-collapse:collapse;font-size:13.5px}
.wk th,.wk td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
.wk th{background:var(--p1bg);font-size:12.5px}
.cw{white-space:nowrap;font-variant-numeric:tabular-nums}
.cr{display:block;font-size:11px;color:var(--muted)}
.cu{color:var(--muted);font-size:12.5px;min-width:150px}
.cl{display:flex;flex-direction:column;gap:4px;min-width:220px}
.lk{display:flex;gap:6px;font-size:13px}
.lk .n{color:var(--muted);font-variant-numeric:tabular-nums;min-width:20px}
.cn,.ch{white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--muted)}
.wk tr.carry{background:none}
.wk tr.carry .cl{color:var(--muted)}
.mk{display:inline-block;background:var(--p3bg);color:var(--p3ink);
border-radius:5px;padding:1px 7px;font-size:11.5px;font-weight:700;margin:0 4px 4px 0}
.foot{margin-top:24px;display:flex;gap:16px;flex-wrap:wrap;font-size:14px}
@media(max-width:640px){.wrap{padding:16px 14px 48px}.wk{font-size:12.5px}}
@media print{.pac,.foot{display:none}}
"""


def main():
    page = build_plan()
    out = os.path.join(WEB, "plan.html")
    open(out, "w", encoding="utf-8").write(page)
    print(f"周计划页 {len(page) // 1024} KB → web/plan.html")


if __name__ == "__main__":
    main()
    import theme
    theme.sweep([WEB])
