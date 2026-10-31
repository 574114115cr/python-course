# iteration_bug.py —— 复现"边遍历边删除"的漏删 bug


def make_bullets():
    """y <= 0 表示已飞出屏幕；故意让多个消失的子弹相邻。"""
    return [{"id": i, "y": y}
            for i, y in enumerate([100, -5, -5, 80, 60, -5, -5, -5, 40])]


# 错误写法：直接遍历并删除
bullets = make_bullets()
print("删除前：", [b["y"] for b in bullets])
for bullet in bullets:
    if bullet["y"] <= 0:
        bullets.remove(bullet)
print("错误写法删除后：", [b["y"] for b in bullets])
print("还剩几个 -5：", sum(1 for b in bullets if b["y"] <= 0))

# 正确写法：遍历副本
bullets = make_bullets()
for bullet in bullets.copy():
    if bullet["y"] <= 0:
        bullets.remove(bullet)
print("正确写法删除后：", [b["y"] for b in bullets])

print("结论：迭代器按序号走，删除会让后面的元素往前补位、被跳过；"
      "这和阶段 1 遍历字典时不能删键是同一个坑。")
