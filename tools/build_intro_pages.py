"""入门课补齐两项「进阶课已有」的能力：术语索引 + 覆盖矩阵。

术语索引：从 111 个课节页的正文里抽行内代码（剥掉代码块），按首字母分组，
          每条给 1–4 个课号直达。解决「知道函数名但不知道在第几节」。
覆盖矩阵：从 22 份讲义首部的「对应教材第 X 章」自动解析，生成
          20 章 + 附录 A–E 的逐项对照，外加「多出来的 / 不替代 / 怎么用」。
          数据源是讲义原文，改讲义后重跑即可。
"""

import os
import re
import html
import json
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import site_data                                    # noqa: E402

ROOT = os.path.dirname(HERE)
WEB = os.path.join(ROOT, "web")
LESSONS_DIR = os.path.join(WEB, "lessons")
COURSE = os.path.join(ROOT, "course")

# 这些是语法关键字/太通用的词，做索引没有检索价值
STOP = {
    "python", "Python", "True", "False", "None", "self", "cls", "def", "class",
    "return", "import", "from", "for", "while", "if", "else", "elif", "try",
    "except", "finally", "with", "as", "in", "not", "and", "or", "is", "lambda",
    "yield", "pass", "break", "continue", "global", "nonlocal", "assert", "del",
    "raise", "async", "await", "match", "case", "type", "object", "print",
}

# 附录：教材第 3 版 A–E。课程里真正讲到的只有 A/B/D 的一部分与 E
APPENDIX = [
    ("A", "安装与故障排除", "单元 0", "讲到「装好 Python + 虚拟环境 + 常见安装报错」"
                                "（PATH、pip 装错解释器、PowerShell 执行策略、文件名撞标准库、"
                                "中文编码共 8 条），不含三平台逐步截图"),
    ("B", "文本编辑器与 IDE", "单元 0", "VS Code 为主，另给出 IDLE / Thonny / PyCharm / "
                                   "Jupyter / 在线编辑器六选一对比表与选型建议"),
    ("C", "寻求帮助", "单元 11 + 求助手册页", "独立成节：怎么搜、最小可复现（MRE）、提问模板、"
                                      "去哪问、问 AI 的四条纪律；help.html 提供报错提取器与模板复制"),
    ("D", "使用 Git 进行版本控制", "单元 0", "讲 init/add/commit/checkout 四条命令，"
                                        "不含分支、合并、远程协作"),
    ("E", "部署故障排除", "单元 20", "独立成节：看日志、8 条症状对照表、WhiteNoise 静态文件、"
                                "四步排查法与先回滚再修"),
]


def unit_titles():
    """从讲义 H1 取单元标题（文件名去掉「单元N-」会丢标点，不能用作标题）。"""
    out = {}
    for f in os.listdir(COURSE):
        m = re.match(r"^(\d\d)-单元(\d+)-.*\.md$", f)
        if not m:
            continue
        no = int(m.group(2))
        with open(os.path.join(COURSE, f), encoding="utf-8") as fh:
            first = fh.readline().strip()
        t = first.lstrip("# ").strip()
        t = re.sub(r"^单元\s*\d+\s*[：:]\s*", "", t)
        out[no] = t
    return out


def chapter_line():
    """每份讲义首部的「对应教材第 X 章…」原文 → {unit: 原文}。"""
    out = {}
    for f in os.listdir(COURSE):
        m = re.match(r"^(\d\d)-单元(\d+)-.*\.md$", f)
        if not m:
            continue
        no = int(m.group(2))
        with open(os.path.join(COURSE, f), encoding="utf-8") as fh:
            head = [next(fh, "") for _ in range(12)]
        line = ""
        for ln in head:
            if "教材第" in ln:
                line = ln.strip().lstrip("> ").strip()
                break
        out[no] = line
    return out


def unit_stats():
    """每单元的 可运行示例 / 练习 / 正文字数，用讲义原文统计。"""
    out = {}
    for f in os.listdir(COURSE):
        m = re.match(r"^(\d\d)-单元(\d+)-.*\.md$", f)
        if not m:
            continue
        no = int(m.group(2))
        s = open(os.path.join(COURSE, f), encoding="utf-8").read()
        out[no] = {
            "examples": len(re.findall(r"^### 示例 \d+", s, re.M)),
            "exercises": len(re.findall(r"^### 参考答案 \d+-\d+", s, re.M)),
            "chars": len(re.sub(r"\s+", "", re.sub(r"```.*?```", "", s, flags=re.S))),
            "code": len(re.findall(r"^```python", s, re.M)),
        }
    return out


# ── 术语索引 ────────────────────────────────────────────────────────────
def local_names(meta):
    """代码块里被赋值的名字（x = / for x in / as x）→ 视为局部变量，不做术语。

    「只收正文里出现过的名字」还不够：讲义正文常写「把 `age` 加一」，
    这类局部变量进索引只会稀释检索价值。函数名、类名、方法名不在此列。
    """
    bad = set()
    for m in meta:
        p = os.path.join(LESSONS_DIR, f"{m['no']:02d}.html")
        s = open(p, encoding="utf-8").read()
        for block in re.findall(r"<pre\b.*?</pre>", s, flags=re.S):
            txt = html.unescape(re.sub(r"<[^>]+>", "", block))
            bad.update(re.findall(r"^\s*([A-Za-z_]\w*)\s*(?:=[^=]|,\s*\w+\s*=)", txt, re.M))
            bad.update(re.findall(r"\bfor\s+([A-Za-z_]\w*)\s+in\b", txt))
            bad.update(re.findall(r"\bas\s+([A-Za-z_]\w*)\s*:", txt))
    return bad


