单元 17 · 17-单元17-使用API与Plotly.md
============================================================

先从这个开始：api_basics.py

本目录的 .py 文件全部抽自讲义，可直接用 Python 运行。
snippets/ 里是「片段」——属于某个文件的一部分，不能单独运行。
.v2/.v3 是同一文件的其它版本（教材练习的参考答案），按需查看。

  api_basics.py                      ← 示例 1：认识 API 网址的结构 + 第一次调用
  parse_response.py                  ← 示例 2：处理响应字典——提取平行列表
  rate_limit_guard.py                ← 示例 3：速率限制守门员 + 缓存响应
  bar_chart.py                       ← 示例 4：Plotly 条形图——悬停提示、颜色、可点击链接
  hacker_news.py                     ← 示例 5：Hacker News 两段式调用
  api_pipeline.py                    ← 示例 6：把「请求 → JSON → 取字段」拆成纯函数（api_pipeline.py）
  api_url_parser.py                  ← 参考答案 17-1
  api_watchtower.py                  ← 参考答案 17-2
  clickable_chart.py                 ← 参考答案 17-3
  hn_digest.py                       ← 参考答案 17-4

运行：在终端执行  python 文件名.py
缺库时先装：python -m pip install 包名
