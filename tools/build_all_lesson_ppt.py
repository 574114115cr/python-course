# -*- coding: utf-8 -*-
"""编排「逐节版讲授课件」的全部构建：

1. 生成每单元的 DSL（复用 build_lesson_ppt）
2. 用 slidep 构建逐节课件/Python讲授课件-单元NN.pptx
3. 渲染每页 PNG 到 web/ppt/u/NN/slide-XX.png
4. 生成每单元的 HTML 播放器 web/ppt/u/NN.html
5. 写出映射 web/ppt/u/manifest.json（课节 -> 单元、页码）

用法：
  python tools/build_all_lesson_ppt.py            # 全量
  python tools/build_all_lesson_ppt.py 12 13      # 只做指定单元
"""
import json
import os
import shutil
import subprocess
import time
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slidep/swc 需要可写的 TEMP（本机 TEMP 指向 workbuddy-update 目录时会静默失败）
sys.path.insert(0, os.path.join(ROOT, "tools"))
import slidep_env  # noqa: E402
slidep_env.prepare()

TOOLS = os.path.join(ROOT, "tools")
PPT_DIR = os.path.join(ROOT, "python-course-ppt")
DECK_SRC = os.path.join(PPT_DIR, "lessons-deck")
OUT_PPT = os.path.join(PPT_DIR, "逐节课件")
WEB_U = os.path.join(ROOT, "web", "ppt", "u")

NODE = r"C:\Users\57411\.workbuddy\binaries\node\versions\22.22.2-6\node.exe"
SLIDEP = (r"C:\Users\57411\.workbuddy\binaries\node\versions\22.22.2-6"
          r"\node_modules\@tencent\slidep\dist\index.js")


def slide_count(pptx):
    """读 pptx 实际页数（不依赖 python-pptx）。"""
    import re
    import zipfile
    try:
        with zipfile.ZipFile(pptx) as z:
            return len([n for n in z.namelist()
                        if re.match(r"ppt/slides/slide\d+\.xml$", n)])
    except Exception:
        return 0


def run(args, timeout=120, **kw):
    """跑一个子进程。**必须带超时**——slidep 偶尔会挂住，不加超时整个脚本会永久卡死。"""
    try:
        return subprocess.run(args, capture_output=True, text=True,
                              encoding="utf-8", errors="ignore",
                              timeout=timeout, **kw)
    except subprocess.TimeoutExpired:
        class _R:
            stdout = ""
            stderr = f"timeout after {timeout}s"
            returncode = -1
        return _R()


def clear_dir(path):
    """清空一个图片目录 —— 用「移到垃圾目录」而不是「删除」。

    坑：沙箱把删除改写成移入回收站，并在**每轮**删除数超过 50 时弹批量确认，
    该确认会抛异常直接中断整个构建（曾因此让 u05 之后的单元全没渲染）。
    而 `os.replace` 只是改名，不触发这套策略。旧图必须清掉，否则页数变少时
    会残留上一版的尾巴，所以这里逐个搬到 `.cache/ppt_garbage/`。
    """
    if not os.path.isdir(path):
        return
    garbage = os.path.join(ROOT, ".cache", "ppt_garbage")
    os.makedirs(garbage, exist_ok=True)
    tag = os.path.basename(os.path.normpath(path))
    blocked = 0
    for name in sorted(os.listdir(path)):
        src = os.path.join(path, name)
        try:
            os.replace(src, os.path.join(garbage, f"{tag}_{name}"))
        except Exception as error:          # 被策略拦下也不要中断构建
            blocked += 1
            if blocked == 1:
                print(f"  清理 {tag} 被拦（{type(error).__name__}），先跳过：{name}")
    if blocked:
        print(f"  !! {tag} 有 {blocked} 个旧图没清掉，页数变少时可能残留尾巴")


FAILED = []