def build_terms(meta):
    local = local_names(meta)
    index = {}
    for m in meta:
        no = m["no"]
        p = os.path.join(LESSONS_DIR, f"{no:02d}.html")
        s = open(p, encoding="utf-8").read()
        body = s.split('<main class="main">', 1)[-1].split("</main>", 1)[0]
        body = re.sub(r"<pre\b.*?</pre>", "", body, flags=re.S)      # 代码块整段不要
        for raw in re.findall(r"<code\b[^>]*>(.*?)</code>", body, flags=re.S):
            t = html.unescape(raw).strip()
            t = re.sub(r"^([A-Za-z_][A-Za-z0-9_.]*)\s*\(\s*\)$", r"\1", t)
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", t):
                continue
            if len(t) < 2 or t in STOP or t.endswith("."):
                continue
            if re.search(r"\.(py|html|css|js|json|txt|md|db|sqlite3)$", t, re.I):
                continue                                   # 文件名不是术语
            if t in local and "__" not in t:
                continue                                   # 代码块里被赋值的局部变量
            if re.match(r"^[a-z]\.[A-Za-z_]", t):        # a.append 这类实例用法
                continue
            if "." in t and (t.split(".")[0] in local or
                             t.split(".")[0] in ("self", "cls")):   # dates.append / self.x.y
                continue
            if "__" in t and not t.startswith("__"):
                continue
            index.setdefault(t, []).append(no)

    groups = {}
    for t, nos in index.items():
        key = t[0].upper() if t[0].isalpha() else "_"
        groups.setdefault(key, []).append((t, sorted(set(nos))))

    order = sorted(k for k in groups if k != "_") + (["_"] if "_" in groups else [])
    blocks = []
    for k in order:
        items = sorted(groups[k], key=lambda x: x[0].lower())
        lis = "".join(
            f'<li data-t="{html.escape(t.lower())}"><code>{html.escape(t)}</code>'
            + "".join(f'<a href="lessons/{n:02d}.html">{n}</a>' for n in nos[:4])
            + (f"<span>+{len(nos) - 4}</span>" if len(nos) > 4 else "")
            + "</li>" for t, nos in items)
        blocks.append(f'<div class="ig"><div class="ih">{k}</div><ul>{lis}</ul></div>')

    body = f"""<div class="wrap">
  <div class="hero">
    <span class="bdg">INDEX · 术语索引</span>
    <h1>术语索引 · {len(index)} 条</h1>
    <p>从 {len(meta)} 节课的正文里自动抽出的标识符。右边的数字是<b>课号</b>，点进去就是讲解位置。
       相当于教材末尾的索引，但每条都指向一节 90 分钟的课。只收正文里出现过的名字，
       代码块里的局部变量不收。</p>
    <div class="st">
      <div><b>{len(index)}</b><span>条术语</span></div>
      <div><b>{len(meta)}</b><span>节课</span></div>
      <div><b>{len(order)}</b><span>个字母组</span></div>
    </div>
  </div>
  <div class="fbar"><input id="tq" type="search" autocomplete="off" spellcheck="false"
    placeholder="输入过滤：append、input、sorted、__init__ …" aria-label="术语过滤">
    <span id="tqn"></span></div>
  <div class="idx" id="idx">{''.join(blocks)}</div>
  <p class="empty" id="tempty">没有匹配的术语</p>
  <div class="foot">
    <a href="../index.html">主页</a> ·
    <a href="lessons/index.html">课程目录</a> ·
    <a href="coverage.html">覆盖与自足性</a> ·
    <a href="bank.html">题库</a> ·
    <a href="review.html">复习计划</a>
  </div>
</div>"""
    return page("术语索引", body, TERMS_JS)


TERMS_JS = """(function(){
  var q=document.getElementById('tq'), items=[].slice.call(document.querySelectorAll('#idx li'));
  var groups=[].slice.call(document.querySelectorAll('.ig')), empty=document.getElementById('tempty');
  var cnt=document.getElementById('tqn');
  function run(){
    var v=(q.value||'').trim().toLowerCase(), n=0;
    items.forEach(function(li){
      var ok=!v||li.dataset.t.indexOf(v)>=0;
      li.style.display=ok?'':'none'; if(ok) n++;
    });
    groups.forEach(function(g){
      var any=[].some.call(g.querySelectorAll('li'),function(li){return li.style.display!=='none'});
      g.style.display=any?'':'none';
    });
    empty.style.display=n?'none':'block';
    cnt.textContent=v?('匹配 '+n+' 条'):'';
  }
  q.addEventListener('input',run); run();
  document.addEventListener('keydown',function(e){
    if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus();}
  });
})();"""


