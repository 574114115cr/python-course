# bullet.py —— 管理飞船发射的子弹的类
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"   # 自测不需要真实显示器

import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """管理飞船发射的子弹的类。"""

    def __init__(self, ai_game):
        """在飞船的当前位置创建一颗子弹。"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # 先在 (0, 0) 处创建子弹矩形，再移动到飞船顶部
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
                                self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # 用浮点数记录纵坐标（Rect 的 y 只能是整数）
        self.y = float(self.rect.y)

    def update(self):
        """向上移动子弹。"""
        self.y -= self.settings.bullet_speed
        self.rect.y = self.y

    def draw_bullet(self):
        """在屏幕上绘制子弹。"""
        pygame.draw.rect(self.screen, self.color, self.rect)


if __name__ == "__main__":
    # 自测：不打开真实窗口，验证位置、移动和绘制
    import pygame

    pygame.init()

    class StubSettings:
        bullet_speed = 2.0
        bullet_width = 3
        bullet_height = 15
        bullet_color = (60, 60, 60)
        bullets_allowed = 3

    class StubShip:
        rect = pygame.Rect(400, 552, 60, 48)

    class StubGame:
        settings = StubSettings()
        screen = pygame.display.set_mode((800, 600))
        ship = StubShip()

    game = StubGame()
    bullet = Bullet(game)
    print("是否精灵：", isinstance(bullet, Sprite))
    print("初始 y：", bullet.y, "rect：", bullet.rect)
    for _ in range(3):
        bullet.update()
    print("update 3 次后 y：", bullet.y)
    bullet.draw_bullet()
    print("draw_bullet() 调用成功")
