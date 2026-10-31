# high_score_json.py —— 最高分写进文件，跨局还在；顺便看懂升级进位
import json
from pathlib import Path

HIGH_SCORE_FILE = Path("data/high_score.json")
RULES = {"alien_points": 50, "score_scale": 1.5, "aliens_per_level": 3}


def load_high_score(path=HIGH_SCORE_FILE):
    """第一次运行时文件还不存在——必须兜底成 0，不能让游戏开不了。"""
    try:
        return int(json.loads(path.read_text(encoding="utf-8"))["score"])
    except (OSError, ValueError, KeyError, TypeError):
        return 0


def save_high_score(score, path=HIGH_SCORE_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"score": score}, ensure_ascii=False),
                    encoding="utf-8")


def add_score(stats, rules, aliens_hit=1):
    """击落 aliens_hit 只外星人：加分、记数、够 3 只就升级并提分。"""
    stats["score"] += rules["alien_points"] * aliens_hit
    stats["killed"] += aliens_hit
    while stats["killed"] >= rules["aliens_per_level"]:
        stats["killed"] -= rules["aliens_per_level"]
        stats["level"] += 1
        rules["alien_points"] = int(rules["alien_points"] * rules["score_scale"])
    return stats


def new_round(high_score):
    """一局的初始状态；high_score 从外面传进来，不能在内层被清零。"""
    return {"score": 0, "level": 1, "killed": 0, "high_score": high_score}


rules = dict(RULES)
stats = new_round(load_high_score())
print("开局：", stats, "（文件不存在时 high_score 兜底成 0）")

print("\n=== 连打 4 波，每波 2 只，看分数怎么跳级 ===")
for wave in range(1, 5):
    add_score(stats, rules, aliens_hit=2)
    print(f"第 {wave} 波后：score={stats['score']:>5}  level={stats['level']}"
          f"  本波已收 {stats['killed']} 只  下一只值 {rules['alien_points']} 分")

if stats["score"] > stats["high_score"]:
    stats["high_score"] = stats["score"]
    save_high_score(stats["high_score"])
    print(f"\n新纪录 {stats['high_score']} 已写入 {HIGH_SCORE_FILE}")

print("\n=== 关掉程序再启动（重建一局，只从文件拿纪录）===")
rules = dict(RULES)                       # 难度回到初始值
second = new_round(load_high_score())
print("第二局开局：", second)
print(f"文件内容：{HIGH_SCORE_FILE.read_text(encoding='utf-8').strip()}")
HIGH_SCORE_FILE.unlink()                  # 演示完删掉，真项目里要留着
