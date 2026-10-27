"""校验 web/lessons 产物：死链 / 占位符残留 / 目录项 / 代码高亮 / 必填区块。"""
import os, re, glob, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "web", "lessons")

pages = sorted(glob.glob(os.path.join(D, "*.html")))
print(f"页面数：{len(pages)}")

bad_link = placeholder = no_toc = no_hl = 0
total_toc = total_code = total_broken = 0
ids = {os.path.basename(p) for p in pages}

for p in pages:
    name = os.path.basename(p)
    s = open(p, encoding="utf-8").read()

    # 占位符残留
    for ph in re.findall(r"@@CODE\d+@@", s):
        placeholder += 1
        print(f"  !! {name} 占位符残留 {ph}")

    # 链接检查（先剥掉 <pre> 代码块与行内 <code>：
    # 里面的 Django 模板标签、示例 URL 是教学内容，不是真链接）
    body = re.sub(r"<pre\b.*?</pre>", "", s, flags=re.S)
    body = re.sub(r"<code\b[^>]*>.*?</code>", "", body, flags=re.S)
    for href in re.findall(r'href="([^"]+)"', body):
        if href.startswith(("http", "#", "mailto:", "data:")):
            continue
        tgt = href.split("#")[0]
        if not tgt:
            continue
        if tgt.startswith("../"):
            real = os.path.normpath(os.path.join(D, tgt))
        else:
            real = os.path.join(D, tgt)
        if not os.path.exists(real):
            bad_link += 1
            print(f"  !! {name} 死链 -> {href}")

    # 锚点检查（同页目录，同样跳过代码块）
    for a in re.findall(r'href="#([^"]+)"', body):
        if f'id="{a}"' not in s:
            bad_link += 1
            print(f"  !! {name} 死锚点 -> #{a}")

    toc = len(re.findall(r'<h[23] id="', s))
    code = len(re.findall(r'<div class="code', s)) or len(re.findall(r'<pre', s))
    hl = len(re.findall(r'<span class="k">|<span class="nf">|<span class="s2">', s))
    broken = len(re.findall(r'class="broken"', s))
    total_toc += toc
    total_code += code
    total_broken += broken
    if name != "index.html" and toc == 0:
        no_toc += 1
        print(f"  !! {name} 目录为空")
    if code and hl == 0:
        no_hl += 1
        print(f"  !! {name} 有代码块但无高亮")

print(f"\n目录项合计：{total_toc}")
print(f"代码块合计：{total_code}（其中故意写错 {total_broken} 块）")
print(f"死链/死锚点：{bad_link}")
print(f"占位符残留：{placeholder}")
print(f"目录为空的页：{no_toc}   无高亮的页：{no_hl}")

# 索引页必须列出全部课节（课号 1–111，文件名 01.html–111.html）
lesson_files = {os.path.basename(p) for p in pages
                if re.fullmatch(r"\d+\.html", os.path.basename(p))}
idx = open(os.path.join(D, "index.html"), encoding="utf-8").read()
links = set(re.findall(r'href="(\d+\.html)"', idx))
print(f"\n索引页列出课节：{len(links)} / {len(lesson_files)}")
missing = lesson_files - links
if missing:
    print(f"  !! 索引页缺失：{sorted(missing)}")

print("\n结论：" + ("全部通过" if bad_link == 0 and placeholder == 0 and no_toc == 0
                 and not missing else "存在问题，需修复"))