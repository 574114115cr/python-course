"""把 course-fluent/cases/*.txt 的「综合案例」注入对应单元讲义。

格式：@@<单元号>|<案例标题>  正文 markdown
注入位置：`## 单元验收` 之前；已存在 `## 综合案例：` 则先剥掉旧段。
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "course-fluent")
CASES = os.path.join(SRC, "cases")
MARK = "## 综合案例："


def parse(path):
    txt = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    parts = re.split(r"(?m)^@@(\d+)\|(.+)$", txt)
    out = {}
    for i in range(1, len(parts), 3):
        out[int(parts[i])] = (parts[i + 1].strip(), parts[i + 2].strip("\n").strip())
    return out


def main():
    data = {}
    for fn in sorted(os.listdir(CASES)):
        if fn.endswith(".txt"):
            data.update(parse(os.path.join(CASES, fn)))
    if sorted(data) != list(range(1, 13)):
        raise SystemExit(f"案例应为 12 个单元，实际 {sorted(data)}")

    total = 0
    for no in range(1, 13):
        fn = next(f for f in sorted(os.listdir(SRC))
                  if f.startswith(f"{no:02d}-") and f.endswith(".md"))
        path = os.path.join(SRC, fn)
        md = open(path, encoding="utf-8").read().replace("\r\n", "\n")

        i = md.find(MARK)
        if i != -1:
            j = md.find("\n## ", i + len(MARK))
            md = md[:i].rstrip("\n") + "\n" + (md[j + 1:] if j != -1 else "")

        title, body = data[no]
        block = f"{MARK}{title}\n\n{body}\n\n"
        if "## 单元验收" in md:
            md = md.replace("## 单元验收", block + "## 单元验收", 1)
        else:
            md = md.rstrip("\n") + "\n\n" + block
        total += len(body)
        open(path, "w", encoding="utf-8").write(md)

    print(f"注入 12 个案例，新增正文 {total} 字")


if __name__ == "__main__":
    main()
