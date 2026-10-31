# alien_invasion.py —— 只贴出与帧率显示相关的部分
import pygame


class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.last_report = pygame.time.get_ticks()   # 上次报告帧率的时刻

    def run_game(self):
        while True:
            self._check_events()
            self._update_screen()
            self.clock.tick(60)
            self._report_fps()          # 新增：报告帧率

    def _report_fps(self):
        """每秒打印一次实际帧率。"""
        now = pygame.time.get_ticks()
        if now - self.last_report >= 1000:
            print(f"当前帧率: {self.clock.get_fps():.1f} FPS")
            self.last_report = now
