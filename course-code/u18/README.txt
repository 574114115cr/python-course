单元 18 · 18-单元18-Django入门.md
============================================================

先从这个开始：learning_logs/models.py

本目录的 .py 文件全部抽自讲义，可直接用 Python 运行。
snippets/ 里是「片段」——属于某个文件的一部分，不能单独运行。
.v2/.v3 是同一文件的其它版本（教材练习的参考答案），按需查看。

  fk_simulation.py                   ← 示例 1：用纯 Python 看懂外键和级联删除
  request_chain_simulation.py        ← 示例 2：用纯 Python 模拟「URL → 视图 → 模板」请求链路
  template_inheritance_simulation.py ← 示例 3：用纯 Python 模拟模板继承
  learning_logs/models.py            ← 示例 4：`learning_logs/models.py`（项目文件，完整版）
  learning_logs/admin.py             ← 示例 5：`learning_logs/admin.py` 与 Django shell 查数据
  learning_logs/urls.py              ← 示例 6：两个 `urls.py`（项目文件，完整版）
  ll_project/urls.py                 ← 示例 6：两个 `urls.py`（项目文件，完整版）
  learning_logs/views.py             ← 示例 7：`learning_logs/views.py`（项目文件，完整版）
  learning_logs/models.v2.py         ← 参考答案 18-2
  pizzas/models.py                   ← 参考答案 18-3
  pizzas/admin.py                    ← 参考答案 18-3
  mini_template.py                   ← 参考答案 18-4
  learning_logs/urls.v2.py           ← 参考答案 18-5
  learning_logs/views.v2.py          ← 参考答案 18-5

片段（需并入上面的文件，不能单独跑）：
  settings.py                        ← 2.2 Django 的三个层次：项目、应用程序、MVT ★

运行：在终端执行  python 文件名.py
缺库时先装：python -m pip install 包名
