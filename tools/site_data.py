"""站点数量常量的单一来源。

为什么要它：22 / 111 / 52 / 23 这些数字以前散落在各构建器和手写页面里，
扩阶段时必然漏改——已经踩过两次（首页进度写死 64、讲义卡片写「12 份」）。

注意：全部做成**惰性函数**。构建器之间存在互相 import（build_lessons →
build_lectures → site_data），如果在模块顶层就去取 build_lessons.LESSONS，
会拿到半初始化的模块并抛 AttributeError。
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_cache = {}


def lessons():
    if "lessons" not in _cache:
        import build_lessons
        _cache["lessons"] = build_lessons.LESSONS
    return _cache["lessons"]


def total_lessons():
    return len(lessons())


def unit_cnt():
    return len({L[0] for L in lessons()})


def unit_lessons(unit):
    return sum(1 for L in lessons() if L[0] == unit)


def unit_lesson_range(unit):
    """该单元的课节号区间 (起, 止)，1 起。用于按课节进度算单元完成度。"""
    if "range" not in _cache:
        rng, n = {}, 0
        for L in lessons():
            n += 1
            u = L[0]
            rng.setdefault(u, [n, n])[1] = n
        _cache["range"] = {k: tuple(v) for k, v in rng.items()}
    return _cache["range"].get(unit, (0, 0))


def question_cnt():
    if "q" not in _cache:
        import bank_map
        _cache["q"] = bank_map.TOTAL
    return _cache["q"]


def slide_cnt():
    if "s" not in _cache:
        import ppt_map
        _cache["s"] = len(ppt_map.SLIDES)
    return _cache["s"]


if __name__ == "__main__":
    print(f"单元 {unit_cnt()} 个 | 课节 {total_lessons()} 节 | 题 {question_cnt()} | "
          f"大纲课件 {slide_cnt()} 页")
