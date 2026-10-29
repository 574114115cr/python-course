# python-course

Python 学习课程包：纯静态站点 + PWA + Capacitor 安卓壳。目前包含两门课，首页可互相切换。

## 两门课

| 课程 | 教材 | 规模 | 入口 |
|---|---|---|---|
| Python 入门课 | 《Python 编程：从入门到实践（第 3 版）》 | 22 单元 / 111 节 / 120 题 / 2 关卡 | `index.html` |
| 流畅的 Python 精读课 | 《流畅的 Python（第 2 版）》24 章 | 12 单元 / 48 节 / 12 案例 / 48 题 / 2 关卡 | `fluent/index.html` |

两门课共用同一套视觉与交互：单元讲义 → 课节页 → 题库 → 关卡 → 大纲课件；进度全部写 localStorage，
键前缀分别为 `py-` / `lesson-`（入门课）与 `fl-`（进阶课），互不干扰。

## 目录

```
course/            入门课讲义源（22 份 Markdown）
exercises/         入门课题库源
web/               入门课产物（单元页、课节页、题库、课件）
fluent/            进阶课产物（index + web/）
course-fluent/     进阶课讲义源（12 份 Markdown）、bank.json、bookmap.json、
                   deepen/（48 条延伸）、cases/（12 个案例）
tools/             构建与验证脚本
dist/              便携版 zip
```

## 构建

必须使用装了 markdown / pygments 的解释器：

```
C:/Users/57411/.workbuddy/binaries/python/envs/default/Scripts/python.exe
```

入门课（改动 `course/` 或页面模板后全量重建）：

```
build_bank → build_gates → build_search_index → build_lectures → build_lessons
→ build_ppt_html → build_ppt_hub → audit_all
```

进阶课（改动 `course-fluent/` 或 `tools/build_fluent.py` 后）：

```
python tools/make_fluent_bank.py     # 仅在改题库源时运行
python tools/build_fluent.py
node tools/verify_fluent.mjs         # 390px 溢出 + 本地链接 404
```

便携包（会同时打入两门课）：

```
python tools/build_portable.py       # → dist/Python课程包-便携版.zip
```

## 本地预览

整站页面跨目录（`lessons/` → `web/` → `ppt/`），内置预览面板只解析同一目录，直接双击或单页预览会出现 404。

```
python tools/serve.py                # http://127.0.0.1:8090
```

## 说明

- 进阶课每节课的结构固定：机制精讲 → 惯用法 → 实战改造 → 坑与验收；每单元 4 节，共 48 节。
- 每节末尾有「延伸」小节（补原书同节一句话带过的易踩点）与「教材对照」框（标明章节范围，声明本节自足）。
- 每单元末尾有「综合案例」：40–60 行可运行项目 + 设计取舍 + 下一步，对应原书靠长案例教设计的部分。
- 覆盖与自足性见 `fluent/web/coverage.html`（24 章逐章对照 + 不替代清单），术语索引见 `fluent/web/terms.html`。
- 进阶课讲义按 Python 3.10+ 语法编写，3.11+ 特性（`TaskGroup`、`asyncio.timeout`、`ExceptionGroup`）在正文单独标注。
- 课节页末尾有「原书对照」：标注对应章节小节，并列出课上没有展开的细节。
- 课件为纯 HTML：18 页大纲 + 12 套逐节课件（每套 10 页；键盘 ← →、触摸滑动、`#sN` 深链），不依赖 pptx。
