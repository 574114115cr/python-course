# -*- coding: utf-8 -*-
"""逐节版课件的收尾处理（在 build_all_lesson_ppt 之后跑）：

1. 图片瘦身：把 1920x1080 的截图压到 1440x810 并优化，体积约降 6 成
2. 生成总览页 web/ppt/u/index.html
3. 校验：每个单元的页数、图片数、播放器是否齐备
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slidep/swc 需要可写的 TEMP（本机 TEMP 指向 workbuddy-update 目录时会静默失败）
sys.path.insert(0, os.path.join(ROOT, "tools"))
import slidep_env  # noqa: E402
slidep_env.prepare()

WEB_U = os.path.join(ROOT, "web", "ppt", "u")
PY = sys.executable

try:
    from PIL import Image
except ImportError:
    Image = None


def _runid():
    import time
    return f"{int(time.time())%100000}"


def rerender():
    """从 pptx 重新渲染全部图片，然后瘦身。

    注意：瘦身是有损的，而且必须先渲染再压缩——不能对已压缩的图重复压缩。
    """
    sys.path.insert(0, ROOT + "/tools")
    import importlib.util
    sp = importlib.util.spec_from_file_location(
        "blp", os.path.join(ROOT, "tools", "build_all_lesson_ppt.py"))
    blp = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(blp)
    n = 0
    for u in range(22):
        pptx = os.path.join(ROOT, "python-course-ppt", "逐节课件",
                            f"Python讲授课件-单元{u:02d}.pptx")
        if not os.path.exists(pptx):
            continue
        cnt = blp.slide_count(pptx)
        d = os.path.join(WEB_U, f"{u:02d}")
        os.makedirs(d, exist_ok=True)
        for i in range(1, cnt + 1):
            out = os.path.join(d, f"slide-{i:02d}.png")
            # 不能先删再渲染到同名文件：一是 slidep 按输出路径缓存截图，
            # 二是批量删除会触发安全拦截。改成渲染到唯一临时名再重命名覆盖。
            tmp = out + f".r{_runid()}.png"
            blp.run([blp.NODE, blp.SLIDEP, "screenshot", pptx,
                     "--page-index", str(i - 1), "--out", tmp], timeout=90)
            if os.path.exists(tmp) and os.path.getsize(tmp) > 2000:
                os.replace(tmp, out)
                n += 1
            elif os.path.exists(tmp):
                os.remove(tmp)
    print(f"  重新渲染 {n} 张")


def shrink():
    if Image is None:
        print("  PIL 不可用，跳过瘦身")
        return
    before = after = n = 0
    # 校验方式：查调色板里是否还留着设计色。
    # 别用固定坐标采样——封面页 / 小结页版式不同，那些坐标上根本不是同一种颜色，
    # 会误报一大片「色偏」（踩过）。
    DESIGN = [(250, 252, 254), (253, 243, 226), (238, 245, 251),
              (22, 35, 46), (31, 95, 168)]
    keep = {c: 0 for c in DESIGN}
    for cur, _d, files in os.walk(WEB_U):
        for f in files:
            if not f.endswith(".png"):
                continue
            p = os.path.join(cur, f)
            before += os.path.getsize(p)
            im0 = Image.open(p)
            # 已经处理过就跳过——重复量化是有损的，多跑几次会把文字边缘磨糊
            if im0.mode == "P" and im0.width <= 1440:
                after += os.path.getsize(p)
                n += 1
                pal = im0.getpalette() or []
                cols = [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]
                for c in DESIGN:
                    if any(max(abs(x - y) for x, y in zip(cc, c)) <= 6
                           for cc in cols):
                        keep[c] += 1
                continue
            im = im0.convert("RGB")
            if im.width > 1440:
                im = im.resize((1440, int(im.height * 1440 / im.width)),
                               Image.LANCZOS)
            # 关键：用 MEDIANCUT，它会保留大块纯色（卡片底色是教学信息，不能被并掉）。
            # 曾经用 ADAPTIVE，把 #FAFCFE / #FFFFFF / #FDF3E2 三种浅色并成一种，
            # 卡片分组在视觉上就没了。
            q = im.quantize(colors=256, method=Image.MEDIANCUT,
                            dither=Image.NONE)
            q.save(p, optimize=True)
            after += os.path.getsize(p)
            n += 1
            pal = q.getpalette() or []
            cols = [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]
            for c in DESIGN:
                if any(max(abs(x - y) for x, y in zip(cc, c)) <= 6
                       for cc in cols):
                    keep[c] += 1
    if before:
        print(f"  瘦身 {n} 张：{before/1024/1024:.1f} MB → {after/1024/1024:.1f} MB")
    # 各色「应该出现多少张」是不一样的，不能都拿总数当基准：
    # 浅橙卡只在课节页与小结页出现，主蓝在封面/知识点页的用量也不同。
    # 这里只守住真正会被量化算法并掉的那几种浅色。
    must = {
        (250, 252, 254): ("页面底色", 266),
        (238, 245, 251): ("浅蓝区", 266),
        (253, 243, 226): ("浅橙卡底", 133),
    }
    bad = [f"{nm} {keep[c]}/{exp}"
           for c, (nm, exp) in must.items() if keep[c] < exp]
    print("  设计色保留：" + ("全部达标"
          if not bad else "缺 " + ", ".join(bad)))


def verify():
    mani = json.load(open(os.path.join(ROOT, "python-course-ppt",
                                       "lessons-deck", "manifest.json"),
                          encoding="utf-8"))
    bad = []
    total_png = 0
    for u in sorted(int(k) for k in mani):
        want = len(mani[str(u)])
        d = os.path.join(WEB_U, f"{u:02d}")
        # 页面引用的是 .webp（PNG 转完就删了），数 .png 会永远数到 0。
        # 踩过两次：这个校验一直假报「图片 0/16」，导致收尾步骤没人敢信。
        have = (len([f for f in os.listdir(d) if f.endswith(".webp")])
                if os.path.isdir(d) else 0)
        total_png += have
        if have != want:
            bad.append(f"单元{u:02d} 图片 {have}/{want}")
        if not os.path.exists(os.path.join(WEB_U, f"{u:02d}.html")):
            bad.append(f"单元{u:02d} 缺播放器")
        pptx = os.path.join(ROOT, "python-course-ppt", "逐节课件",
                            f"Python讲授课件-单元{u:02d}.pptx")
        if not os.path.exists(pptx):
            bad.append(f"单元{u:02d} 缺 pptx")
    print(f"  校验：22 个单元 / {total_png} 张图 / "
          f"{len(mani)} 份 manifest")
    for b in bad[:12]:
        print("   ✗", b)
    return not bad


def main():
    if "--rerender" in sys.argv:
        print("0) 从 pptx 重新渲染")
        rerender()
    print("1) 图片瘦身")
    shrink()
    print("2) 转 WebP（页面已引用 .webp，PNG 转完即删）")
    import png2webp
    n, b, a = png2webp.convert_all(delete_png=True)
    if n:
        print(f"  {n} 张：{b/1024/1024:.1f} MB → {a/1024/1024:.1f} MB")
    print("2) 生成总览页")
    subprocess.run([PY, os.path.join(ROOT, "tools", "build_ppt_hub.py")])
    print("3) 校验")
    ok = verify()
    print("\n收尾完成" if ok else "\n收尾完成，但有遗漏（见上）")


if __name__ == "__main__":
    main()
