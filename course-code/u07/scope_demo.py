# scope_demo.py —— 全局变量与局部变量

name = "全局变量"


def show_variables():
    local_name = "局部变量"
    print("  函数内可以看全局：", name)
    print("  函数内可以看局部：", local_name)


show_variables()
# print(local_name)      # NameError: 局部变量出了函数就不存在了

# ===== 修改全局变量的三种方式 =====
count = 0

# 方式1：直接赋值 -> 只是新建了一个局部变量，全局没变
def way_one():
    count = 100
    print(f"  方式1 函数内 count = {count}")


way_one()
print("方式1 之后全局 count =", count, "\n")    # 0  没变

# 方式2：global 声明 -> 真能改，但官方不推荐
def way_two():
    global count
    count = 100
    print(f"  方式2 函数内 count = {count}")


way_two()
print("方式2 之后全局 count =", count, "\n")    # 100  改了

# 方式3（最佳）：把数据传进去，把结果返回出来
def add_to_count(amount, current):
    """不碰全局状态，纯靠参数和返回值。"""
    return current + amount


total = 100
total = add_to_count(50, total)      # 显式接住返回值
print("方式3 total =", total)         # 150

# 结论：能用参数和返回值解决的，绝不用 global
# 因为 global 让函数的"隐藏副作用"变多，代码会变得难追踪
