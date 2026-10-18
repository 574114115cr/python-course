# -*- coding: utf-8 -*-
"""生成 PWA 图标（标准 + maskable 两套，192/512）。

设计沿用站点 favicon：圆角方块 + 等宽字体 "Py"。
maskable 版按安全区（中心 80%）排版，任意形状裁切都不丢内容。

运行：venv python tools/build_pwa_icons.py
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pil_font import draw_centered, load_mono_font  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLUE = (31, 95, 168, 255)        # --p1 #1f5fa8
WHITE = (255, 255, 255, 255)


def text_center(draw, box, text, font):
    l, t, r, b = box
    draw_centered(draw, ((l + r) / 2, (t + b) / 2), text, font, WHITE)


def standard(size, path):
    """白底 + 蓝色圆角方块 + 白字 Py。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(size * 0.06)
    d.rounded_rectangle([pad, pad, size - pad, size - pad],
                        radius=int(size * 0.22), fill=BLUE)
    font = load_mono_font(int(size * 0.42))
    text_center(d, (0, 0, size, size), "Py", font)
    img.save(path)
    return path


def maskable(size, path):
    """全出血蓝底 + 白字 Py（文字在中心 80% 安全区内）。"""
    img = Image.new("RGBA", (size, size), BLUE)
    d = ImageDraw.Draw(img)
    font = load_mono_font(int(size * 0.36))
    text_center(d, (0, 0, size, size), "Py", font)
    img.save(path)
    return path


def main():
    out = []
    for s in (192, 512):
        out.append(standard(s, os.path.join(ROOT, f"icon-{s}.png")))
        out.append(maskable(s, os.path.join(ROOT, f"icon-maskable-{s}.png")))
    for p in out:
        print("生成", os.path.basename(p), os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
