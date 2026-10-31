# place_rect.py —— 按钮定位函数
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


def place_rect(rect, screen_rect, position):
    """把 rect 摆到 screen_rect 的对应位置，四周留 20 像素边距。"""
    if position == "center":
        rect.center = screen_rect.center
    elif position == "bottom_right":
        rect.right = screen_rect.right - 20
        rect.bottom = screen_rect.bottom - 20
    elif position == "top_left":
        rect.left = 20
        rect.top = 20
    else:
        raise ValueError(f"未知位置: {position}")
    return rect


pygame.init()
screen_rect = pygame.display.set_mode((800, 600)).get_rect()

play = place_rect(pygame.Rect(0, 0, 200, 50), screen_rect, "center")
quit_btn = place_rect(pygame.Rect(0, 0, 200, 50), screen_rect, "bottom_right")
help_btn = place_rect(pygame.Rect(0, 0, 200, 50), screen_rect, "top_left")

buttons = [("Play", play), ("Quit", quit_btn), ("Help", help_btn)]
for name, rect in buttons:
    print(f"{name}: rect={rect}, 中心={rect.center}")

print("\n--- 点击判定 ---")
for name, rect in buttons:
    hit_self = rect.collidepoint(rect.center)
    others = [r for n, r in buttons if r is not rect]
    hit_other = any(r.collidepoint(rect.center) for r in others)
    print(f"  点 {name} 中心：命中自己={hit_self}，误伤别人={hit_other}")

# 无法识别的位置必须报错
try:
    place_rect(pygame.Rect(0, 0, 10, 10), screen_rect, "middle")
except ValueError as error:
    print(f"\n错误处理正常：{error}")

pygame.quit()
