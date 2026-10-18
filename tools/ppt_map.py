# -*- coding: utf-8 -*-
"""课件的唯一数据源：页码、标题、与单元/课节的映射。

被三处消费，避免各自维护一份而漂移：
  - tools/build_lectures.py   单元页顶栏与底部课件入口
  - tools/lesson_tpl.py       课节页顶栏 + 侧栏「本单元课件」缩略图
  - tools/build_ppt_html.py   HTML 课件播放器的目录与缩略图
"""

# (页码, 标题, 角色, 覆盖的单元)
SLIDES = [
    (1,  "封面", "hero", ""),
    (2,  "课程坐标", "supporting", ""),
    (3,  "22 个单元全景", "hero", ""),
    (4,  "90 分钟课节结构", "supporting", ""),
    (5,  "零基础教学三原则", "supporting", ""),
    (6,  "单元 1–3 · 先把地基拍实", "supporting", "1,2,3"),
    (7,  "单元 4–6 · 让程序会做判断", "supporting", "4,5,6"),
    (8,  "单元 7 · 函数", "hero", "7"),
    (9,  "单元 8 · 类", "hero", "8"),
    (10, "单元 9–10 · 从「能跑」到「靠谱」", "supporting", "9,10"),
    (11, "单元 11 · 总复习 + 关卡验收", "transition", "11"),
    (12, "关卡 1 · 四项全部达标", "hero", "11"),
    (13, "从「能写」到「能交付」", "transition", ""),
    (14, "项目一 · 外星人入侵", "supporting", "12,13,14"),
    (15, "项目二 · 数据可视化", "supporting", "15,16,17"),
    (16, "项目三 · 学习笔记 Web", "supporting", "18,19,20"),
    (17, "阶段 2 的统一工程流程", "supporting", ""),
    (18, "关卡 2 · 判定「能独立做项目」", "hero", "21"),
    (19, "练习题库 · 六档递进共 84 题", "supporting", ""),
    (20, "常见卡点与对策", "supporting", ""),
    (21, "综合项目 · 三选一", "supporting", "11"),
    (22, "阶段 3 · 从会写代码到会交付软件", "supporting", ""),
    (23, "结束页", "hero", ""),
]

TOTAL_SLIDES = len(SLIDES)
TITLE_BY_NO = {n: t for n, t, _r, _u in SLIDES}

# 单元 → 默认课件页码（课件是单元级概览，多个单元会指向同一页）
UNIT_SLIDE = {
    0: 4,
    1: 6, 2: 6, 3: 6,
    4: 7, 5: 7, 6: 7,
    7: 8, 8: 9,
    9: 10, 10: 10,
    11: 11,
    12: 14, 13: 14, 14: 14,
    15: 15, 16: 15, 17: 15,
    18: 16, 19: 16, 20: 16,
    21: 18,
}

# 具体课节的覆盖：这类课的定位比「本单元概览」更精确，直接指到对应的主题页
LESSON_SLIDE = {
    12: 4,    # 阶段 2 开课准备 → 课节结构
    63: 12,   # ★ 关卡 1 现场测评 → 关卡 1 验收标准
    110: 18,  # ★ 关卡 2 五项逐条自测 → 关卡 2 验收标准
    111: 22,  # 综合项目与阶段 2 收尾 → 阶段 3 预告
}

# 课节标题里的关键词 → 课件页码（优先级低于 LESSON_SLIDE 的精确指定）
TITLE_RULES = [
    ("综合项目", 21),   # 阶段 1 的三个综合项目 → 「综合项目 · 三选一」
    ("关卡 1", 12),
    ("关卡 2", 18),
    # 注意：不要用泛化的「收尾」当规则——单元 6 有节标题叫「交互程序的骨架与收尾」，
    # 会被误判成阶段 3 预告页。阶段 2 收尾那节用上面的 LESSON_SLIDE 精确指定。
]


def slide_for_lesson(no, unit, title=""):
    """给定课节号、单元号、标题，返回最贴切的课件页码。"""
    if no in LESSON_SLIDE:
        return LESSON_SLIDE[no]
    for kw, sn in TITLE_RULES:
        if kw in title:
            return sn
    return UNIT_SLIDE.get(unit)


def slide_for_unit(unit):
    return UNIT_SLIDE.get(unit)


if __name__ == "__main__":
    print(f"课件 {TOTAL_SLIDES} 页；单元映射 {len(UNIT_SLIDE)} 个；"
          f"课节精确映射 {len(LESSON_SLIDE)} 个；标题规则 {len(TITLE_RULES)} 条")


# ── 逐节版讲授课件：课节 -> (单元, 该节的页码) ──────────────────
# 由 tools/build_all_lesson_ppt.py 生成，缺失时回落到单元概览页。
import json as _json
import os as _os

_MAP_PATH = _os.path.join(_os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__))), "web", "ppt", "lesson-slide-map.json")

LESSON_DECK = {}
try:
    with open(_MAP_PATH, encoding="utf-8") as _fh:
        LESSON_DECK = _json.load(_fh)
except Exception:
    LESSON_DECK = {}


def lesson_deck(no):
    """返回 (单元号, 该课节在单元课件里的页码)；无数据返回 (None, None)。"""
    d = LESSON_DECK.get(str(no))
    if not d:
        return None, None
    return d.get("unit"), d.get("slide")


def unit_deck_path(unit):
    """单元课件的网页播放器相对 web/ 的路径。"""
    return f"ppt/u/{unit:02d}.html"


def unit_deck_slide_img(unit, slide):
    """单元课件某页图片，相对 web/ 的路径。"""
    return f"ppt/u/{unit:02d}/slide-{slide:02d}.webp"
