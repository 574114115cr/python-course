"""从 DSH 桌宠插件提取官方 Q 版鲸鱼娘动画，做成课程讲解员资产。

两个来源：
1. standalone 帧序列（RGBA 透明 webp，11 个动作）→ 直接复制
   C:/Users/57411/AppData/Local/Programs/dsh-pet-standalone-webm/_internal/
   assets/characters/shenshen/frameseq/
2. 插件本体黑底 webm（106 个动作）→ ffmpeg 解帧 + 亮度键抠图（LO=6/HI=28，
   背景纯黑且角色内部无近黑像素，实测深蓝裙无损失）
   C:/Users/57411/.dsh/profiles/desktop/node_modules/dsh-pet/assets/webm/

每帧跟踪脸框（肤色连通域 + 时序平滑；11 个片段第 1 帧都是同一 idle 姿态，
肤色域里脸永远是大头），嘴 = 脸框内固定相对位（idle 帧 1 目测标定）。
输出 tools/assets/pet/<动作>/f_0000.webp… + pet_meta.json。
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time
from collections import deque

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "assets", "pet")
FFMPEG = os.path.expanduser("~/.workbuddy/binaries/python/envs/default/Lib/"
                            "site-packages/imageio_ffmpeg/binaries/"
                            "ffmpeg-win-x86_64-v7.1.exe")
SEQ_BASE = ("C:/Users/57411/AppData/Local/Programs/dsh-pet-standalone-webm/"
            "_internal/assets/characters/shenshen/frameseq")
WEBM_BASE = ("C:/Users/57411/.dsh/profiles/desktop/node_modules/dsh-pet/"
             "assets/webm")

# 课程动作名 → (来源类型, 来源路径片段)。src 里不含 hash 后缀，运行时匹配。
ACTIONS = {
    "wave":   ("seq", "click/点击回应-元气挥手"),
    "idle":   ("seq", "idle/待机呼吸休闲"),
    "happy":  ("seq", "click/点击回应-开心跃动"),
    "shy":    ("seq", "click/点击回应-害羞惊讶"),
    "angry":  ("seq", "click/点击回应-傲娇生气"),
    "look":   ("seq", "turn/东张西望"),
    "think":  ("webm", "工作状态-思考冒泡"),
    "code":   ("webm", "写代码"),
    "type":   ("webm", "工作状态-忙碌点按"),
    "sigh":   ("webm", "工作状态-垂头叹气冒汗"),
    "party":  ("webm", "工作状态-雀跃庆祝"),
    "bow":    ("webm", "女仆屈膝礼仪"),
}

# idle 帧 1 脸框 (276,184,345,213) 内嘴中心 (308,203) 的相对位（目测标定）
MOUTH_REL = (0.46, 0.66)
KEY_LO, KEY_HI = 6, 28      # 亮度键阈值


def is_skin(p):
    r, g, b, a = p
    if a < 150:
        return False
    return r > 170 and r > b + 22 and g > b and g > 105 and r < 252


def face_bbox(im, roi):
    """在 roi 内找最大肤色连通域的包围盒。roi=(x0,y0,x1,y1)。"""
    px = im.load()
    x0, y0, x1, y1 = roi
    w, h = im.size
    x1, y1 = min(x1, w), min(y1, h)
    seen = {}
    best = None
    for y in range(y0, y1):
        for x in range(x0, x1):
            if (x, y) in seen or not is_skin(px[x, y]):
                continue
            q = deque([(x, y)])
            seen[(x, y)] = 1
            n = 0
            bx0 = by0 = 10 ** 9
            bx1 = by1 = -1
            while q:
                X, Y = q.popleft()
                n += 1
                bx0, bx1 = min(bx0, X), max(bx1, X)
                by0, by1 = min(by0, Y), max(by1, Y)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    p2 = (X + dx, Y + dy)
                    if x0 <= p2[0] < x1 and y0 <= p2[1] < y1 \
                            and p2 not in seen and is_skin(px[p2[0], p2[1]]):
                        seen[p2] = 1
                        q.append(p2)
            if n > 200 and (best is None or n > best[0]):
                best = (n, (bx0, by0, bx1, by1))
    return best[1] if best else None


def track_all(ims):
    """逐帧跟踪脸框。首帧全图上半部搜索，之后 ROI 跟随上一帧 ±30px。"""
    boxes = []
    prev = None
    for im in ims:
        if prev is None:
            roi = (180, 120, 460, 250)
        else:
            roi = (prev[0] - 30, prev[1] - 30, prev[2] + 30, prev[3] + 30)
        bb = face_bbox(im, roi)
        if bb is None:            # 极少数帧脸被遮挡：沿用上一帧
            bb = prev
        boxes.append(bb)
        prev = bb
    return boxes


def webm_frames(src):
    """ffmpeg 解 webm → png 帧列表（临时目录）。"""
    tmp = os.path.join(ROOT, ".cache", "pet_webm_%d" % time.time())
    os.makedirs(tmp, exist_ok=True)
    subprocess.run([FFMPEG, "-v", "error", "-i", src,
                    os.path.join(tmp, "f_%04d.png")],
                   check=True, timeout=300)
    return sorted(glob.glob(tmp + "/f_*.png")), tmp


def luminance_key(im):
    """纯黑底 → alpha（亮度键查表，C 速度）。LO..HI 线性过渡。"""
    lum = im.convert("L")
    table = [0 if v <= KEY_LO else
             255 if v >= KEY_HI else
             int((v - KEY_LO) / (KEY_HI - KEY_LO) * 255)
             for v in range(256)]
    out = im.convert("RGB").copy()
    out.putalpha(lum.point(table))
    return out


def main():
    only = set(sys.argv[1:]) or None
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for name, (kind, sub) in ACTIONS.items():
        if only and name not in only:
            continue
        if kind == "seq":
            hits = glob.glob(os.path.join(SEQ_BASE, sub + ".*"))
            if len(hits) != 1:
                raise SystemExit("%s: 匹配到 %d 个源目录" % (name, len(hits)))
            frames = sorted(glob.glob(hits[0] + "/f_*.webp"))
            src_im = [Image.open(f).convert("RGBA") for f in frames]
            tmp = None
        else:
            src = os.path.join(WEBM_BASE, sub + ".webm")
            frames, tmp = webm_frames(src)
            src_im = [luminance_key(Image.open(f)) for f in frames]
        boxes = track_all(src_im)
        fdir = os.path.join(OUT, name)
        if os.path.exists(fdir):
            shutil.move(fdir, os.path.join(ROOT, ".cache", "pet_old_%d" % time.time()))
        os.makedirs(fdir)
        for i, im in enumerate(src_im):
            im.save(os.path.join(fdir, "f_%04d.webp" % i), lossless=False, quality=90)
        if tmp:
            shutil.move(tmp, os.path.join(ROOT, ".cache", "pet_webm_done_%d" % time.time()))
        bb0 = boxes[0]
        fw = bb0[2] - bb0[0]
        fh = bb0[3] - bb0[1]
        meta[name] = {
            "dir": name,
            "frames": len(src_im),
            "fps": 24,
            "face0": list(bb0),
            "mouth": [round(bb0[0] + MOUTH_REL[0] * fw, 1),
                      round(bb0[1] + MOUTH_REL[1] * fh, 1)],
            "mouth_rel": list(MOUTH_REL),
            "boxes": boxes,
        }
        print("%-6s %d 帧 脸0=%s" % (name, len(src_im), bb0))
    with open(os.path.join(OUT, "pet_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print("\n写好 %d 个动作 → %s" % (len(meta), OUT))


if __name__ == "__main__":
    main()
