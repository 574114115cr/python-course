# triangle.py —— 三角形判定

def classify_triangle(a, b, c):
    """根据三条边判断三角形类型。"""
    # 第一道关：是不是三角形。必须放在最前面，
    # 否则 1, 2, 100 这种数据会被误判成"普通三角形"
    if a + b <= c or a + c <= b or b + c <= a:
        return "不是三角形"
    elif a == b == c:
        # 三个都相等才是等边。等腰要放在等边后面判断，
        # 否则等边三角形也会被"任意两边相等"命中
        return "等边三角形"
    elif a == b or b == c or a == c:
        return "等腰三角形"
    else:
        return "普通三角形"


# 测试
test_cases = [
    (3, 3, 3),
    (5, 5, 8),
    (7, 10, 5),
    (1, 2, 3),
    (1, 2, 10),
]

for a, b, c in test_cases:
    print(f"边长 {a}, {b}, {c} -> {classify_triangle(a, b, c)}")

# 输出：
# 边长 3, 3, 3 -> 等边三角形
# 边长 5, 5, 8 -> 等腰三角形
# 边长 7, 10, 5 -> 普通三角形
# 边长 1, 2, 3 -> 不是三角形
# 边长 1, 2, 10 -> 不是三角形
