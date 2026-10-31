# speedup.py —— 击落加速（封顶 6.0）+ 结束简报
bullet_speed = 2.0
killed, frames, ships_left = 0, 0, 3

for f in range(1, 11):          # 模拟 10 帧，每 3 帧击落一个
    frames = f
    if f % 3 == 0:
        killed += 1
        bullet_speed = min(6.0, round(bullet_speed + 0.5, 1))
    print(f"帧 {f:>2}：击落 {killed} 速度 {bullet_speed}")

print(f"本局击落 {killed} 个外星人、坚持了 {frames} 帧、剩余 {ships_left} 条命")
