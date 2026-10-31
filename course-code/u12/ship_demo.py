# ship_demo.py —— 飞船撞右边界就停（复用示例 4 的 Ship）
import sys
import time

import pygame

from ship import Ship


class ShipDemo:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("撞墙就停")
        self.bg_color = (230, 230, 230)

        # 准备一个"假游戏"对象喂给 Ship（Ship 只用 screen 和 settings）
        class StubSettings:
            ship_speed = 2

        class FakeGame:
            screen = self.screen
            settings = StubSettings()

        self.ship = Ship(FakeGame())
        self.ship.moving_right = True     # 相当于一开始就按住右方向键
        self.reported = False

    def run(self):
        start = time.perf_counter()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    return

            # 到边界时报告一次（Ship.update 已保证位置不再变化）
            if not self.reported and self.ship.rect.right >= 800:
                print("已到达右边界")
                self.reported = True

            self.ship.update()
            self.screen.fill(self.bg_color)
            self.ship.blitme()
            pygame.display.flip()
            self.clock.tick(60)

            if time.perf_counter() - start > 5:
                print("最终 rect.x =", self.ship.rect.x)
                return


if __name__ == "__main__":
    ShipDemo().run()
    pygame.quit()
