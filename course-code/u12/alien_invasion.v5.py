# alien_invasion.py —— 重构后：主循环只剩四行
import sys

import pygame


class CleanGame:
    def __init__(self):
        pygame.init()
        self.settings_bg = (230, 230, 230)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))

    def run_game(self):
        """主循环保持'薄'：只负责按顺序点名。"""
        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """所有事件相关的逻辑都下沉到这里。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit()

    def _update_screen(self):
        """所有绘制相关的逻辑都下沉到这里。"""
        self.screen.fill(self.settings_bg)
        pygame.display.flip()


if __name__ == "__main__":
    CleanGame().run_game()