# ── 覆盖矩阵 ────────────────────────────────────────────────────────────
def build_coverage(meta):
    titles = unit_titles()
    lines = chapter_line()
    stats = unit_stats()
    units = sorted(titles)

    # 章节 → 单元（从原文里抓所有「第 X 章」）
    ch_units = {}
    for u in units:
        for ch in re.findall(r"第\s*(\d+)\s*章", lines.get(u, "")):
            ch_units.setdefault(int(ch), set()).add(u)

    # 章名以讲义原文里的「」为准，取不到就用通用名
    ch_names = {}
    for u in units:
        for ch, name in re.findall(r"第\s*(\d+)\s*章\s*「([^」]+)」", lines.get(u, "")):
            ch_names.setdefault(int(ch), name)

    rows = []
    for ch in range(1, 21):
        us = sorted(ch_units.get(ch, []))
        if not us:
            rows.append(f"<tr class='miss'><td>{ch}</td><td>{html.escape(ch_names.get(ch, '—'))}</td>"
                        f"<td>—</td><td><span class='tag no'>未覆盖</span></td></tr>")
            continue
        links = " ".join(f"<a href='{u:02d}.html'>单元 {u}</a>" for u in us)
        n_units = len(us)
        tag = ("<span class='tag ok'>精讲</span>" if n_units == 1
               else f"<span class='tag part'>拆成 {n_units} 个单元</span>")
        rows.append(f"<tr><td>{ch}</td><td>{html.escape(ch_names.get(ch, '—'))}</td>"
                    f"<td>{links}</td><td>{tag}</td></tr>")

    ap_rows = "".join(
        f"<tr><td>{k}</td><td>{html.escape(name)}</td><td>{html.escape(where)}</td>"
        f"<td class='s'>{html.escape(note)}</td></tr>"
        for k, name, where, note in APPENDIX)

    # 每单元规模表
    urows = []
    for u in units:
        s = stats.get(u, {})
        lo, hi = site_data.unit_lesson_range(u)
        urows.append(
            f"<tr id='u{u}'><td><a href='{u:02d}.html'>单元 {u}</a></td><td>{html.escape(titles[u])}</td>"
            f"<td class='n'>{hi - lo + 1}</td><td class='n'>{s.get('examples', 0)}</td>"
            f"<td class='n'>{s.get('exercises', 0)}</td>"
            f"<td class='n'>{s.get('chars', 0) // 1000}k</td>"
            f"<td class='s'>{html.escape(lines.get(u, '') or '—')}</td></tr>")

    total_chars = sum(v["chars"] for v in stats.values())
    total_ex = sum(v["examples"] for v in stats.values())
    total_qs = sum(v["exercises"] for v in stats.values())
    n_lessons = len(meta)
    covered = sum(1 for ch in range(1, 21) if ch_units.get(ch))

    body = f"""<div class="wrap">
  <div class="hero">
    <span class="bdg">COVERAGE · 覆盖与自足性</span>
    <h1>教材 {covered}/20 章 + 附录 A–E，逐项对照</h1>
    <p>这张表回答一个问题：<b>不翻原书，这套课够不够？</b>
       左边是教材章节，右边是本课程对应的单元。表格由讲义首部的「对应教材第 X 章」
       自动生成，改讲义后重跑即可，不会出现「说覆盖了其实没讲」。</p>
    <div class="st">
      <div><b>{n_lessons}</b><span>节课</span></div>
      <div><b>{total_ex}</b><span>可运行示例</span></div>
      <div><b>{total_qs}</b><span>道练习（带答案）</span></div>
      <div><b>{total_chars // 1000}k</b><span>正文字数</span></div>
    </div>
  </div>

  <h2>一、教材章节对照</h2>
  <p class="sub">「拆成 N 个单元」表示一章被切成多节讲，不是漏讲；点单元号可直达讲义。</p>
  <div class="tblwrap"><table class="cov">
    <thead><tr><th>章</th><th>标题</th><th>对应单元</th><th>覆盖方式</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>

  <h2>二、附录对照</h2>
  <p class="sub">附录最容易「以为讲了其实只讲了一条路径」，所以逐条写清讲到什么程度。</p>
  <div class="tblwrap"><table class="cov">
    <thead><tr><th>附录</th><th>标题</th><th>位置</th><th>讲到的程度</th></tr></thead>
    <tbody>{ap_rows}</tbody>
  </table></div>

  <h2>三、每个单元的规模</h2>
  <p class="sub">示例数与练习数都从讲义原文里数出来，不是估算。练习全部带参考答案。</p>
  <div class="tblwrap"><table class="cov">
    <thead><tr><th>单元</th><th>标题</th><th>节</th><th>示例</th><th>练习</th><th>正文</th>
      <th>对应教材</th></tr></thead>
    <tbody>{''.join(urows)}</tbody>
  </table></div>

  <h2>四、这套课比原书多出来的</h2>
  <div class="cards">
    <div class="cb"><b>111 节 × 90 分钟的切分</b>
      <p>原书按章，一章 30–60 页。这里切成 90 分钟能上完的课节，每节四段：
      复盘 10 · 讲解 30 · 实操 40 · 讲评 20，并写明「这节课的产出是什么」。</p></div>
    <div class="cb"><b>{total_qs} 道分档练习 + 全部答案</b>
      <p>基础档 / 进阶档分开，答案不是代码片段而是可运行文件，附「为什么这样写」。
      另有 <a href="bank.html">120 题题库</a>（L1–L6）可标记已掌握 / 待复习。</p></div>
    <div class="cb"><b>关卡验收</b>
      <p><a href="gate1.html">关卡 1</a>（基础语法，19 项）与 <a href="gate2.html">关卡 2</a>（项目，5 项）
      都是可勾选的清单，勾满才算过，不是「大概会了」。</p></div>
    <div class="cb"><b>复习排程</b>
      <p><a href="review.html">艾宾浩斯 6 轮复习</a>按课节自动排期，
      与题库的「待复习」标记联动。原书没有这一层。</p></div>
    <div class="cb"><b>可检索</b>
      <p><a href="terms.html">术语索引</a>把正文里的标识符全部抽出来并按字母分组，
      配全站搜索与深链（<code>#u6</code> / <code>#L2-5</code>），比翻纸质索引快。</p></div>
    <div class="cb"><b>离线与投屏</b>
      <p>每单元 10 页课件、整站可离线（PWA / 便携包 / 安卓 APK），
      不依赖网络，也不依赖某个阅读器。</p></div>
  </div>

  <h2>五、这套课不替代的部分</h2>
  <div class="cards">
    <div class="cb"><b>1. 三个项目的完整演进过程</b>
      <p>原书第 12–20 章是「一个项目从零长到能部署」的连续叙事，代码在几十页里逐步修改。
      本课程按单元拆开讲每个机制，项目线仍在（射击游戏 → 数据可视化 → Django 博客），
      但「同一个文件改了 15 次的中间状态」需要回原书看。</p></div>
    <div class="cb"><b>2. 附录里的平台细节</b>
      <p>三平台安装截图、其他编辑器配置、Git 分支与远程协作、部署服务商的控制台界面——
      这些会随版本变化，课程只给一条能跑通的路径。</p></div>
    <div class="cb"><b>3. 纸质书的查阅手感</b>
      <p>术语索引与搜索能替代「翻到某页」，但替代不了在页边写批注。
      习惯纸书的话，把本课程当「讲解版」，原书当「手册」。</p></div>
  </div>

  <h2>六、怎么用</h2>
  <div class="cards">
    <div class="cb"><b>没有原书</b>
      <p>按 <a href="lessons/index.html">课程目录</a> 顺序走：讲义 → 动手练习 → 对照参考答案 →
      单元验收自测。每单元学完做一次 <a href="bank.html">题库</a> 对应单元，
      再按 <a href="review.html">复习计划</a> 滚动复习。</p></div>
    <div class="cb"><b>有原书</b>
      <p>把本表当索引：先看课节，再回原书对应章读长段落。
      本课程讲得比原书细的地方是「报错怎么读」与「练习答案」；
      原书更强的地方是项目连续性与平台截图。</p></div>
  </div>

  <div class="foot">
    <a href="../index.html">主页</a> ·
    <a href="lessons/index.html">课程目录</a> ·
    <a href="terms.html">术语索引</a> ·
    <a href="bank.html">题库</a> ·
    <a href="review.html">复习计划</a>
  </div>
</div>"""
    return page("覆盖与自足性", body, "")


