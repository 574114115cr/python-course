"""把 ImageGen 生成的动作立绘做成资产：抠背景 → 裁边 → 统一高度 → 记脸中心。

用法：python tools/make_pose_assets.py [源目录]
默认源目录 .cache/char3（ImageGen 输出），产物写 tools/assets/pose/。

为什么要记脸中心：口型贴片是逐帧画在嘴上的，嘴锚点不能写死——
各动作的头会轻微位移，锚点必须跟着脸走。脸中心用「最大肤色连通域」
的包围盒中心估计（Q 版角色脸占肤色面积绝大部分），再叠一个从
idle 图实测量出的嘴偏移即可。
"""
import glob
import json
import os
import sys
from collections import deque

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "tools", "assets", "pose")

# 生成顺序 → 动作名（ImageGen 按时间戳落盘，文件名不可读，按 mtime 对应）
POSES = [
    ("idle", "站立待机"),
    ("wave", "招手"),
    ("guide", "讲解指引"),
    ("think", "思考"),
    ("wow", "强调惊喜"),
    ("confuse", "疑惑歪头"),
    ("fist", "加油握拳"),
    ("present", "双手展示"),
    ("pointdown", "指向下方"),
    ("nod", "点头认可"),
    ("shrug", "摊手无奈"),
    ("clap", "鼓掌"),
    ("listen", "俯身倾听"),
]

# 嘴锚点：逐张视觉实测（裁脸放大 5 倍人工读数，写入 .cache/face_*.png 核对）。
# 不能用「脸中心 + 固定偏移」——12/13 张是侧脸/歪头姿势，嘴在脸中心
# 左上方而非正下方，固定偏移会把锚点画到领结上。
# 也不能靠唇色掩码自动检测——嘴线是 2-3px 抗锯齿细线，阈值稍动就碎，
# 且手/腮红/眼线颜色相近，误判率太高。重建资产后必须重新目测核对。
MOUTH_MANUAL = {
    "idle": (264.0, 344.0), "wave": (216.0, 333.0), "guide": (224.0, 342.0),
    "think": (232.0, 351.0), "wow": (213.0, 326.0), "confuse": (228.0, 353.0),
    "fist": (242.0, 356.0), "present": (226.0, 348.0),
    "pointdown": (231.0, 352.0), "nod": (227.0, 346.0),
    "shrug": (223.0, 341.0), "clap": (238.0, 354.0), "listen": (232.0, 359.0),
}


def is_bg(p):
    mx, mn = max(p), min(p)
    return mn > 148 and mx - mn < 34


def cutout(path):
    """从整条边缘 BFS 抠掉浅色背景（单种子 floodfill 跨不过渐变）。"""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(px[x, y]) and not seen[y * w + x]:
                seen[y * w + x] = 1
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(px[x, y]) and not seen[y * w + x]:
                seen[y * w + x] = 1
                q.append((x, y))
    n = 0
    while q:
        x, y = q.popleft()
        n += 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] \
                    and is_bg(px[nx, ny]):
                seen[ny * w + nx] = 1
                q.append((nx, ny))
    out = Image.new("RGBA", (w, h))
    op = out.load()
    for y in range(h):
        base = y * w
        for x in range(w):
            if not seen[base + x]:
                r, g, b = px[x, y]
                op[x, y] = (r, g, b, 255)
    return out, n / float(w * h)


def is_skin(p):
    r, g, b, a = p
    if a < 120:
        return False
    return r > 170 and r > b + 22 and g > b and g > 105 and r < 252


