单元 10 · 10-单元10-测试代码.md
============================================================

先从这个开始：conftest.py

本目录的 .py 文件全部抽自讲义，可直接用 Python 运行。
snippets/ 里是「片段」——属于某个文件的一部分，不能单独运行。
.v2/.v3 是同一文件的其它版本（教材练习的参考答案），按需查看。

  conftest.py                        ← 2.9 fixture：准备代码只写一遍
  test_00_version.py                 ← 示例 1：安装与验证
  calculator.py                      ← 示例 2：第一个被测模块与测试
  test_calculator.py                 ← 示例 2：第一个被测模块与测试
  test_assertions.py                 ← 示例 3：断言消息与常见断言
  test_bank.py                       ← 示例 4：测试类
  test_parametrize.py                ← 示例 5：参数化测试
  test_fixture.py                    ← 示例 6：测试夹具（简单版）
  text_utils.py                      ← 参考答案 10-1
  test_text_utils.py                 ← 参考答案 10-1
  divider.py                         ← 参考答案 10-2
  test_divider.py                    ← 参考答案 10-2
  book.py                            ← 参考答案 10-3
  test_book.py                       ← 参考答案 10-3
  buggy.py                           ← 参考答案 10-4
  test_buggy.py                      ← 参考答案 10-4
  buggy_fixed.py                     ← 参考答案 10-4
  test_parametrize_demo.py           ← 参考答案 10-5
  cart.py                            ← 参考答案 10-6
  test_cart.py                       ← 参考答案 10-6
  vote_analyzer.py                   ← 参考答案 10-7
  test_vote_analyzer.py              ← 参考答案 10-7
  test_feature.py                    ← 参考答案 10-8
  tip.py                             ← 参考答案 10-8
  test_calc.py                       ← 参考答案 10-8

运行：在终端执行  python 文件名.py
缺库时先装：python -m pip install 包名
