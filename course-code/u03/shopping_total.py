# shopping_total.py —— 用元组解包遍历商品

# 列表的每个元素是一个元组：(名称, 单价)
products = [("键盘", 299), ("鼠标", 129), ("显示器", 1899)]

# for 循环直接解包元组：两个变量依次接住元组的第0、第1 个元素
total = 0
for name, price in products:
    print(f"{name}：{price} 元")
    total += price

print("原价合计：", total, "元")       # 2327 元

# 超过 1000 就打折
if total > 1000:
    print("总价超过 1000 元，享受 9 折优惠！")
    discounted = total * 0.9
    print(f"折后价格：{discounted:.2f} 元")    # 2094.30 元
else:
    print("总价不足 1000 元，无优惠")

# 顺带演示：排序后遍历（按价格从高到低）
print("按价格从高到低：")
for name, price in sorted(products, key=lambda item: item[1], reverse=True):
    print(f"  {name}: {price}")
