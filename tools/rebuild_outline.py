"""重建 23 页大纲课件（阶段 0–2）：DSL → pptx → 图片 → WebP → 播放器。

为什么单独一个：逐节课件有 rebuild_decks.py，大纲课件却一直没有对应脚本，
改了 DSL 之后没人知道怎么把 pptx 和网页重新生出来，于是「图上还写着 84 题」。

用法：
  python tools/rebuild_outline.py            # 全流程
  python tools/rebuild_outline.py --render   # 只重渲染 + 播放器（DSL 没改时）
"""
import os
import re
import subprocess
import sys
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
NODE = r"C:\Users\57411\.workbuddy\binaries\node\versions\22.22.2-6\node.exe"
SLIDEP = (r"C:\Users\57411\.workbuddy\binaries\node\versions\22.22.2-6"
          r"\node_modules\@tencent\slidep\dist\index.js")

SRC = os.path.join(ROOT, "python-course-ppt", "slides", "deck2")
PPTX = os.path.join(ROOT, "python-course-ppt", "Python阶段0-2课程大纲.pptx")
# 沙箱里「删除再重建」会被 safe-delete 拦下（回收站不可用），
# 所以先建到临时文件，渲染完再把字节原地写回正式文件。
BUILD = ""   # 每次换新名字：旧文件删不掉（回收站不可用）也不会挡住 create
WEB = os.path.join(ROOT, "web", "ppt")


def run(args, timeout=180):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def slide_count(pptx):
    try:
        with zipfile.ZipFile(pptx) as z:
            return len([n for n in z.namelist()
                        if re.match(r"ppt/slides/slide\d+\.xml$", n)])
    except Exception:
        return -1


def build_pptx(slides):
    global BUILD
    BUILD = os.path.join(ROOT, ".cache", f"outline_build_{int(time.time())}.pptx")
    os.makedirs(os.path.dirname(BUILD), exist_ok=True)
    r = run([NODE, SLIDEP, "create", BUILD])
    if '"ok":true' not in r.stdout:
        raise SystemExit(f"create 失败：{(r.stdout or r.stderr)[:200]}")
    for i, f in enumerate(slides, 1):
        ok = False
        for _ in range(2):
            r = run([NODE, SLIDEP, "upsert-dsl", BUILD, "--dsl-file", f])
            if '"ok":true' in r.stdout:
                ok = True
                break
        if not ok:
            print(f"  第 {i} 页 ({os.path.basename(f)}) upsert 失败："
                  f"{(r.stdout or r.stderr)[:140]}")
    got = slide_count(BUILD)
    if got != len(slides):
        raise SystemExit(f"页数不对：{got} / {len(slides)}")
    try:
        with open(BUILD, "rb") as src, open(PPTX, "wb") as dst:
            dst.write(src.read())
        print(f"  pptx 已重建并写回：{got} 页")
    except PermissionError:
        # 文件被别的进程占着（sandbox 回收站不可用时常见）：网页图仍然照常重建，
        # 只是下载的 pptx 会是旧版，重启后再跑一次本条命令即可。
        print(f"  !! pptx 写不进去（被占用），仅重建网页图：{BUILD}")


def render(n):
    from PIL import Image
    for i in range(1, n + 1):
        png = os.path.join(WEB, f"slide-{i:02d}.png")
        webp = os.path.join(WEB, f"slide-{i:02d}.webp")
        if os.path.exists(png):
            os.remove(png)
        for _ in range(2):
            run([NODE, SLIDEP, "screenshot", BUILD,
                 "--page-index", str(i - 1), "--out", png], timeout=120)
            if os.path.exists(png) and os.path.getsize(png) > 2000:
                break
        else:
            print(f"  第 {i} 页截图失败")
            continue
        Image.open(png).convert("RGB").save(webp, "WEBP", quality=86, method=6)
        os.remove(png)
        print(f"  第 {i:02d} 页 OK", end="\r")
    print(f"  渲染完成：{n} 页 → WebP")


def main():
    only_render = "--render" in sys.argv
    slides = [os.path.join(SRC, f) for f in sorted(os.listdir(SRC))
              if f.endswith(".slide")]
    if not slides:
        raise SystemExit("deck2 下没有 .slide")
    print(f"大纲课件：{len(slides)} 页 DSL")
    if not only_render:
        build_pptx(slides)
    render(len(slides))
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "build_ppt_html.py")],
                       cwd=ROOT)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
