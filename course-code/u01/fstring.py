# fstring.py —— f-string：把变量嵌进文字里的最佳方式

product = "机械键盘"
price = 499.5
quantity = 3
discount = 0.85
is_in_stock = True

total = price * quantity * discount

# 基础用法
print(f"商品：{product}")
print(f"单价：{price} 元")

# 花括号里可以放完整的表达式
print(f"总价：{price * quantity * discount:.2f} 元")

# 格式说明符：:.<宽度>.<小数位>f
print(f"|{product:<10}|")# 左对齐，占 10 字符宽
print(f"|{price:>10.2f}|")           # 右对齐，保留两位小数
print(f"|{product:^12}|")            # 居中

# 补零，常用于编号
code = 42
print(f"订单号：{code:05d}")          # 订单号：00042

# 千位分隔符
big = 1234567.891
print(f"金额：{big:,.2f} 元")         # 金额：1,234,567.89 元

# 让布尔值更易读
print(f"是否有货：{is_in_stock}")     # 是否有货：True
print(f"是否有货：{'有' if is_in_stock else '无'}")  # 是否有货：有

# 多行 f-string：括号里可以换行，不用反复 print
print(f"商品：{product}\n"
      f"单价：{price} 元\n"
      f"总价：{total:.2f} 元")
