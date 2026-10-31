# test_score_analyzer.py —— 综合项目 2 的测试

import json
import os
import tempfile

import pytest

from score_analyzer import (
    subject_stats,
    add_total,
    ranking,
    subject_toppers,
    failed_students,
    class_overview,
)


# 共享的测试数据
@pytest.fixture
def sample_scores():
    """pytest 夹具：每个测试自动获得一份干净的数据。"""
    return [
        {"name": "小明", "math": 92, "english": 88},
        {"name": "小红", "math": 78, "english": 95},
        {"name": "小刚", "math": 65, "english": 72},
        {"name": "小强", "math": 55, "english": 48},
    ]


# ===== subject_stats =====
class TestSubjectStats:
    def test_normal(self, sample_scores):
        """正常情况：数学平均分。"""
        stats = subject_stats(sample_scores, "math")
        assert stats["平均分"] == pytest.approx((92 + 78 + 65 + 55) / 4)
        assert stats["最高分"] == 92
        assert stats["最低分"] == 55
        assert stats["人数"] == 4

    def test_empty(self):
        """★ 空数据：不能崩，返回全 0。"""
        stats = subject_stats([], "math")
        assert stats["平均分"] == 0.0
        assert stats["人数"] == 0

    def test_single_student(self):
        """只有一个人：平均分等于自己的分数。"""
        stats = subject_stats([{"name": "A", "math": 88, "english": 90}], "math")
        assert stats["平均分"] == 88
        assert stats["最高分"] == 88
        assert stats["最低分"] == 88


# ===== add_total =====
def test_add_total_does_not_modify_input(sample_scores):
    """★ 纯函数：不能修改传入的数据。"""
    add_total(sample_scores)
    assert "total" not in sample_scores[0]

def test_add_total_values(sample_scores):
    with_total = add_total(sample_scores)
    assert with_total[0]["total"] == pytest.approx(180)


# ===== ranking =====
class TestRanking:
    def test_sorted_descending(self, sample_scores):
        """排名按总分降序。"""
        result = ranking(sample_scores)
        totals = [s["total"] for s in result]
        assert totals == sorted(totals, reverse=True)

    def test_first_place(self, sample_scores):
        """第一名应该是总分最高的。"""
        result = ranking(sample_scores)
        assert result[0]["name"] == "小明"

    def test_empty(self):
        assert ranking([]) == []


# ===== subject_toppers =====
class TestToppers:
    def test_single_topper(self, sample_scores):
        assert subject_toppers(sample_scores, "math") == ["小明"]

    def test_tie_returns_all(self):
        """★ 并列时返回全部第一名。"""
        scores = [
            {"name": "A", "math": 90, "english": 80},
            {"name": "B", "math": 90, "english": 70},
        ]
        assert set(subject_toppers(scores, "math")) == {"A", "B"}

    def test_empty(self):
        assert subject_toppers([], "math") == []


# ===== failed_students =====
class TestFailedStudents:
    def test_one_subject_failed(self, sample_scores):
        """小强两科都不及格。"""
        failed = failed_students(sample_scores)
        names = [f["name"] for f in failed]
        assert "小强" in names
        assert "小明" not in names

    def test_all_pass_returns_empty(self):
        assert failed_students([
            {"name": "A", "math": 90, "english": 80},
        ]) == []

    def test_exactly_60_is_pass(self):
        """★ 正好 60 分算及格（边界）。"""
        assert failed_students([{"name": "A", "math": 60, "english": 60}]) == []


# ===== class_overview =====
class TestOverview:
    def test_normal(self, sample_scores):
        overview = class_overview(sample_scores)
        assert overview["人数"] == 4
        assert overview["最高总分"] == 180
        assert overview["最低总分"] == 103

    def test_empty(self):
        overview = class_overview([])
        assert overview["人数"] == 0
        assert overview["班级平均总分"] == 0.0


# ===== 文件读写 =====
def test_load_scores_missing_file_returns_empty():
    """★ 文件不存在时返回空列表而不是崩溃。"""
    from score_analyzer import load_scores
    assert load_scores("绝对不存在的文件.json") == []


def test_load_scores_invalid_json(tmp_path):
    """内容不是合法 JSON 时返回空列表。"""
    from score_analyzer import load_scores
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{这不是合法JSON", encoding="utf-8")
    assert load_scores(str(bad_file)) == []


def test_load_scores_skips_bad_records(tmp_path):
    """★ 混入坏数据时，只跳过坏的，保留好的。"""
    from score_analyzer import load_scores
    good_file = tmp_path / "mixed.json"
    good_file.write_text(
        json.dumps([
            {"name": "好数据", "math": 90, "english": 80},
            {"name": "缺字段", "math": 70},          # 缺 english
            {"name": "类型错", "math": "abc", "english": 80},
        ]),
        encoding="utf-8",
    )
    result = load_scores(str(good_file))
    assert len(result) == 1
    assert result[0]["name"] == "好数据"
