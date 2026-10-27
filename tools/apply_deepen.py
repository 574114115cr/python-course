"""把 course-fluent/deepen/*.txt 的「延伸」小节注入讲义源文件。

格式（每个文件多节）：
    @@12|小节标题
    正文 markdown（可含代码围栏）
    @@13|小节标题
    ...

注入位置：该课节 `### 关键点` 之前（没有就追加到该节末尾）。
已存在同名 `### 延伸：` 的课节会先剥掉旧段再写入，保证可重复执行。
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "course-fluent")
DEEP = os.path.join(SRC, "deepen")
MARK = "### 延伸："


def parse(path):
    txt = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    blocks = re.split(r"(?m)^@@(\d+)\|(.+)$", txt)
    # blocks[0] 是头部注释，之后每 3 项一组：n, title, body
    out = {}
    for i in range(1, len(blocks), 3):
        n = int(blocks[i])
        title = blocks[i + 1].strip()
        body = blocks[i + 2].strip("\n").strip()
        out[n] = (title, body)
    return out


def strip_old(section):
    i = section.find(MARK)
    if i == -1:
        return section
    j = section.find("\n### ", i + len(MARK))
    if j == -1:
        return section[:i].rstrip("\n") + "\n"
    return section[:i].rstrip("\n") + "\n" + section[j:]


def main():
    data = {}
    for fn in sorted(os.listdir(DEEP)):
        if fn.endswith(".txt"):
            data.update(parse(os.path.join(DEEP, fn)))
    if len(data) != 48:
        raise SystemExit(f"延伸条目应为 48 条，实际 {len(data)} 条")
    missing = [n for n in range(1, 49) if n not in data]
    if missing:
        raise SystemExit(f"缺少第 {missing} 课")

    total = 0
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(SRC, fn)
        md = open(path, encoding="utf-8").read()
        parts = re.split(r"(?m)^(## )", md)
        # parts: [head, '## ', sec, '## ', sec, ...]
        head = parts[0]
        out = [head]
        for i in range(1, len(parts), 2):
            sec = parts[i + 1]
            m = re.match(r"第\s*(\d+)\s*课", sec)
            if not m:
                out.append("## " + sec)
                continue
            n = int(m.group(1))
            sec = strip_old(sec)
            title, body = data[n]
            block = f"{MARK}{title}\n\n{body}\n\n"
            if "### 关键点" in sec:
                sec = sec.replace("### 关键点", block + "### 关键点", 1)
            else:
                sec = sec.rstrip("\n") + "\n\n" + block
            total += len(body)
            out.append("## " + sec)
        open(path, "w", encoding="utf-8").write("".join(out))

    print(f"注入 {len(data)} 节，新增正文 {total} 字")


if __name__ == "__main__":
    main()
