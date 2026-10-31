# ships_demo.py —— 用 Group + Ship 在左上角画"剩余命数"图标
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from pygame.sprite import Group, Sprite


class Ship(Sprite):
    """简化版飞船：只有 rect 和一张纯色图像（用法和教材 Ship 一样）。"""

    def __init__(self):
        super().__init__()
        # 真实项目里这里是 pygame.image.load("images/ship.bmp")
        self.image = pygame.Surface((40, 24))
        self.image.fill((60, 60, 60))
        self.rect = self.image.get_rect()


class Scoreboard:
    def __init__(self, screen, ships_left):
        self.screen = screen
        self.prep_ships(ships_left)

    def prep_ships(self, ships_left):
        """把剩余命数画成左上角一排小飞船图标。"""
        self.ships = Group()
        for ship_number in range(ships_left):
            ship = Ship()
            ship.rect.x = 10 + ship_number * ship.rect.width   # 用图片宽度当间距
            ship.rect.y = 10
            self.ships.add(ship)

    def show_ships(self):
        self.ships.draw(self.screen)


pygame.init()
screen = pygame.display.set_mode((400, 120))

for lives in [3, 2, 0]:
    sb = Scoreboard(screen, lives)
    screen.fill((230, 230, 230))
    sb.show_ships()
    print(f"{lives} 条命：Group 里有 {len(sb.ships)} 个图标，"
          f"x 坐标 {[s.rect.x for s in sb.ships]}")

pygame.quit()
