# high_score_persist.py —— 用 JSON 把最高分写进文件（教材未涉及，补充实现）
import json
import os

HIGH_SCORE_FILE = "high_score.json"


def load_high_score():
    """从文件读取最高分，文件不存在或损坏都返回 0。"""
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data.get("high_score", 0))
    except FileNotFoundError:
        print(f"  {HIGH_SCORE_FILE} 不存在，最高分从 0 开始")
        return 0
    except (json.JSONDecodeError, ValueError):
        print(f"  {HIGH_SCORE_FILE} 内容损坏，最高分从 0 开始")
        return 0


def save_high_score(score):
    """把最高分写进文件。"""
    with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump({"high_score": score}, f, ensure_ascii=False, indent=2)
    print(f"  最高分 {score} 已保存到 {HIGH_SCORE_FILE}")


# ===== 模拟一次完整的游戏生命周期 =====
print("=== 1. 程序启动：读取最高分 ===")
high_score = load_high_score()
print(f"  当前最高分：{high_score}")

print("\n=== 2. 玩了一局，得到 500 分 ===")
score = 500
if score > high_score:
    high_score = score
    save_high_score(high_score)

print("\n=== 3. 模拟重启程序：再次读取 ===")
high_score_2 = load_high_score()
print(f"  重启后最高分：{high_score_2}")
assert high_score_2 == 500, "最高分应该跨进程保留！"
print("  断言通过：关机重开，纪录还在")

print("\n=== 4. 新的一局分数更低，不更新纪录 ===")
if score > high_score_2:
    high_score_2 = score
    save_high_score(high_score_2)
else:
    print(f"  300 < {high_score_2}，纪录保持 {high_score_2}")

# 清理（想体验"重启保留"，把下面两行注释掉再跑两次）
if os.path.exists(HIGH_SCORE_FILE):
    os.remove(HIGH_SCORE_FILE)
    print(f"\n已清理 {HIGH_SCORE_FILE}")
