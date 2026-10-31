# （片段）geometry.py —— 加自测块
def area(w, h):
    return w * h


def perimeter(w, h):
    return 2 * (w + h)


def is_square(w, h):
    return w == h


if __name__ == "__main__":
    # 直接运行 python geometry.py 时才会执行这三行
    assert area(3, 4) == 12
    assert perimeter(3, 4) == 14
    assert is_square(4, 4) is True
    print("geometry.py 自测通过")
