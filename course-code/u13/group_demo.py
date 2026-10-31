# group_demo.py —— 用 dummy 驱动演示 Group 的核心行为（无需真实显示器）
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from pygame.sprite import Group, Sprite, groupcollide, spritecollideany

pygame.init()
screen = pygame.display.set_mode((800, 600))


class Block(Sprite):
    """一个彩色小方块精灵：有 image（长相）和 rect（站位）。"""

    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = 0

    def update(self):
        """Group.update() 会自动调用每个成员的 update()。"""
        self.rect.x += self.vx

    def __repr__(self):
        return f"Block(x={self.rect.x}, y={self.rect.y})"


# 1）创建编组，放入 5 个精灵
blocks = Group()
for i in range(5):
    blocks.add(Block((200, 60, 60), 100 + i * 90, 100))
print("① 编组建好，成员数：", len(blocks))

# 2）批量更新：改一次速度，一次 update 全员生效
for block in blocks:
    block.vx = 10
blocks.update()
print("② update 后第一个方块的 x：", blocks.sprites()[0].rect.x)

# 3）批量绘制：把每个精灵的 image 画到屏幕上（dummy 下不可见但不报错）
blocks.draw(screen)
print("③ draw() 调用成功")

# 4）spritecollideany：单个精灵 vs 整个编组
runner = Block((60, 60, 200), 150, 100)
runner.vx = 20
for _ in range(10):
    runner.update()
    if spritecollideany(runner, blocks):
        break
print("④ spritecollideany 撞到了吗：", spritecollideany(runner, blocks) is not None)

# 5）groupcollide：两个编组互撞，两个 True 表示"碰撞后双方都消失"
enemies = Group()
for i in range(3):
    enemies.add(Block((60, 200, 60), 140 + i * 90, 100))
collisions = groupcollide(blocks, enemies, True, True)
print("⑤ groupcollide 撞掉了", len(collisions), "个；",
      "blocks 剩", len(blocks), "个，enemies 剩", len(enemies), "个")

# 6）empty()：一键清空
blocks.empty()
enemies.empty()
print("⑥ empty() 之后剩：", len(blocks), len(enemies))
