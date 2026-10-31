# read_ways.py —— 四种读取文件的方式

filename = "读取测试.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write("小明\n小红\n小刚\n")# 注意最后一行没有 \n

# ① read()：全部读成一个字符串
with open(filename, "r", encoding="utf-8") as f:
    content = f.read()
print("① read():")
print(f"   类型={type(content).__name__} 内容={content!r}")

# ② readline()：一次读一行
print("\n② readline():")
with open(filename, "r", encoding="utf-8") as f:
    print(f"   第1次={f.readline()!r}")
    print(f"   第2次={f.readline()!r}")
    print(f"   第3次={f.readline()!r}")     # 最后一行的 \n 就是 \n

# ③ readlines()：读成列表
print("\n③ readlines():")
with open(filename, "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"   类型={type(lines).__name__} 内容={lines}")

# ④ for 循环逐行读（推荐方式，能处理超大文件）
print("\n④ for 逐行读:")
with open(filename, "r", encoding="utf-8") as f:
    for line in f:
        print(f"   读到: {line.strip()}")   # strip() 去掉首尾空白和换行

# readline() 的换行符细节
print("\n--- 换行符的细节 ---")
with open(filename, "r", encoding="utf-8") as f:
    for line in f:
        print(f"   {line!r}  -> strip 后 {line.strip()!r}")

# 清理
import os
for name in [filename]:
    if os.path.exists(name):
        os.remove(name)
        print(f"已清理临时文件：{name}")
