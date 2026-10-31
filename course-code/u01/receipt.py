# receipt.py —— 收银小票

# input() 返回的永远是字符串，必须显式转换才能做数值运算
product = input("请输入商品名称：")
price = float(input("请输入单价："))
quantity = int(input("请输入数量："))
discount = float(input("请输入折扣率（如 0.85 表示 85 折）："))

# 计算折后总价
total = price * quantity * discount

# 用 f-string 输出小票
print("=" * 30)
print(f"商品：{product}")
print(f"单价：{price:,.2f} 元")
print(f"数量：{quantity}")
print(f"折扣率：{discount}")
print(f"小计：{price * quantity:,.2f} 元")
print(f"应付：{total:,.2f} 元")
print("=" * 30)
