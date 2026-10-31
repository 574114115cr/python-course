# test_vote_analyzer.py —— 测试模块

import pytest

from vote_analyzer import analyze_votes


# ===== 1. 正常情况 =====
def test_clear_winner():
    """某人明显胜出。"""
    result = analyze_votes(["A", "A", "A", "B", "C"])
    assert result["winner"] == "A"
    assert result["total"] == 5
    assert result["counts"]["A"] == 3
    assert result["tied"] is False


def test_counts_are_correct():
    """各候选人票数统计正确。"""
    result = analyze_votes(["A", "B", "A", "C", "B"])
    assert result["counts"] == {"A": 2, "B": 2, "C": 1}


# ===== 2. 平票 =====
def test_tie_returns_none_winner():
    """★ 平票时 winner 应该是 None。"""
    result = analyze_votes(["A", "B", "A", "B"])
    assert result["winner"] is None
    assert result["tied"] is True
    assert result["total"] == 4


def test_three_way_tie():
    """三人平票。"""
    result = analyze_votes(["A", "B", "C"])
    assert result["winner"] is None
    assert result["tied"] is True


# ===== 3. 空列表 =====
def test_empty_votes():
    """★ 空列表：total 为 0，winner 为 None。"""
    result = analyze_votes([])
    assert result["total"] == 0
    assert result["winner"] is None
    assert result["counts"] == {}


# ===== 4. 只有一票 =====
def test_single_vote():
    """只有一票也算有效结果。"""
    result = analyze_votes(["A"])
    assert result["winner"] == "A"
    assert result["total"] == 1


# ===== 5. 所有人票数相同 =====
def test_all_equal():
    """所有人票数相同时是平票。"""
    result = analyze_votes(["A", "B", "C", "D"])
    assert result["winner"] is None
    assert result["tied"] is True
    assert set(result["counts"].values()) == {1}


# ===== 6. 大量数据 =====
def test_large_number_of_votes():
    """★ 1000 票也不能出错或崩溃。"""
    votes = ["A"] * 600 + ["B"] * 300 + ["C"] * 100
    result = analyze_votes(votes)
    assert result["total"] == 1000
    assert result["winner"] == "A"
    assert result["counts"]["A"] == 600
    assert result["counts"]["B"] == 300
    assert result["counts"]["C"] == 100


def test_large_tie():
    """大量数据下的平票。"""
    votes = ["A"] * 500 + ["B"] * 500
    result = analyze_votes(votes)
    assert result["winner"] is None
    assert result["tied"] is True
    assert result["total"] == 1000


# ===== 7. 参数化：不同的票数分布 =====
@pytest.mark.parametrize(
    "votes,expected_winner,expected_total",
    [
        # (票列表, 期望的 winner, 期望总票数)
        (["A", "A", "B"], "A", 3),                 # A 以 2:1 胜出
        (["A", "B"], None, 2),                     # 平票
        (["A"], "A", 1),                           # 一票
        ([], None, 0),                             # 空
        (["A", "B", "C", "D", "E"], None, 5),       # 五人平票
        (["B", "B", "B", "A", "A"], "B", 5),       # B 反超
        (["X"] * 10 + ["Y"] * 3, "X", 13),         # X 大幅领先
        (["X"] * 3 + ["Y"] * 10, "Y", 13),         # Y 反超
    ],
    ids=[
        "2比1",
        "平票",
        "单票",
        "空列表",
        "五人平票",
        "B反超",
        "X领先",
        "Y反超",
    ],
)
def test_parametrized(votes, expected_winner, expected_total):
    """用参数化一次覆盖 8 种不同的分布。"""
    result = analyze_votes(votes)
    assert result["winner"] == expected_winner
    assert result["total"] == expected_total


# ===== 8. 边界组合 =====
def test_zero_votes_multi_candidate():
    """候选人在 counts 里但没人投他。"""
    result = analyze_votes(["A", "A"])
    assert result["counts"] == {"A": 2}
    assert result["winner"] == "A"


def test_result_structure():
    """返回的字典必须包含约定的四个键。"""
    result = analyze_votes(["A"])
    assert set(result.keys()) == {"winner", "total", "counts", "tied"}


def test_counts_does_not_modify_input():
    """分析过程不能修改传入的列表。"""
    votes = ["A", "B", "A"]
    original = votes[:]
    analyze_votes(votes)
    assert votes == original       # 原列表没有被改动
