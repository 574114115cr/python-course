# scoreboard_demo.py —— 数据与显示分离：prep_* 模式
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


class Settings:
    def __init__(self):
        self.bg_color = (230, 230, 230)
        self.ship_limit = 3
        self.alien_points = 50


class GameStats:
    """score/level/ships_left 每局重置，high_score 不清零。"""

    def __init__(self, settings):
        self.settings = settings
        self.reset_stats()
        self.high_score = 0
        self.game_active = False

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1


class Scoreboard:
    """把 stats 里的数据翻译成屏幕上的图像。"""

    def __init__(self, screen, settings, stats):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.settings = settings
        self.stats = stats
        self.font = pygame.font.SysFont(None, 48)
        self.prep_score()
        self.prep_high_score()
        self.prep_level()

    def _format(self, number):
        """舍入到十位 + 千分位。"""
        return "{:,}".format(round(number, -1))

    def prep_score(self):
        self.score_image = self.font.render(
            self._format(self.stats.score), True, (30, 30, 30),
            self.settings.bg_color)
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_score(self):
        self.high_score_image = self.font.render(
            self._format(self.stats.high_score), True, (30, 30, 30),
            self.settings.bg_color)
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = 20

    def prep_level(self):
        self.level_image = self.font.render(
            str(self.stats.level), True, (30, 30, 30),
            self.settings.bg_color)
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def check_high_score(self):
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def show_score(self):
        for image, rect in [(self.score_image, self.score_rect),
                            (self.high_score_image, self.high_score_rect),
                            (self.level_image, self.level_rect)]:
            self.screen.blit(image, rect)


pygame.init()
screen = pygame.display.set_mode((600, 200))
settings = Settings()
stats = GameStats(settings)
sb = Scoreboard(screen, settings, stats)

print("=== 刚开局 ===")
print(f"  得分: {stats.score}  最高分: {stats.high_score}  等级: {stats.level}")

print("\n=== 击落 2 只外星人：数据 +100，然后 prep_score() ===")
stats.score += settings.alien_points * 2
sb.prep_score()
sb.check_high_score()
print(f"  得分: {stats.score}  最高分: {stats.high_score}（新纪录诞生）")

print("\n★ 忘了 prep 会怎样：只改数据，不重新渲染 ===")
stats.score += 1000000
print(f"  stats.score 已经变成 {stats.score}，但屏幕上还是旧图像（显示 100）")
print("  => 数据归数据，显示归显示，桥梁是 prep_*()！")

sb.prep_score()
sb.check_high_score()
print(f"  补上 prep_score() 后，屏幕显示: {sb._format(stats.score)}")

print("\n=== 重置：再来一局 ===")
stats.reset_stats()
sb.prep_score()
sb.prep_level()
print(f"  score={stats.score}, level={stats.level}（都重置了）")
print(f"  high_score={stats.high_score}（没有清零！跨局记忆）")

pygame.quit()