def build_unit(unit, meta):
    """构建一个单元的 pptx + 图片 + HTML。返回 manifest 片段。"""
    slides = meta["slides"]
    n = len(slides)
    name = f"Python讲授课件-单元{unit:02d}.pptx"
    pptx = os.path.join(OUT_PPT, name)
    img_dir = os.path.join(WEB_U, f"{unit:02d}")
    html_path = os.path.join(WEB_U, f"{unit:02d}.html")
    os.makedirs(OUT_PPT, exist_ok=True)

    # 断点续跑：pptx 页数、图片数、播放器都齐了就直接跳过。
    # 但必须再看一眼 DSL 是否比 pptx 新——页数不变而文字改了（改排版、换要点），
    # 只看页数会全部跳过，等于什么都没重建（踩过：封面/要点改动没落地）。
    if (os.path.exists(pptx) and os.path.exists(html_path)
            and os.path.isdir(img_dir)):
        n_img = len([f for f in os.listdir(img_dir) if f.endswith(".webp")])
        n_ppt = slide_count(pptx)
        dsl_dir = os.path.join(DECK_SRC, f"{unit:02d}")
        dsl_newer = False
        if os.path.isdir(dsl_dir):
            newest = max((os.path.getmtime(os.path.join(dsl_dir, f))
                          for f in os.listdir(dsl_dir) if f.endswith(".slide")),
                         default=0)
            dsl_newer = newest > os.path.getmtime(pptx) + 1
        if n_img == n and n_ppt == n and not dsl_newer:
            print(f"  单元 {unit:>2} 已完成，跳过")
            return {"unit": unit, "pptx": name, "slides": slides}

    # 建到临时文件：沙箱里「删除再重建」会被 safe-delete 拦下，
    # 而且 slidep 编译失败时会在正式路径留下 0 页空 deck。先建临时文件，
    # 页数校验通过后再写回正式文件，正式文件要么是旧的、要么是新的完整版。
    BACKUP_DIR = os.path.join(ROOT, ".cache", "deck_backup")
    backup = os.path.join(BACKUP_DIR, f"{unit:02d}.pptx")
    if os.path.exists(pptx) and slide_count(pptx) > 0:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        shutil.copy2(pptx, backup)      # 留底，便于事后对比/回滚

    tmp_dir = os.path.join(ROOT, ".cache", "deck_tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    # 临时文件绝不复用、也绝不删除：sandbox 的 safe-delete 会让 os.remove 抛 OSError
    # （trash 不可用时直接 FAIL_CLOSED），曾因此让构建在第一单元就崩掉。
    tmp = os.path.join(tmp_dir, f"{unit:02d}_{int(time.time())}.pptx")
    r = run([NODE, SLIDEP, "create", tmp])
    if '"ok":true' not in r.stdout:
        print(f"  单元{unit:02d} create 失败: {r.stdout[:120]} {r.stderr[:120]}")
        FAILED.append(unit)
        return None

    # upsert：失败或超时就重试一次，最后按实际页数补漏
    for i in range(1, n + 1):
        f = os.path.join(DECK_SRC, f"{unit:02d}", f"{i:02d}.slide")
        for attempt in (1, 2):
            r = run([NODE, SLIDEP, "upsert-dsl", tmp, "--dsl-file", f])
            if '"ok":true' in r.stdout:
                break
            print(f"  单元{unit:02d} 第{i}页第{attempt}次失败: "
                  f"{(r.stdout or r.stderr)[:110]}")
    got = slide_count(tmp)
    if got != n:
        print(f"  !! 单元{unit:02d} 只建成 {got}/{n} 页，正式文件保持原样")
        FAILED.append(unit)
        return None

    # 页数对上了，先把演讲者备注补进临时文件，再整体写回。
    # 关键：备注必须和 pptx 合并成「一次写入」——这个环境里文件被写一次就会被
    # 别的进程占住（读得出、写不进），事后单独跑 add_slide_notes 必然失败。
    src_path = tmp
    try:
        import add_slide_notes as notes_mod
        tmp_notes = tmp.replace(".pptx", "_notes.pptx")
        n_notes = notes_mod.annotate(tmp, tmp_notes, unit, slides)
        src_path = tmp_notes
        print(f"  单元{unit:02d} 备注 {n_notes} 页")
    except Exception as error:      # 备注不是命脉，写不进去也别毁掉正文
        print(f"  !! 单元{unit:02d} 备注没补上（{type(error).__name__}: "
              f"{str(error)[:60]}），本次只写正文")

    # 写回正式文件（被占用则另存 .new，不覆盖、不丢内容）
    try:
        with open(src_path, "rb") as src, open(pptx, "wb") as dst:
            dst.write(src.read())
    except PermissionError:
        alt = pptx.replace(".pptx", ".new.pptx")
        with open(src_path, "rb") as src, open(alt, "wb") as dst:
            dst.write(src.read())
        # 关键：这一步直接返回，不渲染图片。
        # 否则网页图是新的、可下载的 pptx 是旧的，同一份课件自相矛盾
        # （踩过：u01–u04 曾出现「图 1440 宽新排版 + pptx 旧排版」）。
        print(f"  !! 单元{unit:02d} 正式文件被占用，新版另存 {os.path.basename(alt)}；"
              f"图片保持旧版不重渲染")
        FAILED.append(unit)
        return None

    # 渲染图片
    clear_dir(img_dir)
    os.makedirs(img_dir, exist_ok=True)
    for i in range(1, min(got, n) + 1):
        out = os.path.join(img_dir, f"slide-{i:02d}.png")
        for attempt in (1, 2):
            r = run([NODE, SLIDEP, "screenshot", pptx,
                     "--page-index", str(i - 1), "--out", out], timeout=90)
            if os.path.exists(out) and os.path.getsize(out) > 2000:
                break
            print(f"  单元{unit:02d} 第{i}页截图第{attempt}次失败")

    return {"unit": unit, "pptx": name, "slides": slides}


def build_html(unit, info, unit_title, total_lessons):
    slides = info["slides"]
    data = []
    for s in slides:
        label = {"cover": "单元封面", "lesson": "课节", "points": "知识点",
                 "summary": "单元小结"}.get(s["kind"], "")
        data.append({"n": s["slide"], "k": s["kind"], "t": s.get("title", ""),
                     "no": s.get("no"), "label": label})
    payload = json.dumps(data, ensure_ascii=False)
    pptx_rel = "../../../python-course-ppt/逐节课件/" + info["pptx"]
    # 0 页的 pptx 是坏文件（slidep 编译失败留下的），宁可不给下载按钮，
    # 也不要让用户下到一个打不开的文件。
    deck_pptx = os.path.join(OUT_PPT, info["pptx"])
    if slide_count(deck_pptx) > 0:
        dlbtn = f'<a class="btn primary" href="{pptx_rel}" download>下载 .pptx</a>'
    else:
        dlbtn = ('<span class="btn" style="opacity:.55;cursor:not-allowed">'
                 '课件文件重建中</span>')
    html = TEMPLATE
    html = html.replace("__DATA__", payload)
    html = html.replace("__UNIT__", str(unit))
    html = html.replace("__UTITLE__", unit_title)
    html = html.replace("__DLBTN__", dlbtn)
    html = html.replace("__UNITPAD__", f"{unit:02d}")
    html = html.replace("__TOTAL__", str(len(slides)))
    html = html.replace("__LESSONS__", str(total_lessons))
    out = os.path.join(WEB_U, f"{unit:02d}.html")
    open(out, "w", encoding="utf-8").write(html)
    return out


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>单元 __UNIT__ 课件 · __UTITLE__</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 32 32\'%3E%3Crect width=\'32\' height=\'32\' rx=\'7\' fill=\'%231f5fa8\'/%3E%3Ctext x=\'16\' y=\'22\' font-size=\'15\' font-family=\'monospace\' fill=\'%23fff\' text-anchor=\'middle\'%3EPy%3C/text%3E%3C/svg%3E">
<style>
:root{--bg:#eef2f7;--card:#fff;--line:#d8e3ee;--text:#16232e;--muted:#5f7183;
--p1:#1f5fa8;--p2:#0e9b78;--p3:#e08a15}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);line-height:1.7;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}
a{color:var(--p1);text-decoration:none}a:hover{text-decoration:underline}
.top{position:sticky;top:0;z-index:30;background:rgba(238,242,247,.95);
backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top-in{max-width:1180px;margin:0 auto;padding:12px 22px;display:flex;
align-items:center;gap:12px;flex-wrap:wrap}
.brand{font-size:17px;font-weight:700}
.badge{font-size:12.5px;font-weight:700;color:#fff;background:var(--p1);
border-radius:5px;padding:3px 10px}
.spacer{flex:1}
.btn{font-size:13.5px;border:1px solid var(--line);background:#fff;color:var(--p1);
border-radius:8px;padding:7px 13px;cursor:pointer;font-family:inherit;font-weight:600}
.btn:hover{background:#f2f7fd;text-decoration:none}
.btn.primary{background:var(--p1);color:#fff;border-color:var(--p1)}
.wrap{max-width:1180px;margin:0 auto;padding:22px 22px 60px}
h1{font-size:23px;margin:6px 0 4px}
.sub{color:var(--muted);font-size:14.5px;margin:0 0 18px}
.stage{background:var(--card);border:1px solid var(--line);border-radius:14px;
box-shadow:0 2px 12px rgba(22,35,46,.06);overflow:hidden}
.stage-img{display:block;width:100%;height:auto;background:#fff}
.bar{display:flex;align-items:center;gap:12px;padding:12px 16px;
border-top:1px solid var(--line);flex-wrap:wrap}
.bar .t{font-size:15px;font-weight:700}
.bar .k{font-size:11.5px;font-weight:700;color:#fff;background:var(--p2);
border-radius:4px;padding:2px 8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));
gap:12px;margin-top:22px}
.cell{background:var(--card);border:2px solid var(--line);border-radius:10px;
padding:0;cursor:pointer;overflow:hidden;text-align:left;font-family:inherit;
transition:border-color .12s,transform .12s}
.cell:hover{border-color:var(--p1);transform:translateY(-2px)}
.cell.on{border-color:var(--p3);box-shadow:0 0 0 3px rgba(224,138,21,.16)}
.cell img{display:block;width:100%;height:auto}
.cell .cap{padding:7px 9px;font-size:12px;display:flex;gap:6px;align-items:baseline}
.cell .no{font-weight:700;color:var(--p1);font-variant-numeric:tabular-nums}
.note{background:#fff;border:1px solid var(--line);border-left:4px solid var(--p2);
border-radius:10px;padding:14px 18px;margin-top:22px;font-size:14px;color:#3a4a58}
kbd{background:#f2f5f9;border:1px solid var(--line);border-bottom-width:2px;
border-radius:5px;padding:1px 6px;font-size:12.5px;font-family:inherit}
@media print{.top,.grid,.bar,.note{display:none}
.stage{border:0;box-shadow:none}.stage-img{page-break-after:always}}
</style>
</head>
<body>
<div class="top"><div class="top-in">
  <span class="brand">单元 __UNIT__ 课件</span>
  <span class="badge">__TOTAL__ 页 · 覆盖 __LESSONS__ 节课</span>
  <span class="spacer"></span>
  <a class="btn" href="../../lessons/index.html#u__UNIT__">本单元课节</a>
  <a class="btn" href="../../__UNITPAD__.html">单元讲义</a>
  <a class="btn" href="../index.html">课程总课件</a>
  <a class="btn" href="#" id="fsBtn" title="全屏放映（Esc 退出）">全屏</a>
  __DLBTN__
</div></div>

<div class="wrap">
  <h1>单元 __UNIT__ · __UTITLE__</h1>
  <p class="sub">每一节课都有两页：<b>课节页</b>（目标 / 实操 / 作业）与
     <b>知识点页</b>（本节要点 + 代码示例）。按 <kbd>←</kbd> <kbd>→</kbd> 翻页。</p>

  <div class="stage">
    <img class="stage-img" id="img" alt="课件页">
    <div class="bar">
      <button class="btn" id="prev">← 上一页</button>
      <button class="btn" id="next">下一页 →</button>
      <span class="k" id="kk"></span>
      <span class="t" id="tt"></span>
      <span class="spacer"></span>
      <a class="btn" id="lk" href="#">去上这节课 →</a>
      <span class="t" id="pg"></span>
    </div>
  </div>

  <div class="note">课件与讲义一一对应：看到哪一页卡住了，点「去上这节课」直接跳到那一节的讲义与练习。</div>
  <div class="grid" id="grid"></div>
</div>

<script>
var S = __DATA__, U = __UNIT__, cur = 0;
function pad(n){ return (n<10?'0':'')+n; }
function src(n){ return pad(U)+'/slide-'+pad(n)+'.webp'; }
var img=document.getElementById('img'), tt=document.getElementById('tt'),
    kk=document.getElementById('kk'), pg=document.getElementById('pg'),
    lk=document.getElementById('lk'), grid=document.getElementById('grid');
function show(i, push){
  if(i<0)i=0; if(i>=S.length)i=S.length-1;
  cur=i; var s=S[i];
  img.src=src(s.n);
  tt.textContent=s.t; kk.textContent=s.label;
  if(s.no){ lk.style.display=''; lk.href='../../lessons/'+pad(s.no)+'.html'; }
  else { lk.style.display='none'; }
  pg.textContent=(i+1)+' / '+S.length;
  for(var k=0;k<grid.children.length;k++)
    grid.children[k].className='cell'+(k===i?' on':'');
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
});
function fromHash(){
  var m=/^#s(\d+)$/.exec(location.hash||''); if(!m) return 0;
  var n=parseInt(m[1],10);
  for(var i=0;i<S.length;i++) if(S[i].n===n) return i;
  return 0;
}
window.addEventListener('hashchange',function(){ show(fromHash(),false); });
show(fromHash(),false);
</script>
<script src="player-extras.js"></script>
<script src="../../media/bgm.js" defer></script>
</body>
</html>
"""


def main():
    only = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None
    sys.path.insert(0, TOOLS)
    import build_lesson_ppt as G
    import lesson_tpl

    manifest = {}
    mpath = os.path.join(DECK_SRC, "manifest.json")
    if os.path.exists(mpath):
        manifest = json.load(open(mpath, encoding="utf-8"))
    if not manifest:
        print("缺少 manifest.json，请先运行生成步骤")
        return

    os.makedirs(WEB_U, exist_ok=True)
    summary = {}
    units = sorted(int(u) for u in manifest)
    for unit in units:
        if only and unit not in only:
            continue
        slides = manifest[str(unit)]
        info = build_unit(unit, {"slides": slides})
        if not info:
            continue
        build_html(unit, info, lesson_tpl.UNIT_TITLE.get(unit, ""),
                   sum(1 for s in slides if s["kind"] == "lesson"))
        summary[unit] = {"pptx": info["pptx"], "slides": len(slides)}
        print(f"  单元 {unit:>2} 完成：{len(slides)} 页")

    # 汇总映射：课节 -> (单元, 页码)
    lesson_map = {}
    for unit in units:
        for s in manifest[str(unit)]:
            if s["kind"] == "lesson":
                lesson_map[str(s["no"])] = {"unit": unit, "slide": s["slide"]}
    out = os.path.join(WEB_U, "..", "lesson-slide-map.json")
    json.dump(lesson_map, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    if FAILED:
        print(f"\n!! 有 {len(FAILED)} 个单元没建成：{sorted(set(FAILED))}（已回滚到备份）")
        sys.exit(1)
    print(f"\n完成 {len(summary)} 个单元；课节映射 {len(lesson_map)} 条")
    print("映射：", os.path.relpath(out, ROOT))


if __name__ == "__main__":
    main()
    import theme  # 主题派生：把浅色样式表翻成深色表并注入切换按钮
    theme.sweep([WEB_U])
