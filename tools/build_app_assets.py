# -*- coding: utf-8 -*-
"""生成安卓原生图标与启动屏源图（供 @capacitor/assets 消费）。

产出（android/assets/）：
  icon.png   1024×1024  白底 + 蓝圆角方块 + 白字 Py（自适应图标前景）
  splash.png 2732×2732  蓝底 + 白字 Py（启动屏）

运行：venv python tools/build_app_assets.py
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pil_font import draw_centered, load_mono_font  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "android", "assets")
BLUE = (31, 95, 168, 255)
WHITE = (255, 255, 255, 255)


def icon(size, path):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(size * 0.08)
    d.rounded_rectangle([pad, pad, size - pad, size - pad],
                        radius=int(size * 0.22), fill=BLUE)
    font = load_mono_font(int(size * 0.40))
    draw_centered(d, (size / 2, size / 2), "Py", font, WHITE)
    img.save(path)


def splash(size, path):
    img = Image.new("RGBA", (size, size), BLUE)
    d = ImageDraw.Draw(img)
    font = load_mono_font(int(size * 0.22))
    draw_centered(d, (size / 2, size / 2), "Py", font, WHITE)
    img.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    icon(1024, os.path.join(OUT, "icon.png"))
    splash(2732, os.path.join(OUT, "splash.png"))
    for f in ("icon.png", "splash.png"):
        p = os.path.join(OUT, f)
        print("生成", f, os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
