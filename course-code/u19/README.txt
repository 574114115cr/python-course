单元 19 · 19-单元19-用户账户.md
============================================================

先从这个开始：learning_logs/forms.v2.py

本目录的 .py 文件全部抽自讲义，可直接用 Python 运行。
snippets/ 里是「片段」——属于某个文件的一部分，不能单独运行。
.v2/.v3 是同一文件的其它版本（教材练习的参考答案），按需查看。

  learning_logs/forms.py             ← 2.1 表单与 ModelForm：把模型变成表单的捷径
  accounts/urls.py                   ← 2.4 登录、注销、注册三件套
  ll_project/settings.py             ← 2.4 登录、注销、注册三件套
  whitelist_simulation.py            ← 示例 1：用纯 Python 看懂「字段白名单」
  current_user_simulation.py         ← 示例 2：用纯 Python 看懂 `request.user`
  login_required_simulation.py       ← 示例 3：用纯 Python 模拟 `@login_required` 门禁
  data_isolation_simulation.py       ← 示例 4：用纯 Python 看懂数据隔离
  learning_logs/forms.v2.py          ← 示例 5：`learning_logs/forms.py`（项目文件，完整版）
  learning_logs/views.py             ← 示例 6：`learning_logs/views.py`（项目文件，第 19 章完成版）
  accounts/views.py                  ← 示例 7：accounts 应用与项目配置（项目文件，完整版）
  accounts/urls.v2.py                ← 示例 7：accounts 应用与项目配置（项目文件，完整版）
  ll_project/urls.py                 ← 示例 7：accounts 应用与项目配置（项目文件，完整版）
  ll_project/settings.v2.py          ← 示例 7：accounts 应用与项目配置（项目文件，完整版）
  accounts/urls.v3.py                ← 参考答案 19-1
  ll_project/settings.v3.py          ← 参考答案 19-1
  accounts/urls.v4.py                ← 参考答案 19-2
  accounts/views.v2.py               ← 参考答案 19-2
  learning_logs/models.py            ← 参考答案 19-3
  ll_project/settings.v4.py          ← 参考答案 19-3
  isolated_notebook.py               ← 参考答案 19-6

片段（需并入上面的文件，不能单独跑）：
  views.py                           ← 2.2 三段式与数据归属：`commit=False` 的经典手法 ★
  views.py                           ← 2.7 `edit_entry` 的双重保护
  views.py                           ← 参考答案 19-3
  views.py                           ← 参考答案 19-4
  views.py                           ← 参考答案 19-5

运行：在终端执行  python 文件名.py
缺库时先装：python -m pip install 包名
