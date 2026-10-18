# -*- coding: utf-8 -*-
"""Pillow 跨平台等宽字体加载（图标/启动屏生成共用）。

为什么需要它：图标脚本原先只列了 Windows 的 Consolas 路径，
在 GitHub Actions（ubuntu-latest）上全部落空 → 退化成 Pillow 内置
bitmap 字体，1024px 图标上只画出11px 大的「Py」，且 bitmap 字体
的 getmask2 不支持 anchor，会直接抛错。

本模块按优先级探测真实 TTF；实在找不到才退到 load_default(size=)，
并对 anchor 不受支持的情况做降级绘制。
"""
import os

from PIL import ImageFont

# 按优先级排列：Windows Consolas → Linux DejaVu/Liberation → 通用兜底
FONT_CANDIDATES = [
    # Windows
    r"C:\Windows\Fonts\consolab.ttf",
    r"C:\Windows\Fonts\consola.ttf",
    # Linux（ubuntu-latest 自带 DejaVu 与 Liberation）
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    # macOS（本地备用）
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Courier New Bold.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
]


def load_mono_font(px):
    """返回 px 号等宽字体对象；找不到任何 TTF 时退到内置字体。"""
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, px)
            except OSError:
                pass
    try:
        # Pillow >= 10.1：load_default 支持 size，返回 FreeType 字体
        return ImageFont.load_default(size=px)
    except TypeError:
        return ImageFont.load_default()


def draw_centered(draw, xy, text, font, fill):
    """以 xy 为中心绘制文字。

    内置 bitmap 字体不支持 anchor='mm'，此时按字形包围盒手算偏移，
    保证任何环境下都不抛错、且文字仍在视觉中心。
    """
    try:
        draw.text(xy, text, font=font, fill=fill, anchor="mm")
        return
    except (ValueError, OSError):
        pass
    try:
        x0, y0, x1, y1 = font.getbbox(text)
        draw.text((xy[0] - (x1 + x0) / 2, xy[1] - (y1 + y0) / 2),
                  text, font=font, fill=fill)
    except (ValueError, OSError, AttributeError):
        draw.text(xy, text, font=font, fill=fill)