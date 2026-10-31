# test_buggy.py —— 测试：会失败

import pytest

from buggy import calculate_average


def test_average_normal():
    """正常情况：应该有正确的平均值。"""
    assert calculate_average([80, 90, 100]) == 90


def test_average_single_value():
    """只有一个数时，平均值就是它自己。"""
    assert calculate_average([50]) == 50


def test_average_empty():
    """空列表返回 0。"""
    assert calculate_average([]) == 0
