# group_basic.py —— 编组基本功（无需显示器）
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from pygame.sprite import Group, Sprite, groupcollide

pygame.init()


class Block(Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = 0

    def update(self):
        self.rect.x += self.vx


aliens = Group()
for i in range(5):
    aliens.add(Block((200, 60, 60), 100 + i * 90, 100))
print("① 加入 5 个外星人：", len(aliens))

for alien in aliens:
    alien.vx = 100
aliens.update()
print("② 全员右移 100 后，第一个的 x：", aliens.sprites()[0].rect.x)

# 3 颗子弹，故意和外星人重叠
bullets = Group()
for i in range(3):
    bullets.add(Block((60, 60, 200), 120 + i * 90, 100))

collisions = groupcollide(bullets, aliens, True, True)
print("③ 碰撞字典的键（被撞掉的外星人）：")
for key, value in collisions.items():
    print("   ", key, "被", len(value), "颗子弹命中")
print("   碰撞后外星人剩：", len(aliens), "，子弹剩：", len(bullets))

bullets.empty()
aliens.empty()
print("④ empty() 之后：", len(bullets), len(aliens))
