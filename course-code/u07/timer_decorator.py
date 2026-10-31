# timer_decorator.py —— 用"函数返回函数"实现计时器

import time


def make_timer(func):
    """把一个函数包成"会自动打印耗时"的版本。"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)      # 真正干活
        end = time.time()
        print(f"  [{func.__name__}] 耗时 {end - start:.6f} 秒")
        return result                      # 别忘了把结果传出去
    return wrapper


# 被包装的函数：故意做点耗时的活
def slow_sum(n):
    """累加 1 到 n 的和，n 大一点才有感。"""
    total = 0
    for i in range(1, n + 1):
        total += i
    return total


def quick_answer():
    """一个几乎不耗时的函数。"""
    return 42


# ===== 使用 =====
timed_slow_sum = make_timer(slow_sum)
timed_answer = make_timer(quick_answer)

print("调用被包装的慢函数：")
result1 = timed_slow_sum(1000000)
print("  返回值：", result1)

print("\n调用被包装的快函数：")
result2 = timed_answer()
print("  返回值：", result2)

# ===== 观察问题 =====
print("\n--- 问题：被包装后函数名变了 ---")
print("timed_slow_sum 的 __name__ 是：", timed_slow_sum.__name__)
print("原函数 slow_sum 的 __name__ 是：", slow_sum.__name__)
# 打印栈信息或报错时，会显示 wrapper 这个没有意义的名字

# ===== 修复：手动把名字复制过去 =====
timed_slow_sum.__name__ = slow_sum.__name__
print("\n修复后 timed_slow_sum 的 __name__ 是：", timed_slow_sum.__name__)

# Python 内置的functools.wraps 就是自动做这件事的工具：
import functools


def make_timer_pro(func):
    """用 functools.wraps 保留原函数的名字和文档。"""
    @functools.wraps(func)         # 这一行等价于上面的手动赋值 + 复制文档
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"  [{func.__name__}] 耗时 {end - start:.6f} 秒")
        return result
    return wrapper


print("\n用 wraps 版本再试一次：")
timed_slow_sum2 = make_timer_pro(slow_sum)
timed_slow_sum2(100000)
print("  名字是：", timed_slow_sum2.__name__)
print("  文档是：", timed_slow_sum2.__doc__)

# 思考题答案：
# 保留原函数名很重要，因为报错信息、帮助文档、日志都会用到它。
# 如果用户看到一个叫 wrapper 的函数名在报错里，他会完全不知道
# 自己调用的是哪个函数。这正是 @装饰器 语法糖要解决的问题。
