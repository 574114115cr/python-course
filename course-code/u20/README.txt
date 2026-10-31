单元 20 · 20-单元20-样式与部署.md
============================================================

先从这个开始：ll_project/urls.py

本目录的 .py 文件全部抽自讲义，可直接用 Python 运行。
snippets/ 里是「片段」——属于某个文件的一部分，不能单独运行。
.v2/.v3 是同一文件的其它版本（教材练习的参考答案），按需查看。

  ll_project/urls.py                 ← 2.8 定制错误页面与「继续开发」（对应教材 20.2）
  log_extract.py                     ← 2.9.1 先学会看日志
  deploy_doctor.py                   ← 2.9.2 症状对照表
  config_switcher.py                 ← 示例 1：同一份代码，两个环境（config_switcher.py）
  requirements_tools.py              ← 示例 2：给 requirements.txt 做入职体检（requirements_tools.py）
  host_check.py                      ← 示例 3：400 Bad Request 是怎么来的（host_check.py）
  static_collector.py                ← 示例 4：collectstatic 到底在搬什么（static_collector.py）
  deploy_checklist.py                ← 示例 5：推送到 Platform.sh 之前的最后一遍自查（deploy_checklist.py）
  deploy_gate.py                     ← 示例 6：上线前 8 道闸门 + 静态文件清单（deploy_gate.py）
  env_switch.py                      ← 参考答案 20-4（本地模拟双环境）
  settings_snippet.py                ← 错误 6：新文件忘了 git add，推送后线上缺东西

片段（需并入上面的文件，不能单独跑）：
  settings.py                        ← 2.6 platformshconfig：一份代码怎么知道自己在哪（对应教材 20.2）
  settings.py                        ← 2.9.3 用 WhiteNoise 让 Django 自己发静态文件

运行：在终端执行  python 文件名.py
缺库时先装：python -m pip install 包名
