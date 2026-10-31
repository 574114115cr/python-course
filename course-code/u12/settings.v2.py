# settings.py —— 增加子弹和外星人两组设置后的完整版
class Settings:
    """存储游戏《外星人入侵》所有设置的类。"""

    def __init__(self):
        # —— 屏幕设置 ——
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)

        # —— 飞船设置 ——
        self.ship_speed = 1.5

        # —— 子弹设置 ——
        self.bullet_speed = 2.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)

        # —— 外星人设置 ——
        self.alien_speed = 1.0
        self.fleet_direction = 1        # 1 表示向右移，-1 表示向左移

    def describe(self):
        return (
            f"窗口: {self.screen_width}x{self.screen_height}\n"
            f"背景色: {self.bg_color}\n"
            f"飞船速度: {self.ship_speed}\n"
            f"子弹: 速度{self.bullet_speed} "
            f"{self.bullet_width}x{self.bullet_height} {self.bullet_color}\n"
            f"外星人: 速度{self.alien_speed} 方向{self.fleet_direction}"
        )


if __name__ == "__main__":
    print(Settings().describe())
