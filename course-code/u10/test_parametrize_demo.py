# test_parametrize_demo.py —— 参数化测试完整示例

import pytest

from divider import divide
from text_utils import count_words, is_palindrome


# ===== divide的参数化测试：6 组数据 =====
@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5.0),        # 正常
    (9, 3, 3.0),         # 正常，能整除
    (7, 1, 7.0),         # 边界：除以 1
    (1, 10, 0.1),        # 边界：除以比分子大
    (-10, 2, -5.0),      # 负数
    (-10, -2, 5.0),      # 负负得正
])
def test_divide(a, b, expected):
    """多组数据共用一个测试函数。"""
    assert divide(a, b) == expected


# ===== 除零的参数化测试 =====
@pytest.mark.parametrize("zero", [0, 0.0, -0.0])
def test_divide_by_zero_raises(zero):
    """各种形式的零都会导致除零错误。"""
    with pytest.raises(ZeroDivisionError):
        divide(10, zero)


# ===== count_words 的参数化测试 =====
@pytest.mark.parametrize("text,expected", [
    ("hello world", 2),          # 普通句子
    ("hello", 1),               # 单个单词
    ("", 0),                    # 空字符串
    ("   ", 0),                 # 全是空格
    ("a b c d e", 5),           # 五个单词
    ("one two three four", 4),  # 稍长的句子
])
def test_count_words(text, expected):
    """参数化覆盖各种输入。"""
    assert count_words(text) == expected


# ===== 带 id 的参数化：失败时好定位 =====
@pytest.mark.parametrize(
    "text,expected",
    [
        ("racecar", True),
        ("hello", False),
        ("Level", True),         # 忽略大小写
    ],
    ids=["纯回文", "非回文", "混合大小写"],
)
def test_is_palindrome_with_ids(text, expected):
    """ids 让失败报告更易读。"""
    assert is_palindrome(text) is expected


# ===== 多组数据的组合测试 =====
@pytest.mark.parametrize("a,b,c,expected_sum", [
    (1, 2, 3, 6),
    (10, 20, 30, 60),
    (-1, 1, 0, 0),
])
def test_add_three(a, b, c, expected_sum):
    """测试三数求和。"""
    assert a + b + c == expected_sum
