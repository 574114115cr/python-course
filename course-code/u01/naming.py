# naming.py —— 变量命名与重新赋值

# 好名字：全小写 + 下划线分隔 + 有具体含义
user_name = "张三"
total_price = 68.5
item_count = 4

print("用户：", user_name, "总价：", total_price)

# 重新赋值：变量名不变，指向的数据换了
total_price = total_price * item_count# 68.5 × 4 = 274.0
print("四个商品总价：", total_price)

# 一次赋给多个变量
x = y = 10# x 和 y 都指向整数 10
print("x =", x, "y =", y)

# 链式赋值：从右往左执行，等价于 total_price = total_price - 8
total_price -= 8
print("优惠后：", total_price)

# 以下写法会报错，实际动手试一遍
# 2nd_place = "亚军"    # 数字开头 -> SyntaxError
# my name = "张三"       # 有空格   -> SyntaxError
# class = "三班"         # 关键字   -> SyntaxError
