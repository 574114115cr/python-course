# play_button_visibility.py —— Play 按钮显隐与光标切换
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


class Button:
    def __init__(self, screen, msg):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.width, self.height = 200, 50
        self.button_color = (0, 135, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center
        self.msg_image = self.font.render(
            msg, True, self.text_color, self.button_color)

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image.get_rect(
            center=self.rect.center))


class Stats:
    def __init__(self):
        self.game_active = False


pygame.init()
screen = pygame.display.set_mode((800, 500))
font = pygame.font.SysFont(None, 48)
play_button = Button(screen, "Play")
stats = Stats()


def update_screen():
    screen.fill((230, 230, 230))
    if not stats.game_active:
        # 未激活才画按钮；游戏结束后再画一行 Game Over
        play_button.draw_button()
        if stats.game_over_happened:
            text = font.render("Game Over", True, (135, 0, 0))
            screen.blit(text, (300, 320))
    pygame.display.flip()


# 光标状态与 game_active 严格同步
pygame.mouse.set_visible(not stats.game_active)
print(f"启动：game_active={stats.game_active}，"
      f"光标可见={not stats.game_active}")

stats.game_active = True
pygame.mouse.set_visible(not stats.game_active)
print(f"开始：game_active={stats.game_active}，"
      f"光标可见={not stats.game_active}")

stats.game_active = False
stats.game_over_happened = True      # 标记这一局结束过
pygame.mouse.set_visible(not stats.game_active)
print(f"结束：game_active={stats.game_active}，"
      f"光标可见={not stats.game_active}")
update_screen()

print("\n=== 坑点测试 ===")
print("如果把结束时的 set_visible(True) 注释掉：")
print("  游戏结束了，屏幕上只剩 Play 按钮，但鼠标光标凭空消失。")
print("  玩家：'我光标呢？？' 只能凭记忆盲点 Play，体验极差。")
print("  所以 set_visible 必须成对：True（等待）<-> False（游戏中）。")

pygame.quit()
