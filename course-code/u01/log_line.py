# log_line.py —— 拆开、取字段、换格式、再拼回去
line = "2026-10-26 09:15:33 GET /lessons/29.html 200 4213"

parts = line.split(" ")                 # 空格分隔，正好 6 段
print("段数  ", len(parts))
print("原始  ", parts)

date, clock, method, path, status, size = parts       # 解包，顺序必须对上
print(f"日期  {date} {clock}")
print(f"请求  {method} {path}")

pure = path.split("?")[0]               # 去掉查询串；没有 ? 时只有一段
print("纯路径", pure)
print("文件名", pure.removeprefix("/lessons/"))

print("CSV   ", ",".join([date, method, pure, status]))

kb = int(size) / 1024                   # size 现在是字符串，必须先转 int
print(f"大小  {kb:.1f} KB")
print("成功？", status.startswith("2"))
