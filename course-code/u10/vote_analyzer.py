# vote_analyzer.py —— 被测模块

def analyze_votes(votes):
    """分析投票结果。

    参数:
        votes: 候选人名字组成的列表

    返回:
        {
            "winner": 票数最多的候选人名字；平票或无票时为 None,
            "total": 总票数,
            "counts": {候选人: 票数},
            "tied": 是否平票,
        }
    """
    # 统计票数
    counts = {}
    for name in votes:
        counts[name] = counts.get(name, 0) + 1

    total = len(votes)

    # 空列表的边界情况
    if not counts:
        return {
            "winner": None,
            "total": 0,
            "counts": {},
            "tied": False,
        }

    # 找出最高票数
    highest_count = max(counts.values())

    # 找出所有达到最高票数的候选人
    leaders = [name for name, count in counts.items() if count == highest_count]

    # 只有一个人领先才有winner，否则是平票
    winner = leaders[0] if len(leaders) == 1 else None

    return {
        "winner": winner,
        "total": total,
        "counts": counts,
        "tied": len(leaders) > 1,
    }
