# buggy_code.py —— INTENTIONALLY-BROKEN 演示用：4 处 bug，请自己发现
import pygame


def check_keydown(event, ship, bullets):
    """处理按键。"""
    if event.key == pygame.K_q:
        sys.exit()                      # bug 1：用了 sys.exit() 但没 import sys
    elif event.key == pygame.K_SPACE:
        bullets.add(Bullet(ship))       # bug 2：Bullet 类没定义、也没导入
    elif event.key == pygame.K_RIGHT:
        ship.moving_right = False       # bug 3：按右键反而停下，应该 = True


def update_aliens(aliens):
    """让整个舰队横向移动。"""
    for alien in aliens.sprites():
        alien.x += 1
    if len(aliens) == 0:
        game_active = False            # bug 4：只是定义了函数内的局部变量
