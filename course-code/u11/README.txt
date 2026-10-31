单元 11 · 11-单元11-总复习与关卡验收.md
============================================================

先从这个开始：main.py

本目录的 .py 文件全部抽自讲义，可直接用 Python 运行。
snippets/ 里是「片段」——属于某个文件的一部分，不能单独运行。
.v2/.v3 是同一文件的其它版本（教材练习的参考答案），按需查看。

  main.py                            ← 2.3 一个完整项目的骨架
  self_check.py                      ← 示例 1：知识自查清单（可运行的版本）
  class_review.py                    ← 示例 2：类 + 继承的完整复习
  file_review.py                     ← 示例 3：文件 + 异常完整复习
  test_review.py                     ← 示例 4：pytest 复习（可直接运行的测试文件）
  ledger.py                          ← 示例 5：一个小而完整的项目（类 + JSON + 异常）
  check_ledger.py                    ← 示例 6：给上面的项目写 6 条断言（不装 pytest 也能跑）
  todo_manager.py                    ← 参考答案 11-2（综合项目 1：待办管理器完整实现）
  score_analyzer.py                  ← 参考答案 11-3（综合项目 2：成绩分析器完整实现）
  test_score_analyzer.py             ← 参考答案 11-3 的测试文件
  text_analyzer.py                   ← 参考答案 11-4（综合项目 3：文本统计工具完整实现）
  test_text_analyzer.py              ← 参考答案 11-4 的测试文件
  vehicle.py                         ← ✅ 验收 2：手写一个含继承的类
  test_vehicle.py                    ← ✅ 验收 3：用 pytest 写 3 条测试并全部通过
  broken_script.py                   ← ✅ 验收 4：修复 IndentationError / NameError
  fixed_script.py                    ← ✅ 验收 4：修复 IndentationError / NameError

运行：在终端执行  python 文件名.py
缺库时先装：python -m pip install 包名
