# edge_check.py —— 边缘检测逻辑（无需 pygame）


class FakeRect:
    """模拟 pygame.Rect 的 x / right / left。"""

    def __init__(self, x, width):
        self.x = float(x)
        self.width = width

    @property
    def right(self):
        return self.x + self.width

    @property
    def left(self):
        return self.x


class Alien:
    def __init__(self, x):
        self.rect = FakeRect(x, 60)      # 外星人宽 60

    def check_edges(self, screen_width=800):
        screen_rect = FakeRect(0, screen_width)
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)


for x, expect in [(0, True), (740, True), (370, False), (741, True)]:
    result = Alien(x).check_edges()
    print(f"x={x:>3} → check_edges={result}（期望 {expect}）",
          "PASS" if result == expect else "FAIL")

print("解释：用 >= 和 <= 是因为'刚好贴上边缘'也算到边；"
      "速度大于 1 时可能一步跨过精确坐标，用 == 会漏判。")
