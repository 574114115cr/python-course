# button_demo.py —— Button 类完整实现，演示居中、绘制、点击判定
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


class Button:
    """居中的矩形按钮，自己渲染文字、自己绘制自己。"""

    def __init__(self, screen, msg):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.width, self.height = 200, 50
        self.button_color = (0, 135, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center
        self._prep_msg(msg)

    def _prep_msg(self, msg):
        self.msg_image = self.font.render(
            msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


pygame.init()
screen = pygame.display.set_mode((600, 400))
button = Button(screen, "Play")

screen.fill((230, 230, 230))
button.draw_button()
pygame.image.save(screen, "button_demo.png")

print(f"按钮矩形：{button.rect}")
print(f"按钮中心：{button.rect.center}，屏幕中心：{button.screen_rect.center}")
print(f"文字图像类型：{type(button.msg_image).__name__}（render 的产物，不是字符串）")

print("\n--- 点击判定 collidepoint ---")
for pos in [(300, 200), (300, 210), (10, 10), (400, 200)]:
    hit = button.rect.collidepoint(pos)
    print(f"鼠标在 {pos}：{'点中了按钮' if hit else '没点到'}")

pygame.quit()
# 跑完可以删掉 button_demo.png