def face_center(im):
    """最大肤色连通域的中心与面积（≈ 脸），返回 (cx, cy, 面积)。"""
    w, h = im.size
    px = im.load()
    seen = bytearray(w * h)
    best = None
    for sy in range(h):
        for sx in range(w):
            i = sy * w + sx
            if seen[i] or not is_skin(px[sx, sy]):
                continue
            q = deque([(sx, sy)])
            seen[i] = 1
            comp = []
            while q:
                x, y = q.popleft()
                comp.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] \
                            and is_skin(px[nx, ny]):
                        seen[ny * w + nx] = 1
                        q.append((nx, ny))
            if best is None or len(comp) > len(best):
                best = comp
    if not best:
        return None
    xs = [c[0] for c in best]
    ys = [c[1] for c in best]
    return (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, len(best)


# 生成图的角色大小有 ±5% 漂移（ImageGen 固有），直接用会「忽大忽小」。
# 以 idle 的脸尺度（√肤色面积）为基准把所有姿势归一化，再裁到角色包围盒
# （留 PAD 透明边距给摇摆旋转用）。
# 不统一画布：裁边后各图宽度不同，定位靠「脸锚点」——draw_char 把每张的
# 脸对齐到屏幕同一个点，换姿势时视线不跳（脚底略有出入但看不出来）。
PAD = 12


def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, ".cache", "char3")
    files = [p for p in sorted(glob.glob(os.path.join(src_dir, "*.png")),
                               key=lambda p: os.path.getmtime(p))
             if "sheet" not in os.path.basename(p)]
    if not files:
        raise SystemExit("源目录没有 PNG：%s" % src_dir)
    # idle 单独来自 char2 那次（睁眼版），其余本次生成
    idle = os.path.join(ROOT, "tools", "assets", "whale-girl.png")
    jobs = [("idle", "站立待机", idle)]
    if len(files) != len(POSES) - 1:
        print("⚠️ 源图 %d 张，预期 %d 张（不含 idle）" % (len(files), len(POSES) - 1))
    jobs += [(POSES[i + 1][0], POSES[i + 1][1], f)
             for i, f in enumerate(files[:len(POSES) - 1])]

    os.makedirs(OUT_DIR, exist_ok=True)
    # 第一遍：抠图 + 量脸尺度
    cut, fcs = {}, {}
    for name, _, path in jobs:
        if name == "idle":
            im = Image.open(path).convert("RGBA")
            cut[name] = im
        else:
            im, bgp = cutout(path)
            cut[name] = im
        fcs[name] = face_center(im)
        if fcs[name] is None:
            raise SystemExit("%s 没找到肤色域" % name)
    ref_scale = fcs["idle"][2] ** 0.5

    # 第二遍：归一化缩放 + 裁边（脸/嘴锚点随之平移）
    meta = {}
    for name, title, _ in jobs:
        im = cut[name]
        fx0, fy0, area = fcs[name]
        sc = ref_scale / (area ** 0.5)
        if abs(sc - 1.0) > 0.005:
            im = im.resize((max(1, round(im.width * sc)),
                            max(1, round(im.height * sc))), Image.LANCZOS)
        bbox = im.getchannel("A").getbbox()
        im = im.crop(bbox)
        fcx = (fcs[name][0] - bbox[0]) * sc + PAD
        fcy = (fcs[name][1] - bbox[1]) * sc + PAD
        cv = Image.new("RGBA", (im.width + PAD * 2, im.height + PAD * 2))
        cv.alpha_composite(im, (PAD, PAD))
        dst = os.path.join(OUT_DIR, "%02d-%s.png" % (len(meta) + 1, name))
        cv.save(dst)
        # 嘴锚点用逐张目测值。MOUTH_MANUAL 的量测基准就是这批源图归一化后的
        # 坐标（sc 见 poses.json），源图不变则直接可用；若换了源图导致
        # scale 明显变化，必须重新目测——侧脸/歪头下没有任何自动方法可靠。
        mm = MOUTH_MANUAL[name]
        mx, my = mm
        meta[name] = {"title": title, "file": os.path.basename(dst),
                      "face": [round(fcx, 1), round(fcy, 1)],
                      "mouth": [round(mx, 1), round(my, 1)],
                      "scale": round(sc, 3), "size": list(cv.size)}
        print("%-10s %-6s 缩放%.3f %dx%d 脸(%.0f,%.0f) 嘴(%.0f,%.0f)"
              % (name, title, sc, cv.size[0], cv.size[1], fcx, fcy, mx, my))

    with open(os.path.join(OUT_DIR, "poses.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print("\n写好 %d 张 → %s" % (len([k for k in meta if not k.startswith('_')]), OUT_DIR))


if __name__ == "__main__":
    main()
