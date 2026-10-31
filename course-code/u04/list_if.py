# list_if.py —— if 与列表的三个组合
requested = ["蘑菇", "芝士", "榴莲"]
available = ["蘑菇", "芝士", "青椒"]

# ① 在不在名单里
for topping in requested:
    if topping in available:
        print(f"加 {topping}")
    else:
        print(f"没有 {topping}，这道跳过")

# ② 列表是不是空的：空列表直接当条件用
orders = []
if orders:
    print("有订单要处理")
else:
    print("购物车是空的")

# ③ 按多个条件筛选
nums = [12, 5, 30, 7, 18, 42]
big_even = [n for n in nums if n >= 10 and n % 2 == 0]
print("大于等于 10 的偶数", big_even)
