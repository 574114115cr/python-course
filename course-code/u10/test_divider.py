# test_divider.py —— 测试模块

import pytest

from divider import divide, divide_safe


# ===== 正常用例 =====
def test_divide_normal():
    """普通除法。"""
    assert divide(10, 2) == 5
    assert divide(9, 3) == 3
    assert divide(100, 25) == 4


def test_divide_not_exact():
    """除不尽会产生小数。"""
    assert divide(10, 3) == pytest.approx(3.3333333, rel=1e-6)


# ===== 边界用例 =====
def test_divide_by_one():
    """除以 1。"""
    assert divide(7, 1) == 7


def test_divide_zero_by_number():
    """0 除以非 0 数。"""
    assert divide(0, 5) == 0.0


# ===== 负数用例 =====
def test_divide_negative():
    """负数相除。"""
    assert divide(-10, 2) == -5
    assert divide(10, -2) == -5
    assert divide(-10, -2) == 5


# ===== ★ 异常用例：除零 =====
def test_divide_by_zero_raises():
    """除以 0 应该抛出 ZeroDivisionError。"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)


def test_divide_by_zero_float_raises():
    """除以浮点 0.0 也应该报错。"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0.0)


# ===== 参数化版本 =====
@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5.0),
    (9, 3, 3.0),
    (7, 1, 7.0),
    (-10, 2, -5.0),
    (0, 5, 0.0),
    (100, 10, 10.0),
])
def test_divide_parametrized(a, b, expected):
    """用参数化覆盖多组除法数据。"""
    assert divide(a, b) == expected


# ===== 测试 divide_safe =====
def test_divide_safe_normal():
    assert divide_safe(10, 2) == 5.0


def test_divide_safe_zero():
    """除零返回默认值。"""
    assert divide_safe(10, 0) == 0.0
    assert divide_safe(10, 0, default=-1.0) == -1.0