# ── 外壳 ────────────────────────────────────────────────────────────────
CSS = """
.wrap{max-width:1100px;margin:0 auto;padding:0 22px 70px}
.hero{background:linear-gradient(135deg,#f4f8fd,#eef4fb);border:1px solid var(--line);
border-radius:16px;padding:34px 36px;margin:26px 0 22px}
.hero .bdg{display:inline-block;font-size:11px;font-weight:700;letter-spacing:1.2px;
color:var(--p1);background:var(--p1bg);border-radius:20px;padding:3px 10px;margin-bottom:10px}
.hero h1{margin:0 0 10px;font-size:clamp(22px,3.4vw,30px);line-height:1.3}
.hero p{margin:0;font-size:14px;color:#41505f;line-height:1.8;max-width:74ch}
.hero .st{display:flex;gap:26px;flex-wrap:wrap;margin-top:18px}
.hero .st div{display:flex;flex-direction:column}
.hero .st b{font-size:20px;color:var(--p1)}
.hero .st span{font-size:11.5px;color:var(--muted)}
h2{font-size:17px;margin:34px 0 8px}
h2::before{content:"";display:inline-block;width:4px;height:15px;background:var(--p1);
border-radius:2px;margin-right:9px;vertical-align:-2px}
.sub{margin:0 0 12px;font-size:13px;color:var(--muted);line-height:1.7}
.fbar{display:flex;gap:10px;align-items:center;margin:0 0 18px}
.fbar input{flex:1;font:inherit;font-size:14px;padding:11px 14px;border:1px solid var(--line);
border-radius:10px;background:#fff}
.fbar input:focus{outline:none;border-color:var(--p1);box-shadow:0 0 0 3px rgba(31,95,168,.1)}
.fbar span{font-size:12px;color:var(--muted);white-space:nowrap}
.idx{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(270px,100%),1fr));gap:14px}
.ig{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.ih{font-size:12px;font-weight:700;color:var(--p1);letter-spacing:1px;margin-bottom:8px}
.ig ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:3px}
.ig li{display:flex;align-items:center;gap:6px;font-size:12.5px;flex-wrap:wrap}
.ig code{background:#f2f6fb;border-radius:4px;padding:1px 5px;font-size:12px}
.ig a{font-size:11px;font-weight:700;color:var(--p1);text-decoration:none;
background:var(--p1bg);border-radius:4px;padding:1px 5px}
.ig a:hover{background:#dbe9f8}
.ig span{font-size:10.5px;color:var(--muted)}
.empty{display:none;text-align:center;color:var(--muted);font-size:13px;padding:30px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(300px,100%),1fr));gap:14px}
.cb{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.cb b{display:block;font-size:14px;margin-bottom:6px}
.cb p{margin:0;font-size:13px;color:#44515e;line-height:1.75}
.tblwrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff}
table.cov{border-collapse:collapse;width:100%;min-width:660px;font-size:13px}
table.cov th{background:#f5f8fc;text-align:left;padding:9px 12px;font-size:12px;
color:var(--muted);font-weight:700;border-bottom:1px solid var(--line);white-space:nowrap}
table.cov td{padding:9px 12px;border-bottom:1px solid #eef2f6;vertical-align:top;line-height:1.65}
table.cov tr:last-child td{border-bottom:none}
table.cov td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
table.cov td.s{font-size:12px;color:#5a6875}
table.cov tr[id]{scroll-margin-top:70px}
table.cov tr:target td{background:#f3f8ff}
table.cov tr.miss td{background:#fdf7f7;color:#8a5a5a}
table.cov a{color:var(--p1);text-decoration:none;font-weight:600}
table.cov a:hover{text-decoration:underline}
.tag{display:inline-block;font-size:11px;font-weight:700;border-radius:4px;padding:1px 7px;white-space:nowrap}
.tag.ok{background:#e6f6f0;color:#0b6e54}
.tag.part{background:#fdf3e2;color:#8a5a00}
.tag.no{background:#fdeaea;color:#a33}
.foot{margin-top:34px;padding-top:16px;border-top:1px solid var(--line);font-size:12.5px;
color:var(--muted);display:flex;gap:6px;flex-wrap:wrap}
@media(max-width:640px){
 .hero{padding:24px 20px}
 .wrap{padding:0 14px 50px}
 .hero .st{gap:18px}
}
"""

SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Python 入门课</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f5fa8'/%3E%3Ctext x='16' y='22' font-size='15' font-family='monospace' fill='%23fff' text-anchor='middle'%3EPy%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="css/unit.css">
<style>{css}</style>
</head>
<body>
<div class="top"><div class="top-in">
  <a class="back" href="../index.html">← 主页</a>
  <h1>{title}</h1>
  <span class="sp"></span>
  <a class="ppt" href="lessons/index.html">课程目录</a>
</div></div>
{body}
<script>{js}</script>
<script src="media/bgm.js" defer></script>
</body>
</html>"""


# ── 排错速查 ────────────────────────────────────────────────────
# 异常类型速查：新手在阶段 1、2 里真正会遇到的那些。
# 「先查这里」一栏是刻意写的：报错后第一件事该看什么，比解释原理更有用。
EXC_TABLE = [
    ("SyntaxError", "语法不合规则，代码没跑起来",
     "def/if/for 行末漏冒号；括号没配对；用了中文标点",
     "看报错箭头 ^ 指的那一行的**上一行**"),
    ("IndentationError", "缩进层级不对",
     "该缩进的没缩进；混用空格和 Tab；缩进格数不一致",
     "4 个空格一级；让编辑器把 Tab 自动转空格"),
    ("TabError", "空格和 Tab 混着用了",
     "从网页复制代码进来最容易中招",
     "整段重新缩进（VS Code：全选 → 转换缩进为空格）"),
    ("NameError", "这个名字没定义过",
     "拼写错 / 大小写错 / 定义写在使用之后",
     "搜索这个名字是在哪定义的，看顺序对不对"),
    ("UnboundLocalError", "函数里先用了、后面才赋值",
     "函数内给全局变量赋值却没写 global",
     "要么加 global，要么改成参数传进去"),
    ("TypeError", "类型不对",
     "str 和 int 相加；input() 没转类型；对 None 调用方法",
     "print 出两边的 type()，看哪个不是你以为的类型"),
    ("ValueError", "类型对，但值不合法",
     "int('abc')；int('3.5')；列表里没有要找的值却用了 index()",
     "把那个值 print 出来看一眼（常用 repr()）"),
    ("IndexError", "下标越界",
     "空列表还取 [0]；循环到 len 却写成了 len+1",
     "print(len(列表)) 和你用的下标"),
    ("KeyError", "字典里没有这个键",
     "键名拼错；数据源里有的项缺这个字段",
     "print(字典.keys()) 看看实际有哪些键"),
    ("AttributeError", "对象没有这个属性/方法",
     "方法名拼错；把字符串当列表用；Python 版本太低没这个方法",
     "print(type(对象)) 确认它到底是个啥"),
    ("ZeroDivisionError", "除以 0",
     "分母是变量，某次刚好是 0（常见于求平均）",
     "先判断分母：if len(x) else 给个默认值"),
    ("FileNotFoundError", "文件不存在",
     "相对路径的基准目录不是你以为的那个",
     "print(Path.cwd()) 与 Path('文件').exists()"),
    ("PermissionError", "没权限读写",
     "Windows 上文件被别的程序开着；往系统目录写",
     "关掉占用文件的程序；换到用户目录下写"),
    ("ModuleNotFoundError", "import 的模块找不到",
     "没装；装到了另一个解释器；自己的文件名撞了标准库名",
     "用 python -m pip install；检查文件名别叫 random.py"),
    ("UnicodeDecodeError", "读文件时编码对不上",
     "文件是 UTF-8 却按 GBK 读（Windows 默认）",
     "open(..., encoding='utf-8') 永远显式写编码"),
    ("UnicodeEncodeError", "输出时编码对不上",
     "Windows 控制台是 GBK，print 中文就崩",
     "终端执行 chcp 65001，或写文件代替 print"),
    ("RecursionError", "递归没停下来",
     "递归函数忘了写终止条件，或条件永远不成立",
     "确认每次递归都在接近终止条件"),
    ("StopIteration", "迭代器被手动 next() 取空了",
     "一般不会出现——出现了说明用错了迭代方式",
     "改用 for 循环，别手动 next()"),
    ("400 Bad Request（Django）", "Django 拒了这个请求的 Host",
     "ALLOWED_HOSTS 里没有当前访问的域名",
     "把域名加进 ALLOWED_HOSTS（见单元 20）"),
    ("DisallowedHost（Django）", "同上，只是触发点不同",
     "线上部署后第一件事就是这个",
     "同上；看日志确认实际传进来的 Host 是什么"),
]


def collect_errors():
    """从 22 份讲义的「常见错误清单」段抽条目（数据源是讲义，改讲义后重跑即可）。"""
    items = []
    for f in sorted(os.listdir(COURSE)):
        if not f.endswith(".md"):
            continue
        try:
            u = int(f.split("-")[0])
        except ValueError:
            continue
        s = open(os.path.join(COURSE, f), encoding="utf-8").read()
        m = re.search(r"^## [一二三四五六七八九十]+、常见错误清单.*$", s, re.M)
        if not m:
            continue
        seg = s[m.end():].split("\n## ")[0]
        for part in re.split(r"^### ", seg, flags=re.M)[1:]:
            lines = part.split("\n")
            head = re.sub(r"^错误\s*\d+[：:]\s*", "", lines[0]).strip().strip("`").strip()
            body = "\n".join(lines[1:]).strip()
            if head:
                items.append((u, head, body))
    return items


def build_debug(meta, bl):
    """排错速查：异常类型速查表 + 22 个单元的全部错误清单（可搜索）。"""
    utitles = unit_titles()
    rows = "".join(
        "<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(a), html.escape(b), html.escape(c), html.escape(d))
        for a, b, c, d in EXC_TABLE)

    items = collect_errors()
    units = sorted({u for u, _, _ in items})
    cards = []
    for u, head, body in items:
        try:
            html_body = bl.convert(body)
        except Exception:
            html_body = "<p>" + html.escape(body) + "</p>"
        cards.append(
            '<details class="ec" data-u="{}" data-t="{}"><summary><span class="ub">单元 {}</span>'
            '<b>{}</b></summary><div class="eb">{}</div></details>'.format(
                u, html.escape(head.lower()), u, html.escape(head), html_body))
    opts = "".join('<option value="{}">单元 {} · {}</option>'.format(
        u, u, html.escape(utitles.get(u, ""))) for u in units)

    body = """<div class="wrap">
  <div class="hero">
    <span class="bdg">DEBUG · 排错速查</span>
    <h1>报错了怎么办 · {n} 条实战清单</h1>
    <p>上面那张表是「异常名 → 先查哪里」，下面是 22 个单元讲义里
       <b>常见错误清单</b>的全部条目，可搜索、可按单元筛选。
       数据源就是讲义本身，改了讲义重跑构建即同步。</p>
    <div class="st">
      <div><b>{n}</b><span>条错误清单</span></div>
      <div><b>{ne}</b><span>种异常类型</span></div>
      <div><b>{nu}</b><span>个单元</span></div>
    </div>
  </div>

  <h2>先认异常名：它直接告诉你问题属于哪一类</h2>
  <div class="tblwrap"><table class="exc">
    <thead><tr><th>异常</th><th>含义</th><th>最常见的原因</th><th>先查这里</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>

  <h2>全部错误清单</h2>
  <div class="fbar">
    <input id="dq" type="search" autocomplete="off" spellcheck="false"
      placeholder="搜索：缩进、KeyError、encoding、ALLOWED_HOSTS …" aria-label="错误过滤">
    <select id="du" aria-label="按单元筛选"><option value="">全部单元</option>{opts}</select>
    <span id="dqn"></span>
  </div>
  <div id="dlist">{cards}</div>
  <p class="empty" id="dempty">没有匹配的条目</p>
  <div class="foot">
    <a href="../index.html">主页</a> ·
    <a href="lessons/index.html">课程目录</a> ·
    <a href="help.html">求助手册</a> ·
    <a href="terms.html">术语索引</a> ·
    <a href="coverage.html">覆盖与自足性</a>
  </div>
