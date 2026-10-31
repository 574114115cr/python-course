# stack_sim.py —— 用列表实现"后进先出"的栈

cart = []

# 入栈：用 append 放到末尾
cart.append("手机")
cart.append("耳机")
cart.append("充电器")
print("加入商品后：", cart)        # ['手机', '耳机', '充电器']

# 出栈：用 pop 从末尾取出，取出的值存入变量
popped = cart.pop()
print("结账取出：", popped)        # 充电器（最后加入的先出来）
print("剩余：", cart)              # ['手机', '耳机']

# 再弹一次
popped2 = cart.pop()
print("再次取出：", popped2)       # 耳机
print("剩余：", cart)              # ['手机']

# 统计一共弹出了几个：初始长度 3，现在长度 1，所以弹出了 2 个
initial = 3
print("弹出总数：", initial - len(cart))      # 2

# 空列表再 pop 会报 IndexError，所以要先检查
if cart:
    cart.pop()
    print("弹出后：", cart)
else:
    print("购物车已经是空的，不能再弹出")
