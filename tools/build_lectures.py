"""
把 course/*.md 讲义与 exercises/*.md 题库转换成可直接双击打开的 HTML。
- Pygments 代码高亮
- 自动生成侧边目录（TOC）
- 顶部/底部 上一单元 / 下一单元 导航
- 学习进度勾选存 localStorage
用法：C:\\Users\\57411\\.workbuddy\\binaries\\python\\versions\\3.13.12\\python.exe tools\\build_lectures.py
"""
import os
import re
import html
import markdown
from pygments import highlight
from pygments.lexers import PythonLexer, BashLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE = os.path.join(ROOT, "course")
EXERCISES = os.path.join(ROOT, "exercises")
OUT = os.path.join(ROOT, "web")

# 围栏语言 -> 角标文案；info 串（info string）显式指定时优先
KIND_OF = {
    "python": "Python",
    "bash": "终端命令",
    "sh": "终端命令",
    "shell": "终端命令",
    "console": "运行结果",
    "powershell": "终端命令",
    "text": "代码",
    "json": "JSON",
    "yaml": "YAML",
    "html": "HTML",
    "sql": "SQL",
}
CODE_LABELS = {
    "bash": "终端命令",
    "console": "运行结果",
    "output": "运行结果",
    "text": "示例",
    "gitignore": ".gitignore",
    "tree": "目录结构",
    "traceback": "报错信息",
    "error": "报错信息",
}

PAGES = []
TITLES = {}

# 单元清单从course/ 目录自动扫描，不写死数量（阶段 2 加入后无需改代码）
for _f in sorted(os.listdir(COURSE)):
    if not _f.endswith(".md"):
        continue
    _m = re.match(r"^(\d\d)-单元(\d+)[-：](.+)\.md$", _f)
    if not _m:
        continue
    _no = int(_m.group(2))
    PAGES.append((_f, _no))
    TITLES[_no] = _m.group(3).replace("-", " ").replace("Play按钮", "Play 按钮")
PAGES.sort(key=lambda x: x[1])

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

