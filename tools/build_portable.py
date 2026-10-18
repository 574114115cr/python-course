# -*- coding: utf-8 -*-
"""打包「便携版」课程站点：拷到任何电脑、解压、双击 index.html 即可用，
不需要安装 Python / Node / 任何依赖。

依据：站点是纯静态 HTML + 内联 CSS/JS + PNG，零 fetch/XHR；
已实测 file:// 协议下页面渲染、课件缩略图、localStorage 进度保存均正常。

产出：dist/Python课程包-便携版.zip
"""
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
# 同时产出一个「可直接拷走的文件夹」和一个 zip，用户任选
STAGE = os.path.join(DIST, "Python课程包-便携版")
ZIP_PATH = os.path.join(DIST, "Python课程包-便携版.zip")

# 要打进包的内容（相对项目根）
INCLUDE_FILES = ["index.html", "python-learning-roadmap.html",
                 "python-course-syllabus.html",
                 "sw.js", "manifest.webmanifest",
                 "icon-192.png", "icon-512.png",
                 "icon-maskable-192.png", "icon-maskable-512.png"]
INCLUDE_DIRS = ["web", "course", "exercises", "python-course-ppt"]
INCLUDE_EXTRA = ["python-course-ppt/DESIGN.md", "python-course-ppt/STORY.md"]

# 这些不打包
EXCLUDE_DIRS = {".workbuddy", "tools", "dist", "__pycache__", ".cache", ".slidep",
                "assets", "slides", "node_modules", "_stage", "lessons-deck"}
EXCLUDE_EXT = {".pyc", ".log", ".jsonl"}
EXCLUDE_NAME_PREFIX = ("tmp", "_")

README = """Python 课程包 · 便携版
================================================================

【怎么用】—— 不需要安装任何东西

  1. 把整个文件夹解压到任意位置（桌面、U 盘都行）
  2. 双击打开   index.html
  3. 用浏览器浏览即可（Chrome / Edge / Firefox 都行）

  注意：请解压后再打开，不要直接在压缩包里双击——
        压缩包内的文件浏览器无法正常引用。


【里面有什么】

  index.html ............... 课程主页（建议从这里进）
  python-learning-roadmap.html .. 学习路线图
  python-course-syllabus.html ... 总课表

  web/00.html ~ web/21.html ..... 22 份单元讲义（可直接阅读）
  web/lessons/ ................. 111 节课节页，一节一节学
  web/bank.html ................ 84 道分阶练习题库（答案默认折叠，可标「已掌握 / 待复习」）
  web/gate1.html ............... 关卡 1 验收清单（4 条验收 / 19 项自测）
  web/gate2.html ............... 关卡 2 验收清单（5 条硬指标）（答案默认折叠，可勾「已掌握」）
  web/gate1.html ............... 关卡 1 验收清单（4 条验收 / 19 项自测）
  web/gate2.html ............... 关卡 2 验收清单（5 条硬指标）
  web/ppt/u/index.html ......... 逐节版讲授课件总览（22 个单元）
  web/ppt/u/NN.html ............ 单元 NN 的课件：每节课 2 页
                                 （课节页：目标/实操/作业；知识点页：要点 + 代码示例）
  web/ppt/index.html ........... 课程大纲课件 23 页（宣讲与排期用）

  python-course-ppt/逐节课件/*.pptx ... 22 份逐节版课件源文件
  python-course-ppt/*.pptx .......... 大纲课件源文件
                                        （都可用 PowerPoint / WPS 编辑）

  course/ ...................... 讲义源文件（Markdown，可自行修改）
  exercises/ ................... 题库源文件


【功能说明】

  · 每页都有勾选框，标记完成；进度保存在本机浏览器里，
    换电脑不会同步，也不会因为关机丢失。
  · 课节页右侧「配套资料」能直接跳到对应的讲义、课件、题库。
  · 课件支持键盘左右键翻页，也能按 #s14 这样的地址直达某一页。
  · 课节页右侧「配套资料」里的「课件」会直接跳到本节那两页，
    不用再从大纲里找。
  · 全站有 8-bit 背景音乐（左下角「音乐 开/关」）：
    换页会接着上次的位置放，开关状态各页通用；浏览器限制自动播放，
    首次进来点一下页面任意处才会响。音乐文件在 web/media/bgm-8bit.wav。
  · 首页有全局搜索（Ctrl+K）：课节、讲义小节、题库、课件一起搜。
  · 题库每题默认只显示题目，点开才看答案；可勾「已掌握」记录进度。
  · 关卡页按条勾选，顶部显示「已达标 x/N」，全绿才算过关。
  · 每个单元页右上角能看到「本单元已学 x/y 节」。
  · 进度存在本机浏览器：换电脑前到首页点「导出进度」，到新电脑点「导入进度」。
  · 首页有全局搜索（Ctrl+K）：课节、讲义小节、题库、课件一起搜。
  · 题库每题默认只显示题目，点开才看答案；可勾「已掌握」记录进度。
  · 关卡页按条勾选，顶部显示「已达标 x/N」，全绿才算过关。
  · 每个单元页右上角能看到「本单元已学 x/y 节」。
  · 进度存在本机浏览器：换电脑前到首页点「导出进度」，到新电脑点「导入进度」。
  · 想重来一遍：浏览器里清一下本站数据即可。


【常见问题】

  Q: 双击 index.html 没反应 / 页面是白板？
  A: 确认是「解压后」的文件夹，不是压缩包内。

  Q: 进度勾选会丢吗？
  A: 不会，存在本机浏览器。但换浏览器或清缓存会重置。

  Q: 想给别人一份，直接拷这个文件夹就行吗？
  A: 行。整个文件夹拷过去，对方解压双击 index.html 即可。

================================================================
依据《Python 编程：从入门到实践（第 3 版）》中文版全 20 章
22 个单元 · 111 节课 · 2 道关卡 · 3 个大项目
"""


