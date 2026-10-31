# read_ways.py —— 四种读取方式的关系

FILENAME = "four.txt"

# 创建测试文件
with open(FILENAME, "w", encoding="utf-8") as f:
    f.write("小明\n小红\n小刚\n小丽\n")

# ===== ① read()：返回一个字符串 =====
with open(FILENAME, "r", encoding="utf-8") as f:
    content = f.read()
print(f"① read()      -> 类型 {type(content).__name__}，值 {content!r}")

# ===== ② readline()：每调用一次读一行，返回字符串 =====
with open(FILENAME, "r", encoding="utf-8") as f:
    line1 = f.readline()
    line2 = f.readline()
print(f"② readline() 第一次 -> {line1!r}")
print(f"② readline() 第二次 -> {line2!r}")
print("   注意：每行末尾都带\\n 换行符，需要 strip() 才干净")

# ===== ③ readlines()：返回列表 =====
with open(FILENAME, "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"\n③ readlines() -> 类型 {type(lines).__name__}，值 {lines}")
print(f"   列表长度：{len(lines)}")

# ===== ④ for 循环逐行读（推荐处理大文件）=====
collected = []
with open(FILENAME, "r", encoding="utf-8") as f:
    for line in f:
        collected.append(line)
print(f"\n④ for 循环    -> 收集到 {collected}")
print(f"   与 readlines() 结果相同：{collected == lines}")

# ===== 关系总结 =====
print("\n=== 关系总结 ===")
print("1. read() 返回 str，readlines() 返回 list")
print("2. for line in f 收集起来的结果 == readlines() 的结果")
print("3. read() 把整个文件当成一个大字符串（含 \\n）")
print("4. readline() 每次只前进一行，是'流式'读取")
print("5. 文件大时 read() 可能内存爆，readlines() 也是，for 循环最安全")

# 更安全的逐行处理（不把所有行都存起来）
print("\n=== 逐行处理，不存列表 ===")
count = 0
with open(FILENAME, "r", encoding="utf-8") as f:
    for line in f:
        name = line.strip()          # strip() 去掉换行符
        if name:
            count += 1
            print(f"   第{count} 行：{name}")
# 这种方式不管文件多大，内存里始终只有一行

import os
os.remove(FILENAME)
