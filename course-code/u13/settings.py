# settings.py —— 单元 13 需要的完整设置
class Settings:
    """存储游戏《外星人入侵》所有设置的类。"""

    def __init__(self):
        # —— 屏幕设置 ——
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)

        # —— 飞船设置 ——
        self.ship_speed = 1.5
        self.ship_limit = 3                 # 每条命撞一次少一条

        # —— 子弹设置 ——
        self.bullet_speed = 2.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3            # 屏幕上最多同时存在 3 颗

        # —— 外星人设置 ——
        self.alien_speed = 1.0              # 舰队左右移动的速度
        self.fleet_direction = 1            # 1 向右，-1 向左
        self.fleet_drop_speed = 10          # 撞到边缘后整队下移的距离


if __name__ == "__main__":
    s = Settings()
    for name in ("screen_width", "screen_height", "bg_color", "ship_speed",
                 "ship_limit", "bullet_speed", "bullet_width", "bullet_height",
                 "bullet_color", "bullets_allowed", "alien_speed",
                 "fleet_direction", "fleet_drop_speed"):
        print(f"{name:18} = {getattr(s, name)}")