:root{--bg:#f6f8fb;--card:#fff;--line:#e3e8ef;--text:#16232e;--muted:#5f7183;
--p1:#1f5fa8;--p1bg:#eaf1fb;--p2:#0e9b78;--p3:#e08a15;--p3bg:#fdf3e2}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;line-height:1.75}
a{color:var(--p1);text-decoration:none}
a:hover{text-decoration:underline}

/* 顶栏 */
.top{position:sticky;top:0;z-index:40;background:rgba(246,248,251,.95);backdrop-filter:blur(10px);
border-bottom:1px solid var(--line)}
.top-in{max-width:1360px;margin:0 auto;padding:0 22px;height:58px;display:flex;align-items:center;gap:18px}
.back{font-size:13.5px;color:var(--muted);white-space:nowrap}
.back:hover{color:var(--p1)}
.top-in .tno{font-size:11.5px;font-weight:700;color:var(--p1);background:var(--p1bg);
border-radius:20px;padding:3px 10px;white-space:nowrap;font-variant-numeric:tabular-nums}
.top h1{font-size:16px;margin:0;font-weight:700;flex:1;min-width:0;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tag{font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;background:var(--p1bg);
color:var(--p1);white-space:nowrap}
.tag.done{background:#d9f0e6;color:#0a7a5f}

/* 布局 */
.layout{max-width:1360px;margin:0 auto;padding:26px 22px 80px;display:flex;gap:26px;align-items:flex-start}
/* 侧栏本身不再是一张卡：里面放「配套资料」和「本单元目录」两张独立卡片 */
.side{width:250px;flex-shrink:0;position:sticky;top:84px;max-height:calc(100vh - 110px);
overflow-y:auto}
.tocbox{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:16px 14px;margin-bottom:12px}
.tocbox h4{margin:0 0 10px;font-size:11.5px;color:var(--muted);letter-spacing:1px;font-weight:700}
.toc a{display:block;padding:5px 8px;border-radius:6px;font-size:13px;color:#3d5063;
border-left:2px solid transparent;margin-bottom:1px}
.toc a:hover{background:#f2f5f9;text-decoration:none}
.toc a.lv2{font-weight:600;color:var(--text)}
.toc a.lv3{padding-left:18px;font-size:12.5px;color:var(--muted)}
.sidetag{margin-top:16px;padding-top:14px;border-top:1px solid var(--line);
font-size:12.5px;color:var(--muted);line-height:1.7}
.sidetag b{color:var(--p1)}

.main{flex:1;min-width:0;background:var(--card);border:1px solid var(--line);
border-radius:14px;padding:34px 40px;overflow-wrap:anywhere}

/* 正文排版 */
.main h1{font-size:30px;margin:0 0 8px;line-height:1.3;padding-bottom:16px;border-bottom:2px solid var(--line)}
.main h2{font-size:22px;margin:40px 0 14px;padding-left:13px;border-left:4px solid var(--p1);line-height:1.4}
.main h3{font-size:17px;margin:26px 0 10px;color:var(--p1)}
.main h4{font-size:15px;margin:20px 0 8px;color:#33475a}
.main p{margin:11px 0}
.main ul,.main ol{margin:11px 0;padding-left:24px}
.main li{margin:6px 0}
.main strong{color:#0f4c8a}
.main hr{border:none;border-top:1px dashed var(--line);margin:28px 0}
.main blockquote{margin:14px 0;padding:12px 16px;background:var(--p1bg);
border-left:4px solid var(--p1);border-radius:0 8px 8px 0;color:#2c4a68;font-size:14px}
.main blockquote p{margin:4px 0}
.main code{background:#eef1f5;border-radius:4px;padding:2px 6px;font-size:.88em;
font-family:Consolas,"SFMono-Regular",monospace;color:#0f5a3d}
.main table{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}
.main th{background:#f1f4f8;padding:10px 13px;text-align:left;font-size:13px;
color:var(--muted);border:1px solid var(--line);font-weight:600}
.main td{padding:10px 13px;border:1px solid var(--line);vertical-align:top}
.main pre{background:#1e2a35;border-radius:10px;padding:0;margin:16px 0;overflow:hidden;
position:relative}
.main pre code{display:block;padding:16px 18px;font-size:13.5px;line-height:1.65;
font-family:Consolas,"SFMono-Regular",monospace;background:none;overflow-x:auto}
.main pre .cl{position:absolute;top:8px;right:12px;font-size:10.5px;color:#6b7f92;
letter-spacing:.5px;background:rgba(255,255,255,.07);padding:2px 8px;border-radius:4px}
.main pre.broken{border:2px dashed var(--p3)}
.main pre.broken .cl{background:rgba(224,138,21,.22);color:var(--p3);font-weight:700}
.badge-broken{display:inline-block;background:var(--p3bg);color:#a86a0c;font-size:11.5px;
font-weight:700;padding:4px 11px;border-radius:5px;margin:4px 0 0}

/* 底部导航 */
.pn{display:flex;gap:12px;margin-top:44px;padding-top:22px;border-top:1px solid var(--line)}
.pn a{flex:1;background:#f2f5f9;border-radius:10px;padding:14px 18px;border:1px solid var(--line)}
.pn a:hover{background:#e8edf3;text-decoration:none;border-color:var(--p1)}
.pn .nx{text-align:right}
.pn small{display:block;font-size:11.5px;color:var(--muted);margin-bottom:3px}
.pn b{font-size:14.5px;color:var(--text)}
.pn .spot{flex:0;min-width:90px;display:flex;align-items:center;justify-content:center;
background:#f2f5f9;border-radius:10px;border:1px solid var(--line)}

@media(max-width:1000px){
 .layout{flex-direction:column;align-items:stretch;padding:18px 14px 60px}
 .side{position:static;width:100%;max-height:none}
 .main{padding:24px 18px}
 .main h1{font-size:23px}.main h2{font-size:19px}
 .pn{flex-direction:column}
}

"""

JS = """
/* 代码块一键复制：111 节课每节都有代码，手动选中太费劲 */
(function(){
  document.querySelectorAll('pre').forEach(function(pre){
    if(pre.querySelector('.cp')) return;
    var b=document.createElement('button');
    b.className='cp'; b.type='button'; b.textContent='复制';
    b.addEventListener('click', function(){
      var code=pre.querySelector('code')||pre;
      var txt=code.innerText;
      function ok(){b.textContent='已复制 ✓';b.classList.add('ok');
        setTimeout(function(){b.textContent='复制';b.classList.remove('ok')},1500);}
      function fallback(){
        var t=document.createElement('textarea');
        t.value=txt; t.style.position='fixed'; t.style.opacity='0';
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

/* 单元完成度：读课节页写入的 lesson-done-v1，按本单元的课节号区间统计 */
(function(){
  var box=document.querySelector('.uprog'); if(!box) return;
  var a=+box.dataset.from, b=+box.dataset.to, tot=b-a+1;
  function paint(){
    var o={}; try{o=JSON.parse(localStorage.getItem('lesson-done-v1')||'{}')}catch(e){}
    var n=0; for(var i=a;i<=b;i++) if(o[String(i)]) n++;
    box.querySelector('i').style.width=(n/tot*100)+'%';
    box.querySelector('b').textContent='已学 '+n+' / '+tot+' 节';
  }
  paint();
  window.addEventListener('focus',paint);
  document.addEventListener('visibilitychange',paint);
  window.addEventListener('storage',paint);
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

function markDone(n, on){
  try{
    var k='py-hub-v1', a=JSON.parse(localStorage.getItem(k)||'null');
    if(!Array.isArray(a)) a=new Array(12).fill(false);
    a[n]=on; localStorage.setItem(k, JSON.stringify(a));
  }catch(e){}
}
function initDone(){
  var n=parseInt(document.body.dataset.unit,10);
  if(isNaN(n)) return;
  var box=document.getElementById('doneBox');
  try{
    var a=JSON.parse(localStorage.getItem('py-hub-v1')||'null');
    if(Array.isArray(a)&&a[n]){ box.checked=true; box.closest('.dd').classList.add('on'); }
  }catch(e){}
  box.addEventListener('change',function(){
    box.closest('.dd').classList.toggle('on',box.checked);
    markDone(n,box.checked);
  });
}
document.addEventListener('DOMContentLoaded',function(){
  initDone();
  // TOC 当前项高亮
  var links=[].slice.call(document.querySelectorAll('.toc a'));
  var targets=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));});
  function onScroll(){
    var y=window.scrollY+140, cur=0;
    targets.forEach(function(t,i){ if(t&&t.offsetTop<=y) cur=i; });
    links.forEach(function(a,i){ a.style.background = (i===cur)?'#eaf1fb':''; a.style.borderLeftColor=(i===cur)?'var(--p1)':'transparent'; });
  }
  onScroll(); window.addEventListener('scroll',onScroll, {passive:true});
  // 代码块加标签
  document.querySelectorAll('.main pre').forEach(function(pre){
    var code=pre.querySelector('code');
    var lang=(code.className.match(/language-([\\w-]+)/)||[])[1];
    var label = pre.classList.contains('broken') ? '故意写错 · 观察报错'
              : (lang==='python'?'Python':(lang||'code'));
    var s=document.createElement('span'); s.className='cl'; s.textContent=label;
    pre.appendChild(s);
  });
});
"""


def highlight_html(code, lang):
    """返回高亮后的 HTML，lang 为 None 时表示故意写错的示例。"""
    # 无标注的块按内容猜：traceback / gitignore / 目录树 / 程序输出
    guess = lang
    if guess in (None, "text"):
        head = code.lstrip()[:200]
        if re.search(r'^\s*Traceback \(most recent call last\)|^\s*File ".*", line \d+|\w+Error:', code, re.M):
            guess = "text"
        elif re.search(r"^[#*!\[].*|\b__pycache__|\.venv/|venv/", head, re.M):
            guess = "gitignore"
        elif re.search(r"├──|└──|│\s*├──", code):
            guess = "text"
    try:
        if guess in (None, "python"):
            lexer = PythonLexer()
        elif guess in ("bash", "sh", "shell", "console", "powershell"):
            lexer = BashLexer()
        elif guess == "gitignore":
            lexer = get_lexer_by_name("ini", stripall=False)
        else:
            lexer = get_lexer_by_name(guess, stripall=False)
        fmt = HtmlFormatter(nowrap=True, style="default")
        return highlight(code, lexer, fmt)
    except Exception:
        return html.escape(code)


def convert(md_text):
    """Markdown -> HTML，含代码高亮、错误示例标记、标题锚点。"""
    # 逐块处理 fenced code，先把 python 块替换为占位符，避免被 markdown 解析
    blocks = []

    def stash(m):
        info = m.group(1).strip()
        body = m.group(2)
        # 列表内嵌的代码块每行都带一层列表缩进（如 3/8 空格），
        # python-markdown 渲染 <ol>/<ul> 时会原样保留，页面上看着像多缩进一级；
        # 这里按非空行的公共前缀去掉（顶层代码块没有公共缩进，不受影响）。
        lines = body.split("\n")
        indents = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
        if indents and min(indents) > 0:
            cut = min(indents)
            body = "\n".join(l[cut:] if l.strip() else l for l in lines)
        lang = None
        if info.lower().startswith("python"):
            lang = "python"
        elif info:
            lang = info.split()[0].lower()
        kind = info.strip() or ""
        if not kind:
            # 无 info 时按内容猜标签
            if re.search(r'^\s*Traceback \(most recent call last\)|^\s*File ".*", line \d+'
                         r"|^\w*(Error|Exception):", body, re.M):
                kind = "traceback"
            elif re.search(r"├──|└──|│", body):
                kind = "tree"
            elif re.search(r"^\s*(gitignore|__pycache__|\.venv/|venv/|\*\.pyc)", body, re.M):
                kind = "gitignore"
            elif re.search(r"^\s*(from|import |def |class |for |while |if |print\()", body, re.M):
                lang = lang or "python"
            elif re.search(r"^\s*=+\s*(test session|pytest|warnings summary)",
                           body, re.M) or re.search(r"passed|failed|error in \S+",
                                                    body):
                kind = "console"
            elif re.search(r"^\s*(处理后|商品|你的|第一个|name =|我叫|bool\(|10$)",
                           body, re.M):
                kind = "console"
        broken = body.lstrip().startswith("# INTENTIONALLY-BROKEN")
        # 去掉故意写错标记注释
        lines = body.split("\n")
        if broken:
            for i, ln in enumerate(lines):
                if "INTENTIONALLY-BROKEN" in ln:
                    lines[i] = re.sub(r"#\s*INTENTIONALLY-BROKEN.*", "", ln).rstrip()
                    break
            body = "\n".join(lines)
        blocks.append((body, lang, broken, kind))
        return f"\n\n@@CODE{len(blocks)-1}@@\n\n"

    text = re.sub(r"```([^\n]*)\n(.*?)```", stash, md_text, flags=re.S)

    # 表格 / 列表扩展
    text = re.sub(r"(?<!\\)\*\*", "**", text)
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
        output_format="html5",
    )
    out = md.convert(text)

    # 回填代码块
    def fill(m):
        i = int(m.group(1))
        body, lang, broken, kind = blocks[i]
        cls = "language-" + (lang or "text") if lang else "text"
        h = highlight_html(body.rstrip("\n"), lang)
        bcls = " class=\"broken\"" if broken else ""
        if broken:
            label = "故意写错 · 先跑一遍看报错"
            extra = ('<div class="badge-broken">这是故意写错的示例——先自己跑一遍看报错，'
                     '再对照下面的解析弄清错在哪</div>')
        else:
            label = CODE_LABELS.get(kind) or (KIND_OF.get(lang) or kind or "代码")
            extra = ""
        h = f'<span class="cl">{html.escape(label)}</span>' + h
        return f'<pre{bcls}><code class="{cls}">{h}</code></pre>{extra}'

    out = re.sub(r"<p>@@CODE(\d+)@@</p>", fill, out)
    return out


def add_heading_ids(body_html):
    """给 h1/h2/h3 注入唯一 id，python-markdown 默认不加锚点。"""
    used = {}

    def uniq(base):
        n = used.get(base, 0)
        used[base] = n + 1
        return base if n == 0 else f"{base}-{n}"

    def repl(m):
        tag, inner = m.group(1), m.group(2)
        txt = re.sub(r"<[^>]+>", "", inner)
        base = re.sub(r"[^\w一-鿿]+", "-", txt.strip()).strip("-").lower()[:40] or "sec"
        return f'<h{tag} id="{uniq(base)}">{inner}</h{tag}>'

    return re.sub(r"<h([123])>(.*?)</h\1>", repl, body_html, flags=re.S)


def toc_from_html(body_html):
    """从转换后的 HTML 提取 h2/h3 生成目录。"""
    items = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', body_html, re.S):
        lvl, aid, txt = m.group(1), m.group(2), re.sub(r"<[^>]+>", "", m.group(3))
        items.append(f'<a class="lv{lvl}" href="#{aid}">{html.escape(txt)}</a>')
    return "\n".join(items)


# 课件映射统一来自 tools/ppt_map.py，避免多处维护漂移
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import ppt_map
import bank_map
import site_data
UNIT_SLIDE = ppt_map.UNIT_SLIDE


def page_shell(title, unit_no, body_html, toc_html, prev_link, next_link, done_block=True):
    # 讲义首部的「对应教材第 X 章 / 关键词」从裸 blockquote 升级成对照框：
    # 章节信息一眼可见，并直通覆盖矩阵（该单元对应的那一行）。
    if unit_no is not None:
        _m = re.search(r"<blockquote>\s*<p>(对应教材.*?)</p>\s*</blockquote>",
                       body_html, re.S)
        if _m:
            _inner = _m.group(1)
            _parts = _inner.split("\n", 1)
            _head = _parts[0].strip()
            _rest = _parts[1].strip() if len(_parts) > 1 else ""
            _box = (f'<div class="bkbx"><div class="bk-h"><b>原书对照</b>'
                    f'<span>{_head}</span></div>'
                    + (f'<p class="bk-k">{_rest}</p>' if _rest else "")
                    + f'<a href="coverage.html#u{unit_no}">'
                      f'这套课覆盖了教材哪些章 →</a></div>')
            body_html = body_html[:_m.start()] + _box + body_html[_m.end():]
    prev = ""
    if prev_link:
        prev = (f'<a class="pn" href="{prev_link[1]}"><small>← 上一单元</small>'
                f'<b>{prev_link[0]}</b></a>')
    nxt = ""
    if next_link:
        nxt = (f'<a class="pn nx" href="{next_link[1]}"><small>下一单元 →</small>'
               f'<b>{next_link[0]}</b></a>')
    dd = ""
    if done_block:
        dd = ('<label class="dd"><input type="checkbox" id="doneBox">'
              '<span>标记本单元已完成</span></label>')

    # 本单元配套：课节 / 课件 / 题库 / 课表，一处直达
    rel_box = ""
    if unit_no is not None:
        _sn2 = UNIT_SLIDE.get(unit_no)
        _rows = [f'<a href="lessons/index.html#u{unit_no}">'
                 f'<span class="k">课节</span>'
                 f'<span class="v">本单元全部课节 · 一节一节学</span></a>']
        _rows.append(f'<a href="ppt/u/{unit_no:02d}.html">'
                     f'<span class="k">课件</span>'
                     f'<span class="v">逐节版 · 每节课 2 页</span></a>')
        if _sn2:
            _rows.append(f'<a href="ppt/index.html#s{_sn2}">'
                         f'<span class="k">大纲</span>'
                         f'<span class="v">课程大纲课件 p{_sn2}</span></a>')
        _nq = bank_map.count(unit_no)
        _rows.append(f'<a href="bank.html#u{unit_no}"><span class="k">题库</span>'
                     f'<span class="v">本单元 {_nq} 题 · 共 {bank_map.TOTAL} 题</span></a>'
                     if _nq else
                     '<a href="bank.html"><span class="k">题库</span>'
                     f'<span class="v">题库暂未覆盖本单元 · 共 {bank_map.TOTAL} 题</span></a>')
        _rows.append('<a href="../python-course-syllabus.html">'
                     '<span class="k">课表</span>'
                     '<span class="v">总课表与阶段安排</span></a>')
        _rows.append('<a href="review.html"><span class="k">复习</span>'
                     '<span class="v">艾宾浩斯复习计划 · 6 轮</span></a>')
        _lo, _hi = site_data.unit_lesson_range(unit_no)
        _uprog = (f'<div class="uprog" data-from="{_lo}" data-to="{_hi}">'
                  f'<div class="uprog-h"><b>已学 0 / {_hi - _lo + 1} 节</b>'
                  f'<span>按课节页勾选统计</span></div>'
                  f'<div class="track"><i></i></div></div>')
        rel_box = ('<div class="relbox"><h4>本单元配套资料</h4>'
                   + _uprog +
                   '<div class="rel">' + ''.join(_rows) + '</div></div>')

    # 课件入口：主入口 = 本单元逐节版课件；次入口 = 课程大纲课件对应页
    ppt_link = ppt_btn = ""
    if unit_no is not None:
        _ud = ppt_map.unit_deck_path(unit_no)      # ppt/u/NN.html
        _sn = UNIT_SLIDE.get(unit_no)
        ppt_link = (f'<a class="ppt" href="{_ud}" '
                    f'title="本单元逐节课件：每节课都有课节页与知识点页">'
                    f'本单元课件</a>')
        _also = (f'<a class="pn" href="ppt/index.html#s{_sn}">'
                 f'<small>课程大纲课件</small><b>阶段总览 p{_sn} →</b></a>'
                 if _sn else '')
        ppt_btn = (f'<a class="pn" href="{_ud}">'
                   f'<small>本单元课件</small><b>逐节版 · 点开就讲 →</b></a>'
                   + _also)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231f5fa8'/%3E%3Ctext x='16' y='22' font-size='15' font-family='monospace' fill='%23fff' text-anchor='middle'%3EPy%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="css/unit.css">
<style>
#toTop{{position:fixed;right:22px;bottom:22px;width:42px;height:42px;border-radius:50%;
background:#1f5fa8;color:#fff;border:none;font-size:18px;line-height:1;cursor:pointer;
box-shadow:0 6px 18px rgba(20,40,70,.22);opacity:0;pointer-events:none;
transition:opacity .18s;z-index:60}}
#toTop.on{{opacity:1;pointer-events:auto}}
@media print{{#toTop{{display:none}}}}
</style>
</head>
<body data-unit="{unit_no if unit_no is not None else ''}">
<div class="top"><div class="top-in">
  <a class="back" href="../index.html">← 主页</a>
  <h1>{html.escape(title)}</h1>
  {ppt_link}
  {dd}
</div></div>

<div class="layout">
  <aside class="side">
    {rel_box}
    <div class="tocbox">
      <h4>本单元目录</h4>
      <nav class="toc">{toc_html}</nav>
      <div class="sidetag">
        <b>学习提醒</b><br>
        讲完不超过 10 分钟就要自己敲一遍代码。<br>
        报错是教材，不要擦掉。
      </div>
    </div>
  </aside>
  <main class="main">{body_html}</main>
</div>

<div class="layout" style="padding-top:0">
  <aside class="side"></aside>
  <div class="pn">{prev}<div class="spot">{ppt_btn}</div>{nxt}</div>
</div>

<style>
.dd{{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--muted);
cursor:pointer;white-space:nowrap}}
.dd input{{width:17px;height:17px;accent-color:var(--p2);cursor:pointer}}
.uprog{{margin:0 0 10px;padding:9px 10px;background:#f7f9fc;border-radius:9px}}
.uprog-h{{display:flex;flex-direction:column;gap:2px;font-size:11px;
color:var(--muted);line-height:1.5}}
.uprog-h b{{color:var(--p2);font-size:13px;white-space:nowrap}}
.uprog .track{{margin-top:6px;height:7px;background:#e6ecf3;border-radius:99px;
overflow:hidden}}
.uprog .track i{{display:block;height:100%;width:0;background:var(--p2);
border-radius:99px;transition:width .2s}}
pre .cp{{position:absolute;top:6px;right:10px;font:inherit;font-size:11.5px;
font-weight:700;color:var(--p1);background:#fff;border:1px solid var(--line);
border-radius:6px;padding:2px 9px;cursor:pointer;opacity:0;transition:opacity .12s}}
pre:hover .cp{{opacity:1}}
pre .cp.ok{{color:#fff;background:var(--p2);border-color:var(--p2)}}
.relbox{{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:14px;margin-bottom:12px}}
.bkbx{{background:linear-gradient(135deg,#f6f9fd,#eef4fb);border:1px solid #dbe6f2;
border-radius:12px;padding:13px 16px;margin:0 0 18px}}
.bkbx .bk-h{{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap}}
.bkbx .bk-h b{{font-size:11px;letter-spacing:1px;color:var(--p1);background:#fff;
border:1px solid #d5e3f3;border-radius:5px;padding:2px 8px;white-space:nowrap}}
.bkbx .bk-h span{{font-size:13.5px;font-weight:700;color:#1b3348;line-height:1.6}}
.bkbx .bk-k{{margin:7px 0 0;font-size:12.5px;color:#54636f;line-height:1.7}}
.bkbx > a{{display:inline-block;margin-top:8px;font-size:12px;font-weight:700;
color:var(--p1);text-decoration:none}}
.bkbx > a:hover{{text-decoration:underline}}
.relbox h4{{margin:0 0 8px;font-size:11.5px;color:var(--muted);letter-spacing:1px;
font-weight:700}}
.rel{{display:flex;flex-direction:column;gap:2px}}
.rel a{{display:flex;gap:8px;align-items:baseline;padding:5px 6px;border-radius:7px;
text-decoration:none;color:inherit}}
.rel a:hover{{background:#f2f7fd}}
.rel .k{{flex:0 0 30px;font-size:11px;font-weight:700;color:#fff;background:var(--p1);
border-radius:4px;text-align:center;line-height:17px}}
.rel a:nth-child(2) .k{{background:var(--p3)}}
.rel a:nth-child(3) .k{{background:var(--p2)}}
.rel a:nth-child(4) .k{{background:#7a8b9a}}
.rel a:nth-child(5) .k{{background:#9a7a7a}}
.rel .v{{font-size:12px;color:var(--text);line-height:1.45}}
.top-in .ppt{{font-size:12.5px;font-weight:700;color:#8a5a00;background:#fdf3e2;
border:1px solid #f0d8a8;border-radius:6px;padding:4px 10px;white-space:nowrap}}
.top-in .ppt:hover{{background:#fbe9cc;text-decoration:none}}
.dd.on span{{color:var(--p2);font-weight:700}}
</style>
<script>{JS}</script>
<script src="media/bgm.js" defer></script>
</body>
</html>"""


def main():
    os.makedirs(OUT, exist_ok=True)
    # 22 个单元页共用一份 CSS：抽成外链，别在每个页面里重复 7 KB。
    # 放 css/ 而不是 assets/——build_portable 会自动跳过 assets 目录（PPT 素材），
    # 放那里会导致便携包里样式丢失。
    os.makedirs(os.path.join(OUT, "css"), exist_ok=True)
    open(os.path.join(OUT, "css", "unit.css"), "w",
         encoding="utf-8").write(CSS)
    report = []

    for fname, no in PAGES:
        path = os.path.join(COURSE, fname)
        md = open(path, encoding="utf-8").read()
        body = add_heading_ids(convert(md))
        toc = toc_from_html(body)

        prev_link = None
        if no > 0:
            prev_link = (f"单元 {no-1} · {TITLES[no-1]}", f"{no-1:02d}.html")
        next_link = None
        if no < len(PAGES) - 1:
            next_link = (f"单元 {no+1} · {TITLES[no+1]}", f"{no+1:02d}.html")

        title = f"单元 {no} · {TITLES[no]}"
        page = page_shell(title, no, body, toc, prev_link, next_link)
        out_path = os.path.join(OUT, f"{no:02d}.html")
        open(out_path, "w", encoding="utf-8").write(page)

        n_code = body.count("<pre")
        n_broken = body.count('class="broken"')
        report.append((out_path, len(page), n_code, n_broken, toc.count("<a ")))

    # 题库页由 tools/build_bank.py 生成（答案折叠 / 分档筛选 / 深链）。
    # 这里只负责调用，别再自己渲染一遍——否则会把新版覆盖成旧模板。
    import build_bank
    n_q, size_q = build_bank.build()
    report.append((os.path.join(OUT, "bank.html"), size_q, 0, 0, n_q))

    print(f"{'文件':<14}{'字节':>9}{'代码块':>8}{'故意错':>8}{'目录项':>8}")
    print("-" * 50)
    total_b = total_c = total_x = total_t = 0
    for p, size, nc, nb, nt in report:
        print(f"{os.path.basename(p):<14}{size:>9}{nc:>8}{nb:>8}{nt:>8}")
        total_b += size; total_c += nc; total_x += nb; total_t += nt
    print("-" * 50)
    print(f"{'合计':<14}{total_b:>9}{total_c:>8}{total_x:>8}{total_t:>8}")
    print(f"\n输出目录：{OUT}")


if __name__ == "__main__":
    main()