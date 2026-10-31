# ship.py —— 管理飞船的类（12.6 节完成时）
import pygame


class Ship:
    """管理飞船的类。"""

    def __init__(self, ai_game):
        """初始化飞船并设置其起始位置。"""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        # 教材使用 images/ship.bmp；加载失败时画一张占位图，保证代码可运行
        try:
            self.image = pygame.image.load("images/ship.bmp")
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((60, 48))
            self.image.fill((70, 130, 180))
        self.rect = self.image.get_rect()

        # 每艘新飞船都放在屏幕底部的中央
        self.rect.midbottom = self.screen_rect.midbottom

        # 浮点坐标：rect.x 只存整数，直接加 1.5 会被取整，所以单独记一份小数
        self.x = float(self.rect.x)

        # 移动标志：刚创建时两个都是 False，飞船不动
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """根据移动标志调整飞船的位置，并限制在屏幕内。"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # 把浮点坐标同步回矩形（Rect 会自动取整）
        self.rect.x = self.x

    def blitme(self):
        """在指定位置绘制飞船。"""
        self.screen.blit(self.image, self.rect)
