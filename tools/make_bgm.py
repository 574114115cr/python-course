"""合成 8-bit 风格、可无缝循环的背景音乐（纯标准库，无第三方依赖）。

输出：web/media/bgm-8bit.wav
- 22050 Hz / 16-bit / 单声道，8 小节 = 16.000 秒（样本数精确等于 16×22050）
- 方波（不同占空比）+ 三角波 + 噪声鼓组，A 小调，120 BPM
- 循环无缝的两条硬约束：
  1) 总样本数 = 小节数 × 每小节样本数，循环点落在正拍上；
  2) 最后半拍留空，所有音符在第 15.5 秒前起音并自然衰减到 0，
     循环回开头时不会出现「咔」的接缝。

用法：python tools/make_bgm.py
"""

import array
import math
import os
import random
import wave

SR = 22050
BPM = 120
BEAT = 60.0 / BPM            # 0.5 s
BAR = BEAT * 4               # 2 s
BARS = 8
TOTAL = BAR * BARS           # 16 s
N = int(round(TOTAL * SR))   # 352800
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "web", "media", "bgm-8bit.wav")

random.seed(8)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def env(i, n, attack=0.006, release=0.05):
    """线性 AR 包络：起音短、结尾收到 0，避免爆音。"""
    a = int(attack * SR)
    r = int(release * n) if release < 1 else int(release * SR)
    if i < a:
        return i / a
    if i >= n - r:
        return max(0.0, (n - i) / max(1, r))
    return 1.0


def add_square(buf, start, dur, freq, amp, duty=0.5, decay=0.0):
    """占空比方波。duty=0.5 是经典 chip 音色，0.125 更「细」。"""
    n = int(dur * SR)
    s0 = int(start * SR)
    if n <= 0 or s0 >= N:
        return
    n = min(n, N - s0)
    phase = 0.0
    step = freq / SR
    for i in range(n):
        phase += step
        if phase >= 1.0:
            phase -= int(phase)
        v = 1.0 if phase < duty else -1.0
        e = env(i, n)
        if decay:
            e *= math.exp(-decay * i / SR)
        buf[s0 + i] += v * amp * e


def add_tri(buf, start, dur, freq, amp, decay=0.0):
    """三角波，给贝斯一点厚度。"""
    n = int(dur * SR)
    s0 = int(start * SR)
    if n <= 0 or s0 >= N:
        return
    n = min(n, N - s0)
    phase = 0.0
    step = freq / SR
    for i in range(n):
        phase += step
        if phase >= 1.0:
            phase -= int(phase)
        v = 4.0 * abs(phase - 0.5) - 1.0      # -1..1
        e = env(i, n, release=0.06)
        if decay:
            e *= math.exp(-decay * i / SR)
        buf[s0 + i] += v * amp * e


def add_kick(buf, start, amp=0.9):
    """底鼓：正弦快速下滑 + 短促包络。"""
    n = int(0.12 * SR)
    s0 = int(start * SR)
    if s0 >= N:
        return
    n = min(n, N - s0)
    phase = 0.0
    for i in range(n):
        t = i / SR
        f = 120.0 * math.exp(-28.0 * t) + 45.0
        phase += f / SR
        v = math.sin(2 * math.pi * phase) * math.exp(-16.0 * t)
        buf[s0 + i] += v * amp


def add_hat(buf, start, amp=0.16, dur=0.045):
    n = int(dur * SR)
    s0 = int(start * SR)
    if s0 >= N:
        return
    n = min(n, N - s0)
    prev = 0.0
    for i in range(n):
        x = random.uniform(-1.0, 1.0)
        hp = x - prev * 0.65          # 一阶差分当高通，噪声变「嚓」
        prev = x
        buf[s0 + i] += hp * amp * math.exp(-60.0 * i / SR)


def add_snare(buf, start, amp=0.30):
    n = int(0.09 * SR)
    s0 = int(start * SR)
    if s0 >= N:
        return
    n = min(n, N - s0)
    for i in range(n):
        x = random.uniform(-1.0, 1.0)
        tone = math.sin(2 * math.pi * 190 * i / SR) * 0.35
        buf[s0 + i] += (x + tone) * amp * math.exp(-34.0 * i / SR)


