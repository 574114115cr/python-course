# test_text_analyzer.py —— 综合项目 3 的测试

import os
import tempfile

import pytest

from text_analyzer import (
    clean_text,
    count_chars,
    count_words,
    count_lines,
    count_sentences,
    word_frequency,
    top_words,
    analyze_text,
    analyze_file,
)


SAMPLE = "Python 是一种编程语言。它简单易学。Python 很好用！"


# ===== clean_text =====
class TestCleanText:
    def test_extra_spaces(self):
        assert clean_text("a    b") == "a b"

    def test_strip(self):
        assert clean_text("  hello  ") == "hello"

    def test_newlines(self):
        assert clean_text("a\n\nb") == "a b"

    def test_empty(self):
        assert clean_text("") == ""


# ===== count_chars =====
class TestCountChars:
    def test_exclude_spaces(self):
        assert count_chars("a b c") == 3

    def test_include_spaces(self):
        assert count_chars("a b c", include_spaces=True) == 5

    def test_empty(self):
        assert count_chars("") == 0


# ===== count_words =====
class TestCountWords:
    def test_english_only(self):
        assert count_words("hello world foo") == 3

    def test_chinese_only(self):
        """★ 中文按连续汉字串算一个词。"""
        assert count_words("你好世界") == 1
        assert count_words("你好 世界") == 2

    def test_mixed(self):
        """中英文混合。"""
        assert count_words("我用 Python 编程") == 3

    def test_empty(self):
        assert count_words("") == 0


# ===== count_lines =====
class TestCountLines:
    def test_three_lines(self):
        assert count_lines("a\nb\nc") == 3

    def test_no_trailing_newline(self):
        assert count_lines("a\nb") == 2

    def test_empty(self):
        """★ 空文本是 0 行。"""
        assert count_lines("") == 0


# ===== count_sentences =====
class TestCountSentences:
    def test_chinese_period(self):
        assert count_sentences("你好。世界！很好？") == 3

    def test_english_period(self):
        assert count_sentences("Hello world. How are you?") == 2

    def test_no_punctuation(self):
        assert count_sentences("没有标点的一句话") == 1

    def test_empty(self):
        assert count_sentences("") == 0


# ===== word_frequency =====
class TestWordFrequency:
    def test_count_duplicates(self):
        counts = word_frequency("python is good python")
        assert counts["python"] == 2

    def test_remove_stop_words(self):
        """★ 默认过滤停用词。"""
        # 注意：中文分词是"连续汉字算一个词"，所以这里用英文停用词演示更直观
        counts = word_frequency("this is a good world")
        assert "is" not in counts
        assert "a" not in counts

    def test_keep_stop_words(self):
        """可以关闭停用词过滤。"""
        counts = word_frequency("this is a good world", remove_stop_words=False)
        assert "is" in counts
        assert "a" in counts

    def test_case_insensitive(self):
        """英文不区分大小写。"""
        counts = word_frequency("Python python PYTHON")
        assert counts["python"] == 3


# ===== top_words =====
class TestTopWords:
    def test_order(self):
        result = top_words("apple apple apple banana banana cherry")
        assert result[0] == ("apple", 3)
        assert result[1] == ("banana", 2)

    def test_limit(self):
        """限制返回数量。"""
        result = top_words("apple banana cherry date elder fig", n=3)
        assert len(result) == 3

    def test_empty(self):
        assert top_words("") == []


# ===== analyze_text =====
class TestAnalyzeText:
    def test_full_analysis(self):
        result = analyze_text(SAMPLE)
        assert result["句子数"] == 3
        assert "python" in result["高频词"]

    def test_empty_text(self):
        """★ 空文本不能让任何地方崩。"""
        result = analyze_text("")
        assert result["字符数"] == 0
        assert result["单词数"] == 0
        assert result["平均句长"] == 0.0

    def test_no_punctuation(self):
        """没有标点时平均句长不能除以 0。"""
        result = analyze_text("hello")
        assert result["平均句长"] > 0


# ===== analyze_file =====
class TestAnalyzeFile:
    def test_normal_file(self, tmp_path):
        """正常文件。"""
        test_file = tmp_path / "a.txt"
        test_file.write_text(SAMPLE, encoding="utf-8")
        result = analyze_file(str(test_file))
        assert "错误" not in result
        assert result["文件名"] == "a.txt"

    def test_missing_file(self):
        """★ 文件不存在：返回错误信息，不抛异常。"""
        result = analyze_file("绝对不存在的文件.txt")
        assert "错误" in result

    def test_empty_file(self, tmp_path):
        """★ 空文件。"""
        empty = tmp_path / "empty.txt"
        empty.write_text("", encoding="utf-8")
        result = analyze_file(str(empty))
        assert "错误" in result

    def test_directory(self, tmp_path):
        """★ 传入目录：应该有友好提示。"""
        result = analyze_file(str(tmp_path))
        assert "错误" in result
