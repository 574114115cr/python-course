# state_machine_demo.py —— inactive <-> active 的完整状态转换
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


class Settings:
    def __init__(self):
        self.ship_limit = 3
        self.speedup_scale = 1.1
        self.score_scale = 1.5
        self.alien_points = 50
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        self.ship_speed = 1.5
        self.alien_points = 50


class GameStats:
    def __init__(self, settings):
        self.settings = settings
        self.reset_stats()
        self.high_score = 0
        self.game_active = False

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1


class Game:
    """迷你状态机游戏：点 Play 开始，被撞 3 次结束，可重开。"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 500))
        self.settings = Settings()
        self.stats = GameStats(self.settings)
        self.font = pygame.font.SysFont(None, 48)
        self.clock = pygame.time.Clock()
        # 按钮就是一个 Rect：屏幕正中的 200x50 矩形
        self.button_rect = pygame.Rect(0, 0, 200, 50)
        self.button_rect.center = self.screen.get_rect().center

    def _check_play_button(self, mouse_pos):
        """点 Play 且游戏未激活 -> 开始新的一局。"""
        if self.button_rect.collidepoint(mouse_pos) and not self.stats.game_active:
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            pygame.mouse.set_visible(False)
            print("  -> 游戏开始！game_active = True，光标已隐藏")

    def _ship_hit(self):
        self.stats.ships_left -= 1
        print(f"  -> 飞船被撞！剩余 {self.stats.ships_left} 条命")
        if self.stats.ships_left <= 0:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
            print("  -> 命用完了，game_active = False，光标恢复显示")

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._check_play_button(event.pos)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                return False
        return True

    def _update_screen(self):
        self.screen.fill((230, 230, 230))
        if self.stats.game_active:
            text = self.font.render(
                f"SCORE: {self.stats.score}", True, (30, 30, 30))
            self.screen.blit(text, (20, 20))
        else:
            # 未激活：画一个绿底"Play"按钮
            self.screen.fill((0, 135, 0), self.button_rect)
            msg = self.font.render("Play", True, (255, 255, 255), (0, 135, 0))
            self.screen.blit(msg, msg.get_rect(center=self.button_rect.center))
        pygame.display.flip()

    def run_game(self):
        print("游戏启动：game_active = False，等待玩家点 Play\n")
        # dummy 驱动收不到真实事件，预排 30 帧做演示；
        # 在你自己电脑上删掉 setdefault 两行，就能用真鼠标真键盘玩。
        plan = [
            (10, "click", (400, 250)),   # 点 Play（按钮中心）
            (12, "click", (50, 50)),     # 点空白处（不该有反应）
            (14, "hit", None),
            (16, "hit", None),
            (18, "hit", None),           # 撞三次 -> game over
            (20, "click", (400, 250)),   # 再点 Play -> 重开
        ]
        frame = 0
        running = True
        while running and frame < 30:
            for when, what, arg in plan:
                if frame == when:
                    if what == "click":
                        pygame.event.post(pygame.event.Event(
                            pygame.MOUSEBUTTONDOWN,
                            {"pos": arg, "button": 1}))
                        print(f"[第 {frame} 帧] 模拟鼠标点击 {arg}")
                    elif what == "hit" and self.stats.game_active:
                        print(f"[第 {frame} 帧] 模拟一次撞击")
                        self._ship_hit()
            running = self._check_events()
            if self.stats.game_active:
                self.stats.score += self.settings.alien_points
                if self.stats.score > self.stats.high_score:
                    self.stats.high_score = self.stats.score
            self._update_screen()
            self.clock.tick(60)
            frame += 1
        print(f"\n游戏循环结束：最终得分 {self.stats.score}，"
              f"最高分 {self.stats.high_score}")
        pygame.quit()


if __name__ == "__main__":
    Game().run_game()
