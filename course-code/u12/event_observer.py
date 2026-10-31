# event_observer.py —— 事件观察器：打印 pygame 取到的每一个事件
# 运行：SDL_VIDEODRIVER=dummy python event_observer.py
import sys
import time

import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("事件观察器")
clock = pygame.time.Clock()

start = time.perf_counter()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("收到 QUIT：用户点了关闭按钮")
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # event.key 是键的编号，用 pygame.key.name() 翻译成人类可读的名字
            print(f"收到 KEYDOWN：按下了 {pygame.key.name(event.key)}")
        elif event.type == pygame.KEYUP:
            print(f"收到 KEYUP：松开了 {pygame.key.name(event.key)}")

    # 8 秒后自动退出，避免无显示环境里死循环跑不完
    if time.perf_counter() - start > 8:
        print("演示时间到，自动退出。")
        break

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
