# calc_demo.py —— 认识变量赋值和基本运算

# 变量名 = 值，等号叫"赋值号"，把右边的东西交给左边的名字
price = 35.5        # 一个小数：单价 35.5 元
count = 3           # 一个整数：买了 3 个
total = price * count   # * 是乘法

print("单价：", price, "元")
print("数量：", count, "个")
print("总价：", total, "元")

# 变量可以被重新赋值，像一个可以反复贴标签的盒子
total = total - 5   # 抹掉零头，给 5 元优惠
print("优惠后总价：", total, "元")
