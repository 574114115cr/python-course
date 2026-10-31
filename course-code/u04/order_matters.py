# order_matters.py —— elif 链的顺序为什么关键

age = 20

# ===== 错误顺序：条件从宽到窄 =====
print("--- 错误顺序 ---")
if age > 6:
    print("青少年")         # 20 > 6 成立，立刻执行，后面全部跳过
elif age > 18:
    print("成年")           # 永远执行不到
else:
    print("儿童")           # 也永远执行不到

# ===== 正确顺序：条件从窄到宽 =====
print("--- 正确顺序 ---")
if age > 18:
    print("成年")
elif age > 6:
    print("青少年")
else:
    print("儿童")

# 结论：if 链是"从上往下、命中即停"，所以最特殊的放最前面
