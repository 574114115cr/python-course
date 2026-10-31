# average.py —— 可变参数求平均值

def average(*numbers):
    """返回所有传入数字的平均值，没有参数时返回 0。

    用法:average(1, 2, 3) -> 2.0
    """
    if not numbers:              # 空元组是"假值"
        return 0
    return sum(numbers) / len(numbers)


# 测试
print(average(10, 20, 30))       # 20.0
print(average(1, 2, 3, 4, 5))     # 3.0
print(average(100))               # 100.0
print(average())                  # 0   空输入不崩

# numbers 实际上是一个元组，可以用列表方法以外的方式处理
def average_verbose(*numbers):
    """同样的功能，但展示 numbers 的真实类型。"""
    print(f"  numbers 的类型是 {type(numbers).__name__}，内容是 {numbers}")
    if len(numbers) == 0:
        return 0
    return sum(numbers) / len(numbers)


print()
average_verbose(10, 20, 30)
print("平均值：", average_verbose(80, 90, 100))

# 进阶：把一个已有列表展开成可变参数
data = [70, 80, 90, 100]
print()
print("列表展开调用：", average(*data))     # *data 把列表拆成一个个参数
