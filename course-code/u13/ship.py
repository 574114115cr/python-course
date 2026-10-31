# ship.py —— 单元 13 版的飞船类（相比单元 12 的两处改动已标注）
import pygame
from pygame.sprite import Sprite


class Ship(Sprite):                      # 改动一：继承 Sprite
    """管理飞船的类。"""

    def __init__(self, ai_game):
        super().__init__()               # 改动一（续）：必须调用
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        try:
            self.image = pygame.image.load("images/ship.bmp")
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((60, 48))
            self.image.fill((70, 130, 180))
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom

        self.x = float(self.rect.x)
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """根据移动标志调整飞船的位置，并限制在屏幕内。"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        self.rect.x = self.x

    def blitme(self):
        """在指定位置绘制飞船。"""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):               # 改动二：新增
        """让飞船回到屏幕底部中央。"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