# ── 和声：每 2 小节一个和弦（A 小调 Am–F–C–G）──
CHORDS = [
    (45, [57, 60, 64]),   # Am: A2  / A3 C4 E4
    (41, [53, 57, 60]),   # F : F2  / F3 A3 C4
    (48, [55, 60, 64]),   # C : C3  / G3 C4 E4
    (43, [55, 59, 62]),   # G : G2  / G3 B3 D4
]

# ── 主旋律 (小节, 拍, 时长拍, MIDI) ──
LEAD = [
    (0, 0, 1.0, 76), (0, 1, 0.5, 74), (0, 1.5, 0.5, 72), (0, 2, 2.0, 69),
    (1, 0, 1.0, 72), (1, 1, 1.0, 76), (1, 2, 2.0, 74),
    (2, 0, 1.5, 77), (2, 1.5, 0.5, 76), (2, 2, 2.0, 72),
    (3, 0, 1.0, 69), (3, 1, 1.0, 72), (3, 2, 2.0, 74),
    (4, 0, 1.0, 76), (4, 1, 1.0, 79), (4, 2, 1.0, 76), (4, 3, 1.0, 72),
    (5, 0, 1.5, 74), (5, 1.5, 0.5, 72), (5, 2, 2.0, 69),
    (6, 0, 1.0, 71), (6, 1, 1.0, 74), (6, 2, 2.0, 79),
    # 第 8 小节最后一拍留空：所有声音在循环点之前收干净
    (7, 0, 1.0, 77), (7, 1, 1.0, 76), (7, 2, 1.0, 74),
]

mix = [0.0] * N

# 贝斯：八分音符，根音与五度交替
for bar in range(BARS):
    root = CHORDS[(bar // 2) % 4][0]
    for k in range(8):
        t = bar * BAR + k * BEAT / 2
        note = root if k % 4 in (0, 3) else root + 7
        add_tri(mix, t, BEAT / 2 * 0.92, hz(note), 0.34, decay=2.2)
        add_square(mix, t, BEAT / 2 * 0.92, hz(note), 0.12, duty=0.25, decay=3.0)

# 琶音：十六分音符，和弦音循环
for bar in range(BARS):
    tones = CHORDS[(bar // 2) % 4][1]
    pattern = [tones[0], tones[1], tones[2], tones[1]]
    for k in range(16):
        t = bar * BAR + k * BEAT / 4
        note = pattern[k % 4] + 12
        add_square(mix, t, BEAT / 4 * 0.85, hz(note), 0.10, duty=0.125, decay=6.0)

# 主旋律：方波 50%，带一点起音滑落感
for bar, beat, dur, midi in LEAD:
    t = bar * BAR + beat * BEAT
    add_square(mix, t, dur * BEAT * 0.94, hz(midi), 0.20, duty=0.5, decay=1.2)

# 鼓组：底鼓 1/3 拍，军鼓 2/4 拍，踩镲八分音符
for bar in range(BARS):
    for b in range(4):
        t = bar * BAR + b * BEAT
        add_kick(mix, t, 0.85 if b % 2 == 0 else 0.55)
        if b % 2 == 1:
            add_snare(mix, t, 0.26)
    for k in range(8):
        add_hat(mix, bar * BAR + k * BEAT / 2, 0.10 if k % 2 == 0 else 0.06)

# ── 母带：去直流 → 软限幅 → 归一化 ──
dc = sum(mix) / N
mix = [v - dc for v in mix]
peak = max(abs(v) for v in mix) or 1.0
gain = 0.72 / peak
out = []
for v in mix:
    x = v * gain
    out.append(math.tanh(x * 1.15) / math.tanh(1.15))   # 轻微软削，别糊

# 循环点两端各做极短淡化：从 0 起、到 0 收，循环接缝不会「咔」
fade_in = int(0.005 * SR)
for i in range(fade_in):
    out[i] *= i / fade_in

# 最后 30 ms 强制归零（最后一次起音在第 15.5 s，本应已静音）
fade = int(0.03 * SR)
for i in range(fade):
    idx = N - fade + i
    out[idx] *= (fade - i) / fade

data = array.array("h", (int(max(-1.0, min(1.0, v)) * 32767) for v in out))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with wave.open(OUT, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())

print(f"已生成 {OUT}")
print(f"时长 {N / SR:.3f}s | 样本 {N} | 峰值 {max(abs(v) for v in out):.2f} "
      f"| 大小 {os.path.getsize(OUT)/1024:.0f} KB")
print(f"首样本 {out[0]:+.4f} | 末样本 {out[-1]:+.4f}（应接近 0，循环无接缝）")
