# report.py —— 列对齐报表

products = [
    ("机械键盘", 499.5, 12),
    ("人体工学鼠标", 129.0, 156),
    ("4K 显示器", 2399.0, 7),
]

# 表头：名称左对齐 12，单价右对齐 10，库存居中 6
print(f"{'商品名称':<10}|{'':>11}|{'库存':^6}|")
print("-" * 32)

# 遍历列表，按格式输出每一行
for name, price, stock in products:
    print(f"{name:<12}|{price:>10.2f}|{stock:^6}|")

# 计算库存总件数
total_stock = 0
for _, _, stock in products:
    total_stock += stock
print("-" * 32)
print(f"库存合计：{total_stock} 件")
