# file_basics.py —— 文件读写基础（用 with 语句）

# ===== 写文件 =====
filename = "示例文件.txt"

# "w" 模式：文件不存在就新建，存在就清空
with open(filename, "w", encoding="utf-8") as f:
    f.write("你好，Python！\n")
    f.write("这是第二行。\n")
    f.write("这是第三行。\n")

print(f"已写入文件：{filename}")

# 注意：write() 不会自动换行，必须自己写 \n

# ===== 读文件（全部读进来）=====
with open(filename, "r", encoding="utf-8") as f:
    content = f.read()          # 一次性读入整个文件

print("--- 全部内容 ---")
print(content)
print(f"文件里有 {len(content)} 个字符")

# ===== 追加内容 =====
with open(filename, "a", encoding="utf-8") as f:
    f.write("这是追加的第四行。\n")

with open(filename, "r", encoding="utf-8") as f:
    print("--- 追加后的内容 ---")
    print(f.read())

# ===== with 的价值：出块后文件自动关闭 =====
with open(filename, "r", encoding="utf-8") as f:
    first_line = f.readline()

#出了 with 块，f 已经关闭，不能再用了
# print(f.read())     # ValueError: I/O operation on closed file
# 但我们保存下来的变量还在
print("第一行：", repr(first_line))
