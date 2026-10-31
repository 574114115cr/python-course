# three_projects_core.py —— 三期项目各抽一个纯函数，用 assert 自测
from datetime import datetime


# ===== 项目 1：飞船移动的边界钳制（不碰 pygame 也能测）=====
def move_ship(x, speed, width, screen_width, moving_right):
    """返回移动后的 x；碰到左右边缘就停下，不许飞出屏幕。"""
    x += speed if moving_right else -speed
    if x + width >= screen_width:
        return screen_width - width
    if x <= 0:
        return 0
    return x


# ===== 项目 1：子弹和外星人的矩形相交 =====
def rects_hit(a, b):
    """a、b 是 (x, y, w, h)；返回 True 表示两个矩形有重叠。"""
    return (a[0] < b[0] + b[2] and a[0] + a[2] > b[0]
            and a[1] < b[1] + b[3] and a[1] + a[3] > b[1])


# ===== 项目 2：CSV 数据按年统计最高温 =====
def yearly_max(rows, column="TMAX"):
    """rows 是 (日期字符串, 温度的字符串或 None) 的列表。"""
    best = {}
    for date_text, value in rows:
        try:
            high = int(value)
        except (TypeError, ValueError):
            continue                       # 缺失值跳过，但要记数见调用方
        year = datetime.strptime(date_text, "%Y-%m-%d").year
        if year not in best or high > best[year]:
            best[year] = high
    return dict(sorted(best.items()))


# ===== 项目 3：数据归属判断（Django 的 is_owner 纯逻辑版）=====
def is_owner(resource, user):
    """resource 是 {"owner": "alice"} 这样的字典；未登录一律 False。"""
    if user is None or not user.get("is_authenticated"):
        return False
    return resource.get("owner") == user["username"]


# ================= 以下全是测试，没有一行需要外部库 =================
ship = 0
print("=== 飞船边界钳制（屏幕宽 800，飞船宽 60，速度 5）===")
position = 700
right_trail = [position]
for _ in range(10):
    position = move_ship(position, 5, 60, 800, True)
    right_trail.append(position)
print(f"  从 700 一路向右走 10 步：{right_trail}")
position = 20
left_trail = [position]
for _ in range(5):
    position = move_ship(position, 5, 60, 800, False)
    left_trail.append(position)
print(f"  从 20 一路向左走 5 步：{left_trail}")
assert max(right_trail) == 740                     # 右边缘被钳住：800-60
assert min(left_trail) == 0                        # 左边缘被钳住
assert move_ship(100, 5, 60, 800, True) == 105     # 中间正常移动

print("\n=== 矩形相交（子弹 3x15，外星人 50x40）===")
bullet = (400, 500, 3, 15)
for alien in [(400, 520, 50, 40), (400, 480, 50, 40), (300, 500, 50, 40)]:
    print(f"  子弹{bullet} vs 外星人{alien} -> {rects_hit(bullet, alien)}")
assert rects_hit(bullet, (400, 490, 50, 40)) is True     # 有重叠
assert rects_hit(bullet, (400, 515, 50, 40)) is False    # 刚好错开 1 像素以上
assert rects_hit(bullet, (500, 500, 50, 40)) is False    # 横向不重叠

print("\n=== CSV 按年统计 ===")
rows = [("2021-01-01", "71"), ("2021-07-11", "128"), ("2021-12-31", "64"),
        ("2022-06-17", ""), ("2022-07-09", "127"), ("2022-08-01", None)]
print("  ", yearly_max(rows))
assert yearly_max(rows) == {2021: 128, 2022: 127}
assert yearly_max([]) == {}                              # 空输入不炸

print("\n=== 数据归属判断 ===")
alice = {"username": "alice", "is_authenticated": True}
bob = {"username": "bob", "is_authenticated": True}
topic = {"owner": "alice"}
for who in (alice, bob, {"username": "carol", "is_authenticated": False}, None):
    label = "未登录" if who is None else f"{who['username']}(登录={who['is_authenticated']})"
    print(f"  {label:<20} 能看 alice 的主题？{is_owner(topic, who)}")
assert is_owner(topic, alice) is True
assert is_owner(topic, bob) is False
assert is_owner(topic, None) is False

print("\n全部 assert 通过：这 4 个函数可以直接写进 pytest，不用开窗口、不用连库。")
