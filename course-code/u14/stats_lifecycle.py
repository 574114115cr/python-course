# stats_lifecycle.py —— GameStats 的生命周期：谁归 reset_stats 管


class Settings:
    def __init__(self):
        self.ship_limit = 3


class GameStats:
    def __init__(self, settings):
        self.settings = settings
        self.reset_stats()
        self.high_score = 0
        self.game_active = False

    def reset_stats(self):
        """只重置'一局内部'的数据。"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1


settings = Settings()
stats = GameStats(settings)

print("=== 构造完成 ===")
print(f"  score={stats.score}, level={stats.level}, "
      f"ships_left={stats.ships_left}, high_score={stats.high_score}, "
      f"game_active={stats.game_active}")

print("\n=== 模拟玩了一局：3000 分，4 级，剩 1 条命 ===")
stats.score = 3000
stats.level = 4
stats.ships_left = 1
stats.game_active = True
if stats.score > stats.high_score:      # 模拟 check_high_score
    stats.high_score = stats.score

print("\n=== reset_stats() 之后 ===")
stats.reset_stats()
print(f"  score={stats.score}, level={stats.level}, "
      f"ships_left={stats.ships_left}, high_score={stats.high_score}, "
      f"game_active={stats.game_active}")

print("\n=== 断言验收 ===")
assert stats.score == 0, "score 应该归零"
assert stats.level == 1, "level 应该归 1"
assert stats.ships_left == settings.ship_limit, "命数应该回满"
assert stats.game_active is True, "game_active 不归 reset_stats 管！"
assert stats.high_score == 3000, "最高分是跨局记忆，不能清零！"
print("  全部通过")
print("  归 reset_stats 管：ships_left / score / level")
print("  不归它管：high_score（跨局）和 game_active（事件驱动）")