</div>
<style>
.fbar{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:12px 0 16px}}
.fbar input[type=search]{{flex:1 1 260px;min-width:0}}
.fbar select{{height:34px;border:1px solid var(--line);border-radius:8px;
background:var(--card);color:var(--text);font:inherit;font-size:13px;padding:0 8px}}
.ec{{border:1px solid var(--line);border-radius:10px;margin:8px 0;background:var(--card)}}
.ec summary{{cursor:pointer;padding:11px 14px;font-size:14px;line-height:1.6;
display:flex;gap:10px;align-items:baseline}}
.ec summary b{{font-weight:600}}
.ec .ub{{flex:0 0 auto;font-size:11px;font-weight:700;color:var(--p1);
background:var(--p1bg);border-radius:20px;padding:2px 8px}}
.ec .eb{{padding:0 16px 14px;font-size:13.5px;line-height:1.85;color:var(--text)}}
.ec .eb p{{margin:6px 0}}
.ec .eb pre{{margin:8px 0}}
table.exc td{{font-size:13px;line-height:1.7;vertical-align:top}}
table.exc td:first-child{{white-space:nowrap}}
</style>""".format(n=len(items), ne=len(EXC_TABLE), nu=len(units),
                   rows=rows, opts=opts, cards="".join(cards))

    js = """
