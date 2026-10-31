# module_demo.py —— 直接运行时才跑自测
def area(w, h):
    """矩形面积。"""
    return w * h


def average(nums):
    """平均值；空列表返回 None，而不是 ZeroDivisionError。"""
    return sum(nums) / len(nums) if nums else None


print("__name__ =", __name__)          # 直接运行 → __main__

if __name__ == "__main__":
    print("面积  ", area(3, 4))
    print("平均  ", average([80, 90, 100]))
    print("空列表", average([]))
