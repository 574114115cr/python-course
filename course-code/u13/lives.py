# lives.py —— 把 _ship_hit 的逻辑抽成纯函数，撞 4 次看状态
class GameStats:
    def __init__(self, limit=3):
        self.ships_limit = limit
        self.ships_left = limit
        self.game_active = True


def ship_hit(stats):
    """返回 False 表示这一撞被忽略（游戏已经结束）。"""
    if not stats.game_active:
        return False
    stats.ships_left -= 1
    if stats.ships_left <= 0:
        stats.game_active = False
    return True


st = GameStats()
for hit in range(1, 5):
    ok = ship_hit(st)
    print(f"第 {hit} 次撞击：ships_left={st.ships_left} game_active={st.game_active}"
          + ("" if ok else "  ← 已经结束，不再变化"))
