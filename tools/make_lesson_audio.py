#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第一课旁白配音（edge-tts）+ 分幕时间轴。

设计要点：
  - 字幕文本与朗读文本在这里**单一来源**定义，make_lesson_video.py 直接 import，
    避免「画面字幕」和「配音稿」两处各写一份而走样。
  - 朗读文本（say）可以和字幕（sub）不同：命令行符号、▶、花括号这类东西
    看着清楚、念出来却别扭，所以念的版本单独写。
  - 时间轴由真实语音时长反推：先合成 → 测时长 → 排布每句起止 → 得到各幕时长，
    画面再去适配声音（而不是让声音硬塞进固定时长里）。
  - 断网 / 没装 edge-tts 时不影响视频生成：缺音轨就退回静音 + 原节奏。

用法：
  python tools/make_lesson_audio.py            # 合成并写出音轨 + 时间轴
  python tools/make_lesson_audio.py --check    # 只报告当前状态
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache", "tts")
OUT_WAV = os.path.join(CACHE, "lesson01-audio.wav")
OUT_JSON = os.path.join(CACHE, "lesson01-narr.json")

VOICE = "zh-CN-XiaoxiaoNeural"   # 女声，讲解类最常用；男声换 zh-CN-YunxiNeural
RATE = "+10%"                    # 教学视频略快一点，拖沓会走神
SR = 24000                       # edge-tts 原生 24 kHz 单声道
GAP = 0.34                       # 句间停顿
TAIL = 0.80                      # 幕末句念完后的留白


# ── 剧本 ────────────────────────────────────────────────────────
# 每幕：min = 动画本身需要的最短时长；subs = (字幕, 朗读稿, 最早开始时刻)
# 「最早开始时刻」用于卡画面切换：比如报错演示在第 7.2 秒才出现，
# 讲报错的那句话就不能早于它。
SCRIPT = [
    {   # 0 片头
        "min": 4.6, "lead": 1.0,
        "subs": [
            ("第 1 课", "第 1 课，装好 Python 和 VS Code。", None),
        ],
    },
    {   # 1 解释器
        "min": 11.4, "lead": .55,
        "subs": [
            ("先记住一件事：代码文件自己不会跑。",
             "先记住一件事：代码文件自己不会跑。", None),
            ("解释器才是那个真正干活的程序。",
             "解释器才是那个真正干活的程序。", None),
            ("所以第一步，一定是把 Python 装好。",
             "所以第一步，一定是把 Python 装好。", None),
        ],
    },
    {   # 2 终端
        "min": 11.2, "lead": .55,
        "subs": [
            ("装没装好，用 python --version 一句话验证。",
             "装没装好，用 python version 命令一句话验证。", None),
            ("看到 Python 3.12.x，就说明可以开工了。",
             "看到 Python 三点十二的版本号，就说明可以开工了。", None),
            ("cd 进入目录，dir 或 ls 看看里面有什么。",
             "cd 进入目录，dir 或者 ls，看看里面有什么。", None),
        ],
    },
    {   # 3 VS Code
        "min": 11.2, "lead": .55,
        "subs": [
            ("先装 VS Code，再在扩展里搜 Python。",
             "先装 VS Code，再在扩展里搜索 Python。", None),
            ("装完扩展，右上角就多了一个 ▶ 运行按钮。",
             "装完扩展，右上角就多了一个运行按钮。", None),
            ("红波浪线是好事——它替你提前发现错。",
             "红波浪线是好事，它替你提前发现错。", None),
        ],
    },
    {   # 4 跟着敲
        "min": 13.0, "lead": .55,
        "subs": [
            ("新建 hello.py，先写这三行。",
             "新建 hello.py，先写这三行。", None),
            ("f 开头 + 花括号 = 把变量塞进字符串。",
             "f 开头加花括号，等于把变量塞进字符串。", None),
            ("故意少一个右括号：报错会明确指到第 3 行。",
             "故意少一个右括号，报错会明确指到第三行。", 7.45),
        ],
    },
    {   # 5 小结
        "min": 11.5, "lead": .55,
        "subs": [
            ("这三条都能点头，就可以往下走了。",
             "这三条都能点头，就可以往下走了。", None),
            ("任何一条卡住，回到对应小节重看一遍。",
             "任何一条卡住，回到对应小节重看一遍。", None),
            ("下一课我们给数据贴上名字。",
             "下一课，我们给数据贴上名字。", None),
        ],
    },
]


