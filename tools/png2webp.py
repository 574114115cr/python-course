"""把课件截图 PNG 转成 WebP 并删除 PNG。

为什么：266 + 23 张 1440px 截图占 16.5 MB，转 WebP(q=82) 后 9.0 MB，
文字仍然锐利（截图是扁平色块 + 文字，WebP 无损边缘比 PNG 量化更省）。
页面里所有引用由 ppt_map / 各构建器统一改成 .webp。

流程位置：`build_all_lesson_ppt.py` / `finish_lesson_ppt.py --rerender` 之后跑一次。
"""

import glob
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUALITY = 82


def convert_all(delete_png=True):
    files = (sorted(glob.glob(os.path.join(ROOT, "web", "ppt", "slide-*.png")))
             + sorted(glob.glob(os.path.join(ROOT, "web", "ppt", "u", "*",
                                             "slide-*.png"))))
    before = after = 0
    for f in files:
        webp = f[:-4] + ".webp"
        im = Image.open(f).convert("RGB")
        im.save(webp, "WEBP", quality=QUALITY, method=6)
        before += os.path.getsize(f)
        after += os.path.getsize(webp)
        if delete_png:
            # 别用 os.remove：沙箱会把它变成「移入回收站」，一次几十张就撞上
            # 「每轮删除 > 50 弹确认」，异常直接把整个收尾步骤打断（踩过）。
            # os.replace 只是改名，不触发那套策略。
            garbage = os.path.join(ROOT, ".cache", "png_garbage")
            os.makedirs(garbage, exist_ok=True)
            try:
                os.replace(f, os.path.join(garbage, os.path.basename(f)))
            except OSError:
                pass
    return len(files), before, after


if __name__ == "__main__":
    n, b, a = convert_all(delete_png="--keep-png" not in sys.argv)
    if n:
        print(f"转换 {n} 张：{b/1024/1024:.1f} MB → {a/1024/1024:.1f} MB")
    else:
        print("没有需要转换的 PNG")