def should_skip(name):
    if name in EXCLUDE_DIRS:
        return True
    if os.path.splitext(name)[1] in EXCLUDE_EXT:
        return True
    if name.startswith(EXCLUDE_NAME_PREFIX):
        return True
    return False


def main():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE, exist_ok=True)

    # 1) 拷文件
    n_files = 0
    for f in INCLUDE_FILES:
        src = os.path.join(ROOT, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(STAGE, f))
            n_files += 1
    for d in INCLUDE_DIRS:
        src = os.path.join(ROOT, d)
        if not os.path.isdir(src):
            continue
        for cur, dirs, files in os.walk(src):
            dirs[:] = [x for x in dirs if not should_skip(x)]
            rel = os.path.relpath(cur, ROOT)
            os.makedirs(os.path.join(STAGE, rel), exist_ok=True)
            for fn in files:
                if should_skip(fn):
                    continue
                shutil.copy2(os.path.join(cur, fn), os.path.join(STAGE, rel, fn))
                n_files += 1

    # 2) 使用说明
    # 用 utf-8-sig 写（带 BOM）——否则老版 Windows 记事本打开会乱码
    with open(os.path.join(STAGE, "使用说明.txt"), "w", encoding="utf-8-sig") as fh:
        fh.write(README)

    # 3) 打 zip（UTF-8 文件名）
    os.makedirs(DIST, exist_ok=True)
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for cur, dirs, files in os.walk(STAGE):
            for fn in files:
                full = os.path.join(cur, fn)
                z.write(full, os.path.relpath(full, DIST))

    size = os.path.getsize(ZIP_PATH)
    print(f"文件数：{n_files + 1}")
    print(f"产出：{ZIP_PATH}")
    print(f"大小：{size/1024/1024:.1f} MB")
    return ZIP_PATH


if __name__ == "__main__":
    main()
