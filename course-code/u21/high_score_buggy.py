# high_score_buggy.py —— INTENTIONALLY-BROKEN 演示用：改错题
import json

HIGH_SCORE_FILE = "data/high_score.json"


def load_high_score():
    with open(HIGH_SCORE_FILE) as f:      # 第一次运行时文件还不存在，会直接崩
        return json.load(f)["score"]
