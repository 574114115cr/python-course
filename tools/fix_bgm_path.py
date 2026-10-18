# -*- coding: utf-8 -*-
"""一次性批修：课件播放器里 bgm.js 的相对路径写错一级。

build_all_lesson_ppt.py 曾在 22 个单元播放器里生成 `../media/bgm.js`
（从 web/ppt/u/ 出发只到 web/ppt/media/，实际文件在 web/media/），
播放器控制台一直 404、BGM 不响。生成器已改为 `../../media/bgm.js`，
本脚本把已生成的旧产物一次性补齐，让「源修好了」和「现状也是对的」同时成立。

运行：venv python tools/fix_bgm_path.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
# 生成器模板里的正确引用（build_ppt_hub.py / build_ppt_html.py 的写法）
GOOD = "../../media/bgm.js"


def main():
    fixed = []
    for cur, _dirs, files in os.walk(WEB):
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(cur, f)
            s = open(p, encoding="utf-8").read()
            m = re.search(r'src="([^"]*media/bgm\.js)"', s)
            if not m:
                continue
            ref = m.group(1)
            if ref == GOOD:
                continue
            target = os.path.normpath(os.path.join(cur, ref))
            if os.path.exists(target):
                continue                      # 能解析到真文件，不动
            s = s.replace(f'src="{ref}"', f'src="{GOOD}"')
            open(p, "w", encoding="utf-8").write(s)
            fixed.append(os.path.relpath(p, ROOT))
    for f in fixed:
        print("已修:", f)
    print(f"共修 {len(fixed)} 个页面")


if __name__ == "__main__":
    main()
