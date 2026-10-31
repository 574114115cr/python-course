# test_text_utils.py —— 测试模块

import pytest

from text_utils import count_words, reverse, is_palindrome


# ===== count_words =====
def test_count_words_normal():
    """正常情况：普通句子。"""
    assert count_words("hello world") == 2
    assert count_words("a b c d e") == 5


def test_count_words_single():
    """只有一个单词。"""
    assert count_words("hello") == 1


def test_count_words_empty():
    """空字符串返回 0。"""
    assert count_words("") == 0


def test_count_words_all_spaces():
    """全是空格也返回 0。"""
    assert count_words("   ") == 0
    assert count_words("      ") == 0


# ===== reverse =====
def test_reverse_normal():
    assert reverse("hello") == "olleh"


def test_reverse_empty():
    assert reverse("") == ""


def test_reverse_single_char():
    assert reverse("a") == "a"


def test_reverse_palindrome():
    """反转回文串后不变。"""
    assert reverse("abcba") == "abcba"


def test_reverse_unicode():
    """中文也要能反转。"""
    assert reverse("你好世界") == "界世好你"


# ===== is_palindrome =====
def test_is_palindrome_normal():
    assert is_palindrome("racecar") is True
    assert is_palindrome("level") is True


def test_is_palindrome_case_insensitive():
    """忽略大小写。"""
    assert is_palindrome("RaceCar") is True
    assert is_palindrome("MadamImAdam") is True
    # 反面例子：AbleWasI 看起来像回文，但倒过来是 IsawelbA，其实不是
    assert is_palindrome("AbleWasI") is False


def test_is_palindrome_with_spaces():
    """忽略空格和标点。"""
    assert is_palindrome("A man, a plan, a canal: Panama") is True


def test_is_palindrome_chinese():
    """中文回文。"""
    assert is_palindrome("上海自来水来自海上") is True


def test_is_palindrome_not():
    assert is_palindrome("hello") is False
    assert is_palindrome("python") is False


def test_is_palindrome_empty():
    """空串算回文。"""
    assert is_palindrome("") is True


# ===== 参数化版本（进阶写法）=====
@pytest.mark.parametrize("text,expected", [
    ("hello world", 2),
    ("hello", 1),
    ("", 0),
    ("   ", 0),
    ("a b c d e", 5),
    ("one two three four five six", 6),
])
def test_count_words_parametrized(text, expected):
    """用参数化覆盖更多输入组合。"""
    assert count_words(text) == expected
