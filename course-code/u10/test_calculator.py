# test_calculator.py —— 测试代码（只放测试）

from calculator import add, subtract, multiply, divide

import pytest


# ===== 正常用例 =====
def test_add():
    """测试加法。"""
    assert add(2, 3) == 5
    assert add(0, 0) == 0
    assert add(-1, 1) == 0


def test_subtract():
    """测试减法。"""
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2
    assert subtract(10, 10) == 0


def test_multiply():
    """测试乘法。"""
    assert multiply(3, 4) == 12
    assert multiply(0, 100) == 0
    assert multiply(-2, 3) == -6


def test_divide():
    """测试除法。"""
    assert divide(10, 2) == 5
    assert divide(9, 3) == 3
    assert divide(-10, 2) == -5


# ===== 边界用例 =====
def test_divide_by_one():
    """除以 1 的边界情况。"""
    assert divide(7, 1) == 7


def test_divide_result_is_float():
    """除法结果应该是浮点数。"""
    result = divide(10, 2)
    assert result == 5.0
    assert isinstance(result, float)


# ===== 异常用例：除零 =====
def test_divide_by_zero_raises():
    """除以0 应该抛出 ZeroDivisionError。"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
