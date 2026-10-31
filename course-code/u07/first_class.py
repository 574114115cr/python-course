# first_class.py —— 把函数当数据用

def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


# 1）赋给变量
operation = add
print("operation(3, 4) =", operation(3, 4))        # 7

# 2）放进列表，按需要选
operations = [add, subtract]
print("逐个执行：", [op(10, 3) for op in operations])   # [13, 7]

# 3）当参数传给别的函数（sorted 的 key 就是这么用的）
scores = {"小明": 95, "小红": 88, "小刚": 72}
by_score = sorted(scores.items(), key=lambda item: item[1], reverse=True)
print("按分数排序：", by_score)

# 4）当返回值返回（"工厂函数"）
# 注意：sorted 的 key 参数要求函数只接收"一个"参数，
# 而比较函数天然要接收"两个"，所以要用 cmp_to_key 包一层适配。
import functools


def get_comparator(reverse=False):
    """返回一个"两两比较"函数：接收两个值，返回负/零/正。"""
    def compare(a, b):
        if reverse:
            return b - a
        return a - b

    return compare


asc = get_comparator()
desc = get_comparator(reverse=True)
print("升序：", sorted([3, 7, 1], key=functools.cmp_to_key(asc)))
print("降序：", sorted([3, 7, 1], key=functools.cmp_to_key(desc)))

# 5）lambda：一次性小函数，写法极简
square = lambda x: x ** 2
print("square(5) =", square(5))       # 25

# lambda 的本质就是个没有名字的普通函数
print("lambda 和 def 等价：", (lambda x: x ** 2)(5) == square(5))   # True
