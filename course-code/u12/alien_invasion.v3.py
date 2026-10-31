# alien_invasion.py —— 支持数字键切换背景色
import sys

import pygame


class Settings:
    """带三套候选背景色的设置类。"""

    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)
        # 有哪些颜色，归 Settings 管，不写在事件处理里
        self.bg_options = {
            pygame.K_1: (230, 230, 230),
            pygame.K_2: (0, 0, 0),
            pygame.K_3: (20, 40, 80),
        }


class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

    def run_game(self):
        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_q:
            sys.exit()
        elif event.key in self.settings.bg_options:
            self.settings.bg_color = self.settings.bg_options[event.key]
            print(f"背景色切换为: {self.settings.bg_color}")

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        pygame.display.flip()


if __name__ == "__main__":
    AlienInvasion().run_game()