var q=document.getElementById('dq'),sel=document.getElementById('du'),
    list=document.getElementById('dlist'),n=document.getElementById('dqn'),
    emp=document.getElementById('dempty');
function filt(){
  var s=q.value.trim().toLowerCase(),u=sel.value,c=0;
  [].forEach.call(list.children,function(d){
    var ok=(!s||d.dataset.t.indexOf(s)>=0||d.textContent.toLowerCase().indexOf(s)>=0)
           &&(!u||d.dataset.u===u);
    d.style.display=ok?'':'none'; if(ok)c++;
  });
  n.textContent=c+' / '+list.children.length;
  emp.style.display=c?'none':'';
}
q.addEventListener('input',filt); sel.addEventListener('change',filt); filt();
"""
    return page("排错速查", body, js)


def build_help(meta):
    """求助手册：搜索、最小可复现、提问模板、去哪问、AI 怎么用。"""
    tpl = ("【环境】\n【想做什么】\n【我写的代码】（贴能跑的最小版本）\n"
           "【期望结果】\n【实际结果】\n【完整报错】（Traceback 全部复制）\n【我试过的】")
    body = """<div class="wrap">
  <div class="hero">
    <span class="bdg">HELP · 求助手册</span>
    <h1>卡住了怎么办</h1>
    <p>这一页解决的是「报错看不懂、搜也搜不到、身边没人可问」。
       自己能解决 80% 的问题、剩下 20% 知道怎么问，才算真能脱离课本自学。
       下面的报错提取器和提问模板都可以直接用。</p>
  </div>

  <h2>1 · 从报错里取出该搜的那一句</h2>
  <p>把完整报错粘进来，自动抽出<b>最后一行</b>——搜索只该用这一行，
     前面几行是调用栈，带着你的文件名和行号，搜了也搜不到。</p>
  <textarea id="tb" rows="7" spellcheck="false"
    placeholder="把 Traceback 粘在这里…"></textarea>
  <div class="fbar">
    <button type="button" id="go">提取最后一行</button>
    <button type="button" id="cp">复制</button>
    <a id="sg" class="btn" target="_blank" rel="noopener">去搜索</a>
    <span id="msg"></span>
  </div>
  <pre id="out" class="out">（提取结果会显示在这里）</pre>

  <h2>2 · 求助前先做完这三件事</h2>
  <ol>
    <li><b>把报错的最后一行原样复制</b>——不是凭记忆复述。</li>
    <li><b>把问题压到最小</b>：删代码删到「再删就不报错了」为止。</li>
    <li><b>自己先试过至少两种改法</b>，并把试过什么写进问题里。</li>
  </ol>
  <p>做完这三步，大概有三分之一的问题不用问就已经解决了——
     因为在压最小的过程中你自己就看见了原因。</p>

  <h2>3 · 怎么把问题压到最小（MRE）</h2>
  <ol>
    <li><b>去掉无关的读写和网络请求</b>：文件里读出来的数据，直接用字面量写在代码里。</li>
    <li><b>去掉无关的函数包装</b>：能直接跑的循环就别套函数。</li>
    <li><b>把大列表缩到两三个元素</b>：只要还能复现报错就行。</li>
  </ol>
  <pre><code>users = [{{"name": "a", "active": True}}, {{"name": "b"}}]
for u in users:
    print(u["active"])   # 第二项没有 active 键 → KeyError</code></pre>
  <p>压到这一步，答案往往自己浮出来：有数据缺字段，改 <code>u.get("active", False)</code> 就行。</p>

  <h2>4 · 提问模板（点下面的按钮直接复制）</h2>
  <pre id="tpl" class="out">{tpl}</pre>
  <div class="fbar"><button type="button" id="ct">复制提问模板</button><span id="msg2"></span></div>
  <p>四个最容易犯的错：<b>不贴完整报错</b>、<b>贴截图而不是文字</b>、
     <b>贴 300 行原始代码</b>、<b>把报错翻译成中文再问</b>（别人要搜原文）。</p>

  <h2>5 · 去哪问</h2>
  <div class="tblwrap"><table>
    <thead><tr><th>渠道</th><th>适合什么</th><th>注意</th></tr></thead>
    <tbody>
      <tr><td>搜索引擎</td><td>所有报错，尤其是常见错误</td><td>用上面提取出来的那一行原文</td></tr>
      <tr><td>Python 官方文档 docs.python.org</td><td>某个函数/模块到底怎么用</td><td>有中文版，英文版更新更全</td></tr>
      <tr><td>Stack Overflow</td><td>搜不到、又确实卡住的</td><td>先搜是否已有答案；按模板写</td></tr>
      <tr><td>库的 GitHub Issues</td><td>第三方库本身的 bug</td><td>先搜 closed issues，多半有人问过</td></tr>
      <tr><td>学习群 / 社区</td><td>概念理解、方向选择</td><td>同样要贴报错和代码</td></tr>
    </tbody>
  </table></div>

  <h2>6 · 问 AI 的四条纪律</h2>
  <ol>
    <li><b>给完整上下文</b>：报错原文 + 相关代码 + 你想达成的目标。</li>
    <li><b>要求解释，而不是只给代码</b>：问「为什么」，比问「帮我改」学到的多。</li>
    <li><b>它给的代码一定要自己跑一遍</b>——它会编造不存在的 API，一跑就现形。</li>
    <li><b>它给的解释要能用自己的话复述</b>：复述不出来就是你没懂。</li>
  </ol>
  <p>AI 是加速器，不是裁判。<b>代码跑得通才是唯一的裁判。</b></p>

  <div class="foot">
    <a href="../index.html">主页</a> ·
    <a href="lessons/index.html">课程目录</a> ·
    <a href="debug.html">排错速查</a> ·
    <a href="terms.html">术语索引</a> ·
    <a href="coverage.html">覆盖与自足性</a>
  </div>
