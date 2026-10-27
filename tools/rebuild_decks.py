# -*- coding: utf-8 -*-
"""一条命令重建逐节课件：讲义 → DSL → pptx → 演讲者备注 → 图片/WebP。

为什么单独写一个：这四步分散在四个脚本里，顺序错了就会「课件和讲义不同步」
（例如先 build_all_lesson_ppt 再重新生成 DSL，pptx 里还是旧内容；
或者漏掉 add_slide_notes，pptx 重建后备注全丢——slidep create 是整份重写）。

用法：
  python tools/rebuild_decks.py            # 默认重建单元 1-8
  python tools/rebuild_decks.py 1 2 3      # 只重建指定单元
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

UNITS = [int(x) for x in sys.argv[1:]] or list(range(1, 9))


def step(title, args):
    print(f"\n=== {title}")
    r = subprocess.run([PY] + args, cwd=ROOT)
    if r.returncode != 0:
        print(f"!! 失败（退出码 {r.returncode}）：{title}")
        return False
    return True


def main():
    units = [str(u) for u in UNITS]
    ok = step("1/4 从讲义重生成 DSL", [os.path.join("tools", "build_lesson_dsl.py")] + units)
    ok = ok and step("2/4 生成 pptx + 截图",
                     [os.path.join("tools", "build_all_lesson_ppt.py")] + units)
    ok = ok and step("3/4 补演讲者备注", [os.path.join("tools", "add_slide_notes.py")])
    ok = ok and step("4/4 重渲染 + 瘦身 + WebP + 总览页",
                     [os.path.join("tools", "finish_lesson_ppt.py"), "--rerender"])
    print("\n课件重建完成" if ok else "\n课件重建中断，见上面的报错")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