def sub_texts(scene_idx):
    """某幕的字幕文本列表（画面用）。"""
    return [s[0] for s in SCRIPT[scene_idx]["subs"]]


# ── 工具 ────────────────────────────────────────────────────────
def _ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _wav_len(path):
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


async def _say(text, mp3):
    import edge_tts
    c = edge_tts.Communicate(text, VOICE, rate=RATE)
    await c.save(mp3)


def load():
    """给视频脚本用：返回时间轴 dict，缺产物则返回 None（静音降级）。"""
    if not (os.path.exists(OUT_JSON) and os.path.exists(OUT_WAV)):
        return None
    try:
        with open(OUT_JSON, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


# ── 主流程 ──────────────────────────────────────────────────────
def build(force=False):
    os.makedirs(CACHE, exist_ok=True)
    try:
        ff = _ff()
    except Exception:
        print("缺少 imageio-ffmpeg（pip install imageio-ffmpeg）")
        return 1

    # 1) 逐句合成 + 转 wav
    for si, sc in enumerate(SCRIPT):
        for li, (sub, say, ms) in enumerate(sc["subs"]):
            mp3 = os.path.join(CACHE, "s%d_%d.mp3" % (si, li))
            wav = os.path.join(CACHE, "s%d_%d.wav" % (si, li))
            if force or not os.path.exists(wav):
                if force or not os.path.exists(mp3):
                    try:
                        asyncio.run(_say(say, mp3))
                    except Exception as e:
                        print("合成失败 %s：%s" % (say[:12], str(e)[:120]))
                        return 1
                subprocess.run([ff, "-y", "-i", mp3, "-ar", str(SR), "-ac", "1",
                                "-c:a", "pcm_s16le", wav],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=120)
            print("  %d-%d %.2fs  %s" % (si, li, _wav_len(wav), say[:18]))

    # 2) 时间轴：幕内依次排布，幕长 = max(动画最短时长, 念完+留白)
    scenes, t0 = [], 0.0
    for si, sc in enumerate(SCRIPT):
        t = sc.get("lead", .55)
        subs = []
        for li, (sub, say, ms) in enumerate(sc["subs"]):
            d = _wav_len(os.path.join(CACHE, "s%d_%d.wav" % (si, li)))
            if ms is not None:
                t = max(t, ms)
            subs.append({"t": round(t, 3), "d": round(d, 3), "s": sub})
            t += d + GAP
        dur = max(sc["min"], t - GAP + TAIL)
        scenes.append({"start": round(t0, 3), "dur": round(dur, 3), "subs": subs})
        t0 += dur
    total = t0

    # 3) 按时间轴把各句 PCM 铺进一条完整音轨
    n = int(round(total * SR))
    buf = bytearray(n * 2)
    for si, sc in enumerate(scenes):
        for li, sub in enumerate(sc["subs"]):
            with wave.open(os.path.join(CACHE, "s%d_%d.wav" % (si, li)), "rb") as w:
                pcm = w.readframes(w.getnframes())
            off = int(round((sc["start"] + sub["t"]) * SR)) * 2
            end = min(len(buf), off + len(pcm))
            buf[off:end] = pcm[:end - off]

    with wave.open(OUT_WAV, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(bytes(buf))

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"voice": VOICE, "rate": RATE, "sr": SR, "total": round(total, 3),
                   "scenes": scenes}, f, ensure_ascii=False, indent=1)

    print("音轨 %.2fs / %.1f MB，共 %d 幕 %d 句"
          % (total, os.path.getsize(OUT_WAV) / 1048576.0, len(scenes),
             sum(len(s["subs"]) for s in scenes)))
    print("→ %s" % OUT_WAV)
    return 0


def check():
    n = load()
    if not n:
        print("未生成：%s（跑 python tools/make_lesson_audio.py）" % OUT_WAV)
        return 1
    print("音轨存在 %.1f MB / %.2fs / %s"
          % (os.path.getsize(OUT_WAV) / 1048576.0, n["total"], n["voice"]))
    for i, s in enumerate(n["scenes"]):
        print("  幕%d %.2fs：%s" % (i, s["dur"],
              " ".join("%.1f→%.1f" % (x["t"], x["t"] + x["d"]) for x in s["subs"])))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true", help="忽略缓存重新合成")
    a = ap.parse_args()
    return check() if a.check else build(a.force)


if __name__ == "__main__":
    sys.exit(main())
