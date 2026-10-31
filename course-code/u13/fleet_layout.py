# fleet_layout.py —— 只算数量，不画图
SCREEN_W, SCREEN_H = 1200, 800
ALIEN_W, ALIEN_H = 60, 50
SHIP_H = 60


def layout(per_row_delta=0, rows_delta=0):
    # 和 Settings 里的算法一致：左右各留一个身位，纵向留 3 行给飞船和边距
    avail_x = SCREEN_W - 2 * ALIEN_W
    per_row = avail_x // (2 * ALIEN_W) + per_row_delta
    avail_y = SCREEN_H - 3 * ALIEN_H - SHIP_H
    rows = avail_y // (2 * ALIEN_H) + rows_delta
    return per_row, rows, per_row * rows


before = layout()
after = layout(-1, -1)
print(f"改动前：每行 {before[0]} 个，{before[1]} 行，共 {before[2]} 个")
print(f"改动后：每行 {after[0]} 个，{after[1]} 行，共 {after[2]} 个")
print(f"少了 {before[2] - after[2]} 个外星人（{(before[2]-after[2])/before[2]:.0%}）")
