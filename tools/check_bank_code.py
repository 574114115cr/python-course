"""题库自检：代码块语法 + 结构完整性 + 映射覆盖。

为什么需要：`verify_py.py` 只检查 `course/*.md`（讲义），题库 84 道题的
Python 代码块一直没人校验——写错了也发现不了，直到学习者复制运行报错。

检查项：
1. 每个 ```python 块能通过 compile()（语法层面）
2. 每题都有「题目」与「答案」；缺「解析」只提示，不算错
3. 题号唯一
4. 每题都能在 bank_map.UNIT_OF 里找到归属单元
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

MD = os.path.join(ROOT, "exercises", "题库-从入门到实践.md")


def parse(md):
    parts = re.split(r"^## (L\d-\d+)[\s　]+(.+)$", md, flags=re.M)
    out = []
    for i in range(1, len(parts), 3):
        qid, title, body = parts[i], parts[i + 1].strip(), parts[i + 2]
        # 只切「档位小标题」（# L2 循环与条件…），不能切任意 `# `——
        # 代码块里的 `# views.py` 这类注释也以 # 开头，会把答案和解析一起切掉。
        cut = re.search(r"^#\s+L\d+\s", body, flags=re.M)
        if cut:
            body = body[:cut.start()]
        out.append((qid, title, body))
    return out


def main():
    md = open(MD, encoding="utf-8").read()
    qs = parse(md)
    problems, warns = [], []
    n_code = 0

    import bank_map
    for qid, title, body in qs:
        for j, m in enumerate(re.finditer(r"```python\n(.*?)```", body, re.S), 1):
            n_code += 1
            try:
                compile(m.group(1), f"{qid}#{j}", "exec")
            except SyntaxError as e:
                problems.append(f"{qid} 第 {j} 个代码块语法错误：第 {e.lineno} 行 {e.msg}")

        if "**题目**" not in body:
            problems.append(f"{qid} 缺「题目」段")
        if "**答案**" not in body:
            problems.append(f"{qid} 缺「答案」段")
        if "**解析**" not in body:
            warns.append(f"{qid} 缺「解析」段")

        if qid not in bank_map.UNIT_OF:
            problems.append(f"{qid} 没有归属单元（bank_map.UNIT_OF）")

    ids = [q[0] for q in qs]
    dup = {x for x in ids if ids.count(x) > 1}
    if dup:
        problems.append(f"题号重复：{sorted(dup)}")

    print(f"题库 {len(qs)} 题 / {n_code} 个 python 代码块")
    if warns:
        print(f"提示 {len(warns)} 条（可接受）：")
        for w in warns[:5]:
            print("  ·", w)
    if problems:
        print(f"发现 {len(problems)} 个问题：")
        for p in problems[:20]:
            print("  ✗", p)
        return 1
    print("✓ 语法与结构全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
