# return_demo.py —— return 的三个要点

# 有 return 和没 return 的差别
def with_return():
    return 42


def without_return():
    print("我执行了，但我什么都不返回")


print("with_return() 返回：", with_return())      # 42
print("without_return() 返回：", without_return())  # None

# return 之后立刻结束函数
def early_exit():
    return "这是第一个 return 的结果"
    print("这行永远不会执行")            # 死代码
    return "这行也永远不会执行"


print(early_exit())        # 这是第一个 return 的结果

# 一个函数可以有多个 return，但只会走一个
def classify_number(n):
    """判断正数、负数或零。"""
    if n > 0:
        return "正数"
    elif n < 0:
        return "负数"
    return "零"      # 注意：这行缩进和 if 平齐，不在 elif 里面


for value in [5, -3, 0]:
    print(f"{value} 是 {classify_number(value)}")

# 返回多个值：其实返回的是一个元组
def min_and_max(numbers):
    """返回最小值和最大值。"""
    return min(numbers), max(numbers)


smallest, largest = min_and_max([3, 9, 2, 7])
print(f"最小 {smallest}，最大 {largest}")

# 返回字典：适合"多个名字的东西"
def get_user():
    """返回用户信息的字典。"""
    return {"name": "小明", "age": 18}


user = get_user()
print(f"{user['name']}今年 {user['age']} 岁")

# 无 return 的隐式 None（容易踩坑）
def side_effect_only(numbers):
    """只打印不返回。"""
    for n in numbers:
        print(n)


result = side_effect_only([1, 2, 3])
print("返回值是：", result)      # None —— 所以别拿它参与运算
