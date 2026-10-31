# self_check.py —— 用代码把前 11 章串起来

def check_basics():
    """检查基础语法：变量、类型、格式化。"""
    name = "小明"
    age = 18
    height = 1.75
    is_student = True

    # 类型转换
    age_str = str(age)
    age_int = int(age_str)

    # f-string格式化
    message = f"{name} 今年 {age} 岁，身高 {height:.2f} 米"
    return message, age_int, is_student


def check_collections():
    """检查列表和字典操作。"""
    # 列表
    fruits = ["苹果", "香蕉"]
    fruits.append("橙子")
    fruits.insert(1, "葡萄")
    fruits.remove("香蕉")
    first = fruits[0]
    last = fruits[-1]
    sliced = fruits[1:3]
    reversed_list = fruits[::-1]

    # 列表推导式
    numbers = [1, 2, 3, 4, 5]
    evens = [n for n in numbers if n % 2 == 0]
    squares = [n ** 2 for n in numbers]

    # 字典
    scores = {"语文": 90}
    scores["数学"] = 85
    got = scores.get("英语", 0)
    keys = list(scores.keys())
    items = list(scores.items())

    # 元组
    point = (3, 5)
    x, y = point

    return {
        "列表": fruits, "首元素": first, "末元素": last,
        "切片": sliced, "反转": reversed_list,
        "偶数": evens, "平方": squares,
        "字典": scores, "默认值": got,
        "键": keys, "键值对": items, "元组": point, "x": x,
    }


def check_control_flow():
    """检查条件与循环。"""
    # if / elif / else
    def grade(score):
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "F"

    # for + range
    total = 0
    for i in range(1, 6):
        total += i

    # while + break
    count = 0
    while True:
        count += 1
        if count >= 3:
            break

    # continue
    skipped = []
    for i in range(6):
        if i % 2 == 0:
            continue
        skipped.append(i)

    return {
        "等级": [grade(s) for s in [95, 85, 65, 45]],
        "1到5之和": total,
        "循环次数": count,
        "奇数": skipped,
    }


def check_functions():
    """检查函数与参数。"""
    def calc(*args, **kwargs):
        """可变参数。"""
        return sum(args), kwargs

    def with_default(a, b=10, *rest, **extra):
        """默认参数 + 可变参数。"""
        return a, b, rest, extra

    def pure_function(data):
        """不修改传入列表的纯函数。"""
        return data + [999]

    original = [1, 2, 3]
    result = pure_function(original)

    return {
        "可变参数": calc(1, 2, 3, x=1, y=2),
        "默认参数": with_default(1),
        "纯函数原数据": original,   # [1, 2, 3] 没被改
        "纯函数结果": result,       # [1, 2, 3, 999]
    }


# 展示
if __name__ == "__main__":
    for title, func in [
        ("基础语法", check_basics),
        ("集合类型", check_collections),
        ("流程控制", check_control_flow),
        ("函数", check_functions),
    ]:
        print("=" * 50)
        print(f"【{title}】")
        print("=" * 50)
        result = func()
        if isinstance(result, tuple):
            for i, item in enumerate(result, 1):
                print(f"  {i}. {item}")
        elif isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {value}")
        print()
