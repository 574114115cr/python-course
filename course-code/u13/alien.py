# alien.py —— 表示单个外星人的类
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"   # 自测不需要真实显示器

import pygame
from pygame.sprite import Sprite


class Alien(Sprite):
    """表示单个外星人的类。"""

    def __init__(self, ai_game):
        """初始化外星人并设置其起始位置。"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # 加载外星人图像；没有图片文件时生成一张占位图
        if not os.path.exists("images/alien.bmp"):
            os.makedirs("images", exist_ok=True)
            placeholder = pygame.Surface((60, 58))
            placeholder.fill((80, 200, 120))
            pygame.image.save(placeholder, "images/alien.bmp")
        self.image = pygame.image.load("images/alien.bmp")
        self.rect = self.image.get_rect()

        # 初始位置在屏幕左上角附近，留出一个身位
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # 用浮点数记录水平位置
        self.x = float(self.rect.x)

    def check_edges(self):
        """如果外星人位于屏幕边缘，就返回 True。"""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)

    def update(self):
        """向左或向右移动外星人。"""
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x


if __name__ == "__main__":
    # 自测：不打开真实窗口，验证边缘检测和左右移动
    import pygame

    pygame.init()

    class StubSettings:
        alien_speed = 1.0
        fleet_direction = 1
        fleet_drop_speed = 10

    class StubGame:
        settings = StubSettings()
        screen = pygame.display.set_mode((800, 600))

    game = StubGame()
    alien = Alien(game)
    print("初始位置：x =", alien.rect.x, "y =", alien.rect.y)
    print("是否精灵：", isinstance(alien, Sprite))

    # 边缘检测：中间 False，左边缘 True，右边缘 True
    alien.rect.x = 370
    print("x=370 时 check_edges：", alien.check_edges())
    alien.rect.x = 0
    alien.x = 0.0
    print("x=0 时 check_edges：", alien.check_edges())
    alien.rect.x = 800 - 60
    alien.x = float(alien.rect.x)
    print("x=740 时 check_edges：", alien.check_edges())

    # 方向为 1 向右，改成 -1 向左
    alien.rect.x = 100
    alien.x = 100.0
    alien.update()
    print("fleet_direction=1 移动一次后 x：", alien.rect.x)
    game.settings.fleet_direction = -1
    alien.update()
    print("fleet_direction=-1 移动一次后 x：", alien.rect.x)

    # 清理自测生成的占位图（跑完可以删掉）
    if os.path.exists("images/alien.bmp"):
        os.remove("images/alien.bmp")
        if not os.listdir("images"):
            os.rmdir("images")
        print("已清理占位图片")
