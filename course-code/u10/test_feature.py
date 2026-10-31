# test_feature.py —— 第 1 步：先写测试（此时 tip.py 还不存在）

import pytest

from tip import calculate_tip


# ===== 正常用例 =====
def test_tip_ten_percent():
    """10% 小费。"""
    assert calculate_tip(100, 0.10) == 10.0


def test_tip_twenty_percent():
    """20% 小费。"""
    assert calculate_tip(100, 0.20) == 20.0


# ===== 参数化 =====
@pytest.mark.parametrize("bill,rate,expected", [
    (100, 0.10, 10.0),
    (50, 0.15, 7.5),
    (200, 0.20, 40.0),
    (0, 0.10, 0.0),      # ★ 边界：账单为 0
])
def test_tip(bill, rate, expected):
    """参数化测试。"""
    assert calculate_tip(bill, rate) == expected


# ===== 边界用例（这一步会在实现完成后才通过）=====
def test_tip_zero_bill():
    """★ 账单为 0 时小费必须是 0，不能是 None 或报错。"""
    assert calculate_tip(0, 0.15) == 0


def test_tip_invalid_rate_raises():
    """非法折扣率应该报错。"""
    with pytest.raises(ValueError):
        calculate_tip(100, 1.5)
