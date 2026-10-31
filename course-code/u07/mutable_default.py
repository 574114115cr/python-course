# mutable_default.py —— 默认参数不要用可变对象（重要坑）

# ===== 错误写法：默认参数用了列表 =====
def add_task(task, todo=[]):      # 注意这个 []
    """危险！默认列表只创建一次，所有调用共享它。"""
    todo.append(task)
    return todo


print(add_task("买菜"))     # ['买菜']
print(add_task("做饭"))     # ['买菜', '做饭']  <- 上次的"买菜"还在！
print(add_task("睡觉"))     # ['买菜', '做饭', '睡觉']

# 原因：默认参数在函数**定义时**只求值一次，
# 之后每次调用都用那同一份列表对象。

# ===== 正确写法1：用 None 作为默认值 =====
def add_task(task, todo=None):
    """默认值为 None，每次调用时再创建新列表。"""
    if todo is None:
        todo = []# 每次都新建一个，互不影响
    todo.append(task)
    return todo


print()
print(add_task("买菜"))     # ['买菜']
print(add_task("做饭"))     # ['做饭']  干净了

# ===== 正确写法2：用不可变类型 =====
def add_tag(tag, tags=()):        # 元组不可变，安全
    return tags + (tag,)


print()
print(add_tag("a"))     # ('a',)
print(add_tag("b"))     # ('b',)  独立

# ===== 默认参数还有另一个用途：让函数"记住"状态 =====
# 这是少数"用可变默认值"是合理的场景
def make_counter(start=0):
    """返回一个能计数的函数，记住上次的结果。"""
    return start


# 更实用的闭包写法
def make_adder(n):
    """返回一个"加了 n 的函数"。"""
    def adder(x):
        return x + n

    return adder


add_5 = make_adder(5)
print()
print("add_5(10) =", add_5(10))      # 15
add_10 = make_adder(10)
print("add_10(10) =", add_10(10))    # 20  两者互不影响
