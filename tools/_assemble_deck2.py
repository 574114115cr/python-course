# -*- coding: utf-8 -*-
"""组装「Python 阶段 0–2 课程大纲」的 23 页 DSL。

复用旧 deck 里仍然正确的页面（阶段 1 内容），只改页脚；新增阶段 2 页面。
产出：slides/deck2/NN.slide（NN = 新页码）
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PPT = os.path.join(ROOT, "python-course-ppt")
OLD = os.path.join(PPT, "slides")
NEW = os.path.join(PPT, "slides", "new")
OUT = os.path.join(PPT, "slides", "deck2")

TOTAL = 23

# 新页号 -> 来源：("new", 文件名) 用新建的；("old", 旧页号) 复用旧页
PLAN = [
    (1, "new", "01"), (2, "new", "02"), (3, "new", "03"),
    (4, "old", 4), (5, "old", 5), (6, "old", 6), (7, "old", 7),
    (8, "old", 8), (9, "old", 9), (10, "old", 10), (11, "old", 11),
    (12, "old", 12),
    (13, "new", "13"), (14, "new", "14"), (15, "new", "15"),
    (16, "new", "16"), (17, "new", "17"), (18, "new", "18"),
    (19, "old", 13), (20, "old", 14), (21, "old", 15), (22, "old", 16),
    (23, "new", "23"),
]

os.makedirs(OUT, exist_ok=True)
# 清掉上一次的产物，避免残留
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))

for new_no, kind, src in PLAN:
    if kind == "new":
        s = open(os.path.join(NEW, f"{src}.slide"), encoding="utf-8").read()
    else:
        s = open(os.path.join(OLD, f"{src:02d}.slide"), encoding="utf-8").read()

    # 统一页脚：品牌名 + 页码
    s = s.replace("Python 阶段 0–1 课程大纲", "Python 阶段 0–2 课程大纲")
    s = re.sub(r"\b\d{1,2} / 17\b", f"{new_no:02d} / {TOTAL}", s)
    # 复用页里若没有页码（05/11/17 页脚只有数字），补上规范页码
    if not re.search(r"\d{2} / %d" % TOTAL, s) and new_no not in (1, 23):
        # 找底部那行 Text 里的「NN / 17」已被替换；若原本就缺，跳过（保持原设计）
        pass

    open(os.path.join(OUT, f"{new_no:02d}.slide"), "w", encoding="utf-8").write(s)

# 校验：每页围栏/标签基本平衡、都含 Slide 根标签
bad = []
for f in sorted(os.listdir(OUT)):
    t = open(os.path.join(OUT, f), encoding="utf-8").read()
    if "<Slide" not in t or t.count("<Slide") != t.count("</Slide>"):
        bad.append((f, "Slide 标签不配对"))
    if t.count("<Box") != t.count("</Box>"):
        bad.append((f, f"Box 不配对 {t.count('<Box')}/{t.count('</Box>')}"))
    if t.count("<Text") != t.count("</Text>"):
        bad.append((f, f"Text 不配对 {t.count('<Text')}/{t.count('</Text>')}"))

print(f"生成 {len(os.listdir(OUT))} 页 -> {OUT}")
print("页码：", " ".join(sorted(os.listdir(OUT))))
if bad:
    print("!! 结构问题：")
    for f, m in bad:
        print("   ", f, m)
else:
    print("结构检查：标签全部配对 OK")
