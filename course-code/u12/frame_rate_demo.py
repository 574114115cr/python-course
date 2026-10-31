# frame_rate_demo.py —— 用纯 Python 演示帧率控制
# 运行：python frame_rate_demo.py（不需要 pygame）
import time


def run_loop(fps_limit, seconds):
    """模拟主循环：每圈干一点活，可选限制帧率。"""
    frames = 0
    start = time.perf_counter()
    while True:
        frames += 1
        # 每圈"干的活"：模拟真实游戏一帧的计算量
        _ = sum(range(50000))
        if time.perf_counter() - start >= seconds:
            break
        if fps_limit:
            time.sleep(1 / fps_limit)
    return frames


SECONDS = 2
unlimited = run_loop(None, SECONDS)
limited = run_loop(60, SECONDS)

print(f"不限制帧率：{SECONDS} 秒跑了 {unlimited} 帧")
print(f"限制 60 FPS：{SECONDS} 秒跑了 {limited} 帧")
print(f"差距约 {unlimited / limited:.0f} 倍 —— 这就是别人电脑上游戏'加速'的原因")
