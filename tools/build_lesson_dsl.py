# -*- coding: utf-8 -*-
"""从讲义重新生成「逐节版」课件的 DSL 与 manifest（build_all_lesson_ppt 的上游）。

为什么需要这一步：`build_all_lesson_ppt.py` 只读 `lessons-deck/NN/NN.slide`
（已经生成好的 DSL），**它不会回头读讲义 md**。所以改了讲义之后不重跑本脚本，
再重建 pptx 也只是把旧内容重打一遍。

用法：
  python tools/build_lesson_dsl.py              # 全部 22 个单元
  python tools/build_lesson_dsl.py 1 2 3 4 5 6 7 8

产物：
  python-course-ppt/lessons-deck/NN/MM.slide   每页一份 DSL
  python-course-ppt/lessons-deck/manifest.json 单元 -> 页列表（只更新被指定的单元）
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
DECK_SRC = os.path.join(ROOT, "python-course-ppt", "lessons-deck")
MANI = os.path.join(DECK_SRC, "manifest.json")


def load_builder():
    """build_lesson_ppt 是纯模块（没有 __main__），按文件路径加载。"""
    spec = importlib.util.spec_from_file_location(
        "build_lesson_ppt", os.path.join(TOOLS, "build_lesson_ppt.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    builder = load_builder()
    only = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None

    manifest = {}
    if os.path.exists(MANI):
        manifest = json.load(open(MANI, encoding="utf-8"))

    changed = 0
    for unit in range(22):
        if only and unit not in only:
            continue
        slides, meta = builder.build_unit_slides(unit)
        out_dir = os.path.join(DECK_SRC, f"{unit:02d}")
        os.makedirs(out_dir, exist_ok=True)
        for index, (_kind, dsl) in enumerate(slides, 1):
            path = os.path.join(out_dir, f"{index:02d}.slide")
            old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            if old != dsl:
                open(path, "w", encoding="utf-8").write(dsl)
                changed += 1
        entries = []
        for index, item in enumerate(meta, 1):
            entry = {"slide": index}
            entry.update(item)
            entries.append(entry)
        manifest[str(unit)] = entries
        print(f"  单元 {unit:>2}：{len(slides)} 页 DSL")

    json.dump(manifest, open(MANI, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n写出 {changed} 页有变化的 DSL；manifest 覆盖 {len(manifest)} 个单元")


if __name__ == "__main__":
    main()
