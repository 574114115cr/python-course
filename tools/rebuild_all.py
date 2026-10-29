# -*- coding: utf-8 -*-
"""一条命令把「课件 + 站点 + 两个交付包」全部重出并对齐。

背景：课件相关的活分在 8 个脚本里（DSL → pptx → 备注 → 图片 → 播放器 →
安卓 webDir → 便携包 → 各种校验），顺序错一步就会出现「网页新、下载旧」。
更麻烦的是：只要有一个 pptx 被别的进程占着（写不进），重建就会变成
「一半单元是新版、一半是旧版」——比不重建更糟。

所以本脚本第一步是**前置锁检查**：任何一个 pptx 打不开就整体拒绝执行，并明确
告诉你该重启什么。解锁后再跑同一条命令，22 个单元一次全对。

用法：
  python tools/rebuild_all.py              # 全量：单元 0-21 + 下游全部
  python tools/rebuild_all.py --decks-only # 只做课件（不重打安卓/便携包）
  python tools/rebuild_all.py --check      # 只做锁检查
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
DECK_DIR = os.path.join(ROOT, "python-course-ppt", "逐节课件")
UNITS = [str(u) for u in range(22)]


def probe_writable(path):
    """能不能拿写权限。拿不到多半是别的进程占着句柄（共享冲突）。"""
    try:
        with open(path, "r+b") as fh:
            fh.read(4)
        return True
    except OSError:
        return False


def preflight():
    """任何一个 deck 写不进，就整体拒绝执行——避免新旧混排。"""
    targets = []
    if os.path.isdir(DECK_DIR):
        targets += sorted(os.path.join(DECK_DIR, f)
                          for f in os.listdir(DECK_DIR) if f.endswith(".pptx"))
    outline = os.path.join(ROOT, "python-course-ppt", "Python阶段0-2课程大纲.pptx")
    if os.path.exists(outline):
        targets.append(outline)

    locked = [p for p in targets if not probe_writable(p)]
    if not locked:
        print(f"前置检查：{len(targets)} 个课件全部可写，可以重建")
        return True

    print(f"前置检查：{len(locked)} / {len(targets)} 个课件被占用，拒绝执行。\n")
    for p in locked:
        print("  占用：", os.path.basename(p))
    print("""
这些文件被别的进程持有写句柄（Windows 上表现为「正由另一进程使用」）：
读得出、写不进、删不掉、改不了名，从本进程内部无法解除。

解除办法（任选其一，之后重跑本条命令）：
  1) 完全退出 WorkBuddy（含托盘图标）再打开；
  2) 注销当前 Windows 用户后重新登录；
  3) 重启系统（最彻底）。

不要只重建「能写的那些单元」：那会让封面/要点变成新旧两种版式，
比统一旧版更难解释。
""")
    return False


def step(title, args, allow_fail=False):
    print(f"\n=== {title}")
    r = subprocess.run([PY] + args, cwd=ROOT)
    if r.returncode != 0 and not allow_fail:
        print(f"!! 失败（退出码 {r.returncode}）：{title}")
        return False
    return True


def node_step(title, script):
    print(f"\n=== {title}")
    r = subprocess.run(["node", os.path.join("tools", script)], cwd=ROOT)
    return r.returncode == 0


def main():
    only_check = "--check" in sys.argv
    decks_only = "--decks-only" in sys.argv

    if not preflight():
        return 2
    if only_check:
        return 0

    ok = step("1/8 讲义 → DSL", [os.path.join("tools", "build_lesson_dsl.py")] + UNITS)
    # 注意：备注在这一步里和 pptx 合并成一次写入（build_unit → add_slide_notes.annotate）。
    # 单独再跑一次 add_slide_notes 是没用的：文件刚被写就已经被占住，写不进第二次。
    ok = ok and step("2/8 DSL → pptx（含演讲者备注）+ 截图",
                     [os.path.join("tools", "build_all_lesson_ppt.py")] + UNITS)
    ok = ok and step("3/8 瘦身 + WebP + 总览页",
                     [os.path.join("tools", "finish_lesson_ppt.py")])
    ok = ok and step("4/8 大纲课件（23 页）", [os.path.join("tools", "rebuild_outline.py")])
    if not ok:
        print("\n课件链路中断，下游打包已跳过（避免把半成品打进去）")
        return 1

    if not decks_only:
        # 深色表由浅色表派生：打包前必须重跑，否则安卓/便携包里的页面还是上一版配色
        ok = ok and step("5/8 主题派生（浅色 → 深色）", [os.path.join("tools", "theme.py")])
        ok = ok and step("5b 神经元背景注入", [os.path.join("tools", "neuron.py")])
        ok = ok and step("6/8 安卓 webDir", [os.path.join("tools", "build_android_www.py")])
        ok = ok and node_step("校验安卓 webDir", "verify_android_www.mjs")
        ok = ok and step("7/8 便携包", [os.path.join("tools", "build_portable.py")])
        ok = ok and node_step("校验便携包", "verify_portable.mjs")
        ok = ok and node_step("8/8 PWA", "verify_pwa.mjs")

    print("\n=== 末检：站点审计 / 课节 / 输出一致性 / 窄屏")
    for t, a in (("站点审计", ["tools/audit_all.py"]),
                 ("课节页", ["tools/verify_lessons.py"]),
                 ("运行结果一致性", ["tools/check_outputs.py"])):
        step(t, [os.path.join(*a)])
    node_step("390px 无溢出", "verify_mobile_390.mjs")
    node_step("深浅两套主题对比度", "verify_dark.mjs")
    node_step("补强项实测（周计划/ETA/答案按需/打印）", "verify_extras.mjs")
    node_step("神经元背景实测（开关/密度/跟随/打印）", "verify_neuron.mjs")

    # 备注最容易在重建时被无声抹掉（slidep create 是整份重写），单独核一遍
    import zipfile
    import re
    missing = []
    for u in range(22):
        f = os.path.join(DECK_DIR, f"Python讲授课件-单元{u:02d}.pptx")
        if not os.path.exists(f):
            continue
        z = zipfile.ZipFile(f)
        pages = len([x for x in z.namelist()
                     if re.match(r"ppt/slides/slide\d+\.xml$", x)])
        notes = len([x for x in z.namelist() if "notesSlide" in x])
        if notes < pages:
            missing.append(f"单元{u:02d} 备注 {notes}/{pages}")
    if missing:
        print("\n!! 备注不全：" + "；".join(missing))
        ok = False
    else:
        print("\n备注覆盖：22 个单元全部齐全")

    print("\n全部完成" if ok else "\n完成，但有步骤失败（见上）")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
