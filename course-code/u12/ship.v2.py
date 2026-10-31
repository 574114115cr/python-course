# ship.py —— 支持四方向移动的飞船类
import pygame


class Ship:
    """管理飞船的类（四方向版）。"""

    def __init__(self, ai_game):
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

        # 两个方向各记一份浮点坐标
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # 四个移动标志，全部独立
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def update(self):
        """根据移动标志调整位置，四个边界都限制住。"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.ship_speed
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.ship_speed

        self.rect.x = self.x
        self.rect.y = self.y

    def blitme(self):
        self.screen.blit(self.image, self.rect)
