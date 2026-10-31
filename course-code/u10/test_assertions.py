# test_assertions.py —— 各种 assert 写法

import pytest


def test_equal():
    """相等断言。"""
    assert 2 + 2 == 4


def test_not_equal():
    """不等断言。"""
    assert 2 + 2 != 5


def test_with_message():
    """带消息的断言，失败时会显示消息。"""
    scores = [70, 100, 100]
    average = sum(scores) / len(scores)
    assert average == 90, f"平均分应该是 90，实际是 {average}"


def test_comparison_chain():
    """链式比较。"""
    age = 25
    assert 18 <= age < 60


def test_in_container():
    """判断元素是否在容器里。"""
    fruits = ["苹果", "香蕉", "橙子"]
    assert "苹果" in fruits
    assert "西瓜" not in fruits


def test_type_check():
    """类型断言。"""
    value = "42"
    assert isinstance(value, str)
    assert not isinstance(value, int)


def test_truthy():
    """真假值断言。"""
    assert not []        # 空列表是假，所以 not [] 是真
    assert [1, 2]        # 非空列表是真
    assert not ""        # 空字符串同样是假


def test_approx():
    """浮点数比较要用 approx，不能直接用 ==。"""
    result = 0.1 + 0.2
    # assert result == 0.3        # 失败！结果是 0.30000000000000004
    assert result == pytest.approx(0.3)


def test_multiple_asserts():
    """一个测试函数里可以写多个断言，全部通过才算通过。"""
    data = [1, 2, 3]
    assert len(data) == 3
    assert sum(data) == 6
    assert max(data) == 3
    assert min(data) == 1
