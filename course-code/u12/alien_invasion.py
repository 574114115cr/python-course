# alien_invasion.py —— 《外星人入侵》最小骨架：能开窗、能关闭、有背景色
# 运行：SDL_VIDEODRIVER=dummy python alien_invasion.py（有桌面环境可去掉前缀）
import sys

import pygame


class Settings:
    """简化版设置类（真实项目里这一整块搬去 settings.py）。"""

    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)


class AlienInvasion:
    """管理游戏资源和行为的类。"""

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.clock = pygame.time.Clock()

        # 创建 800x600 的窗口，并设置标题
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

    def run_game(self):
        """开始游戏的主循环。"""
        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """响应按键和鼠标事件。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕。"""
        self.screen.fill(self.settings.bg_color)   # 每帧重刷背景
        pygame.display.flip()                      # 让最近绘制的屏幕可见


if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()