</div>
<style>
textarea{{width:100%;box-sizing:border-box;border:1px solid var(--line);border-radius:10px;
background:var(--card);color:var(--text);font-family:ui-monospace,Consolas,monospace;
font-size:12.5px;line-height:1.6;padding:10px 12px;resize:vertical}}
.out{{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:11px 13px;font-size:12.5px;line-height:1.65;overflow-x:auto;white-space:pre-wrap}}
.fbar button,.fbar .btn{{height:34px;padding:0 14px;border-radius:8px;font:inherit;font-size:13px;
border:1px solid var(--line);background:var(--card);color:var(--text);cursor:pointer;
display:inline-flex;align-items:center;text-decoration:none}}
.fbar #msg,.fbar #msg2{{font-size:12.5px;color:var(--muted)}}
ol li{{margin:5px 0;line-height:1.8}}
</style>""".format(tpl=html.escape(tpl))

    js = """
var tb=document.getElementById('tb'),out=document.getElementById('out'),
    msg=document.getElementById('msg'),msg2=document.getElementById('msg2'),
    sg=document.getElementById('sg');
var last='';
function lastLine(s){
  var ls=s.split('\\n').map(function(x){return x.trim();}).filter(Boolean);
  for(var i=ls.length-1;i>=0;i--){ if(ls[i].indexOf('Error')>=0||ls[i].indexOf('error')>=0) return ls[i]; }
  return ls.length?ls[ls.length-1]:'';
}
document.getElementById('go').addEventListener('click',function(){
  last=lastLine(tb.value);
  out.textContent=last||'（没找到报错行，检查粘贴内容）';
  var q=last.replace(/^[^:]*:/,'').trim()||last;
  sg.href='https://www.bing.com/search?q='+encodeURIComponent(q+' python');
  sg.style.display=last?'':'none';
  msg.textContent=last?'已提取，可直接复制去搜':'';
});
document.getElementById('cp').addEventListener('click',function(){
  if(!last)return; navigator.clipboard.writeText(last).then(function(){msg.textContent='已复制';});
});
document.getElementById('ct').addEventListener('click',function(){
  var t=document.getElementById('tpl').textContent;
  navigator.clipboard.writeText(t).then(function(){msg2.textContent='已复制，粘贴到群里填空即可';});
});
"""
    return page("求助手册", body, js)


def page(title, body, js):
    return SHELL.format(title=html.escape(title), css=CSS, body=body, js=js)


def main():
    meta = []
    for i, (u, span, wk, title, goal, acts, crit) in enumerate(site_data.lessons(), 1):
        meta.append({"no": i, "unit": u, "title": title})
    terms = build_terms(meta)
    coverage = build_coverage(meta)
    open(os.path.join(WEB, "terms.html"), "w", encoding="utf-8").write(terms)
    open(os.path.join(WEB, "coverage.html"), "w", encoding="utf-8").write(coverage)

    # 排错速查需要 markdown 转换器（复用 build_lectures.convert）
    _sp = importlib.util.spec_from_file_location(
        "bl", os.path.join(HERE, "build_lectures.py"))
    bl = importlib.util.module_from_spec(_sp)
    _sp.loader.exec_module(bl)
    debug = build_debug(meta, bl)
    helpp = build_help(meta)
    open(os.path.join(WEB, "debug.html"), "w", encoding="utf-8").write(debug)
    open(os.path.join(WEB, "help.html"), "w", encoding="utf-8").write(helpp)
    n_err = debug.count('<details class="ec"')
    n_terms = terms.count("<li data-t=")
    # 首页资料库卡上的条数跟着实际数量走（不是 data-n，audit 不校验这一处）
    home = os.path.join(ROOT, "index.html")
    if os.path.exists(home):
        s = open(home, encoding="utf-8").read()
        s2 = re.sub(r"术语索引（\d+ 条）", f"术语索引（{n_terms} 条）", s)
        if s2 != s:
            open(home, "w", encoding="utf-8").write(s2)
    print(f"术语索引 {n_terms} 条 | 覆盖矩阵 20 章 + 附录 5 项 | "
          f"排错速查 {n_err} 条 | 求助手册 1 页 | "
          f"terms {len(terms) // 1024} KB, coverage {len(coverage) // 1024} KB, "
          f"debug {len(debug) // 1024} KB, help {len(helpp) // 1024} KB")


if __name__ == "__main__":
    main()
    import theme  # 主题派生：把浅色样式表翻成深色表并注入切换按钮
    theme.sweep([WEB])
