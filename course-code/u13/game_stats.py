# game_stats.py —— 跟踪游戏统计信息
class GameStats:
    """跟踪《外星人入侵》的统计信息。"""

    def __init__(self, ai_game):
        """初始化统计信息。"""
        self.settings = ai_game.settings
        self.reset_stats()
        # 游戏刚启动时处于活动状态
        self.game_active = True

    def reset_stats(self):
        """初始化在游戏运行期间可能变化的信息。"""
        self.ships_left = self.settings.ship_limit


if __name__ == "__main__":
    # 自测：用一个"假游戏"验证三条命的消耗过程
    class StubSettings:
        ship_limit = 3

    class StubGame:
        settings = StubSettings()

    stats = GameStats(StubGame())
    print("初始：ships_left =", stats.ships_left,
          "game_active =", stats.game_active)
    for i in range(1, 5):
        if stats.ships_left > 0:
            stats.ships_left -= 1
        if stats.ships_left == 0:
            stats.game_active = False
        print(f"第 {i} 次被撞后：ships_left = {stats.ships_left}，"
              f"game_active = {stats.game_active}")
