# score_file.py —— 读写成绩文件并统计

FILENAME = "scores.txt"

# ===== 写入成绩 =====
def write_scores(data):
    """把成绩数据写进文件（覆盖模式）。"""
    with open(FILENAME, "w", encoding="utf-8") as f:
        for name, score in data:
            f.write(f"{name},{score}\n")
    print(f"已写入 {len(data)} 条成绩")


# ===== 读取成绩 =====
def read_scores():
    """读回成绩列表，返回 [(姓名, 成绩), ...]。"""
    result = []
    with open(FILENAME, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()# 去掉换行符
            if not line:
                continue                # 跳过空行
            name, score_text = line.split(",")
            # 关键：读回来的是字符串，必须转成数字才能计算
            result.append((name, int(score_text)))
    return result


# ===== 统计 =====
def analyze(data):
    """计算平均分、最高分、及格人数。"""
    if not data:
        return None

    scores = [score for name, score in data]
    average = sum(scores) / len(scores)
    highest_name, highest_score = max(data, key=lambda item: item[1])
    passed = len([s for s in scores if s >= 60])

    return {
        "总人数": len(data),
        "平均分": average,
        "最高分": highest_name,
        "最高分值": highest_score,
        "及格人数": passed,
        "及格率": passed / len(data) * 100,
    }


# ===== 主流程 =====
# 1）显示原始文件内容
with open(FILENAME, "w", encoding="utf-8") as f:
    f.write("姓名,成绩\n")

scores_data = [
    ("小明", 92),
    ("小红", 78),
    ("小刚", 65),
    ("小丽", 88),
    ("小强", 55),
]
write_scores(scores_data)

print("\n--- 文件原始内容 ---")
with open(FILENAME, "r", encoding="utf-8") as f:
    print(f.read(), end="")

# 2）读回来分析
loaded = read_scores()
print(f"读回来的数据：{loaded}")

stats = analyze(loaded)
print("\n--- 统计分析 ---")
for key, value in stats.items():
    if isinstance(value, float):
        print(f"  {key}: {value:.2f}")
    else:
        print(f"  {key}: {value}")

import os
os.remove(FILENAME)
