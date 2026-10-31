# log_extract.py —— 从一坨日志里挑出「该拿去搜的那一行」
def last_error(log_text):
    """返回日志里最后一条 traceback 的**最后一行**——那才是该拿去搜的一行。

    不能简单找「含 Error 的最后一行」：日志里常有
    `Internal Server Error: /topics/1/` 这种 HTTP 状态行，它只是说"挂了"，
    没说为什么挂。真正的原因在 Traceback 块的**最后一行**。
    """
    lines = log_text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("Traceback"):
            start = i                                  # 取最后一个 Traceback 块
    if start is None:                                  # 没有 traceback 就退回模糊找
        for ln in reversed(lines):
            if "Error" in ln or "Exception" in ln:
                return ln.strip()
        return None
    # 块内逐行：跳过 File "..." 栈帧行，遇到 [web] 这类新日志段就停，
    # 剩下的最后一行就是异常行（注意它可能是顶格的，不能靠缩进来判断）
    hit = None
    for j in range(start + 1, len(lines)):
        s = lines[j].strip()
        if not s:
            continue
        if s.startswith("["):                          # 新的日志段落，traceback 结束
            break
        if s.startswith('File "'):                     # 栈帧行，不是原因
            continue
        hit = s
    return hit


def search_query(err_line):
    """把报错行变成搜索词：去掉自己的路径和变量名，只留异常类型 + 关键信息。"""
    import re
    line = err_line.split(": ", 1)[-1] if ": " in err_line else err_line
    line = re.sub(r"File \"[^\"]+\"", 'File "..."', line)   # 抹掉本机路径
    line = re.sub(r"'[^']*'", "'...'", line)                # 抹掉具体的值
    return line.strip()


SAMPLE = """
[web] Starting gunicorn 21.2.0
[web] Listening at: http://0.0.0.0:8888
Internal Server Error: /topics/1/
Traceback (most recent call last):
  File "/app/learning_logs/views.py", line 42, in topic
    entry = topic.entry_set.get(id=entry_id)
  File "/app/.venv/lib/python3.12/site-packages/django/db/models/query.py", line 637, in get
    raise self.model.DoesNotExist(
learning_logs.models.Entry.DoesNotExist: Entry matching query does not exist.
[web] 10.0.3.7 - - "GET /topics/1/ HTTP/1.1" 500
"""

err = last_error(SAMPLE)
print("报错行：", err)
print("该搜的是：", search_query(err))
print()
print("★ 看清楚：日志里唯一的线索是最后那行 DoesNotExist，")
print("  而原因在它上面两行——get() 没找到匹配的记录，要换成 get_object_or_404 或先 exists() 判断。")
