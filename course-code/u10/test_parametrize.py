# test_parametrize.py —— 用 parametrize 减少重复代码

import pytest


def is_prime(n):
    """判断 n 是否为素数。"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


# ===== 不用 parametrize：写 4 个几乎一样的函数 =====
def test_prime_2():
    assert is_prime(2) is True


def test_prime_4():
    assert is_prime(4) is False


def test_prime_17():
    assert is_prime(17) is True


def test_prime_1():
    assert is_prime(1) is False


# ===== 用 parametrize：等价但更紧凑 =====
@pytest.mark.parametrize("n", [2, 3, 5, 7, 11, 13])
def test_is_prime_true(n):
    """这些数都是素数。"""
    assert is_prime(n) is True


@pytest.mark.parametrize("n", [0, 1, 4, 6, 9, 15, 100])
def test_is_prime_false(n):
    """这些数都不是素数。"""
    assert is_prime(n) is False


# ===== 多参数：一次测多组组合 =====
def divide(a, b):
    """返回 a 除以 b。"""
    return a / b


@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5.0),
    (9, 3, 3.0),
    (7, 1, 7.0),
    (-10, 2, -5.0),
    (0, 5, 0.0),
])
def test_divide(a, b, expected):
    """多组数据共用一个测试函数。"""
    assert divide(a, b) == expected


# ===== 参数化 + 异常测试 =====
@pytest.mark.parametrize("b", [0, -0.0])
def test_divide_by_zero(b):
    """除以 0 应该报错。"""
    with pytest.raises(ZeroDivisionError):
        divide(10, b)
