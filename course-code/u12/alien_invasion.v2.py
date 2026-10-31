# alien_invasion.py —— 《外星人入侵》主文件（12.6 节完成时）
# 依赖同目录下的 settings.py 和 ship.py
import sys

import pygame
from settings import Settings
from ship import Ship


class AlienInvasion:
    """管理游戏资源和行为的类。"""

    def __init__(self):
        """初始化游戏并创建资源。"""
        pygame.init()
        self.settings = Settings()
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

        # 创建飞船（传入 self，飞船就能拿到 screen 和 settings）
        self.ship = Ship(self)

    def run_game(self):
        """开始游戏的主循环。"""
        while True:
            self._check_events()
            self.ship.update()
            self._update_screen()
            self.clock.tick(60)

    # —— 事件处理 ——

    def _check_events(self):
        """响应按键和鼠标事件。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """响应按键。"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()

    def _check_keyup_events(self, event):
        """响应松键。"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    # —— 画面更新 ——

    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕。"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        pygame.display.flip()


if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()
