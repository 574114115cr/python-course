# dynamic_settings.py —— Settings 的"难度控制"部分 + 得分格式化


def format_score(score):
    """舍入到十位 + 千分位。"""
    return "{:,}".format(round(score, -1))


class Settings:
    def __init__(self):
        self.speedup_scale = 1.1     # 每升一级，速度 ×1.1
        self.score_scale = 1.5       # 每升一级，外星人分值 ×1.5
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """随游戏重置的动态设置，点 Play 时调用。"""
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.0
        self.alien_points = 50

    def increase_speed(self):
        """外星人编队被清空后调用：提速 + 加分。"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        # int() 截断小数：50 ×1.5 = 75.0，再 ×1.5 = 112.5 -> 112
        self.alien_points = int(self.alien_points * self.score_scale)


print("=== 得分格式化：round(x, -1) + 千分位 ===")
for score in [0, 50, 1230, 1234567, 999999990]:
    print(f"  stats.score = {score:>10}  ->  屏幕显示: {format_score(score)}")

print("\n=== 难度曲线：每级调用一次 increase_speed ===")
settings = Settings()
print(f"{'等级':>4}{'alien_speed':>14}{'bullet_speed':>15}{'alien_points':>14}")
print("-" * 50)
print(f"{1:>4}{settings.alien_speed:>14.2f}{settings.bullet_speed:>15.2f}"
      f"{settings.alien_points:>14}")
for level in range(2, 11):
    settings.increase_speed()
    print(f"{level:>4}{settings.alien_speed:>14.2f}{settings.bullet_speed:>15.2f}"
          f"{settings.alien_points:>14}")

settings.initialize_dynamic_settings()
print(f"\n重置后：alien_speed={settings.alien_speed}，"
      f"alien_points={settings.alien_points}（点 Play 再来一局）")
