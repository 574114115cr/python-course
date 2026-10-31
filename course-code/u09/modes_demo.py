# modes_demo.py —— r / w / a 三种模式的区别

filename = "模式测试.txt"

# 先创建一个有内容的文件
with open(filename, "w", encoding="utf-8") as f:
    f.write("第一行\n第二行\n第三行\n")

def show(title):
    """读取并显示文件内容。"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        print(f"  {title}: {len(lines)} 行 -> {[l.strip() for l in lines]}")
    except FileNotFoundError:
        print(f"  {title}: 文件不存在")


show("初始状态")

# "a" 追加：保留原有内容
with open(filename, "a", encoding="utf-8") as f:
    f.write("追加的行\n")
show("a 追加后")

# "w" 写入：清空原内容！
with open(filename, "w", encoding="utf-8") as f:
    f.write("全新的内容\n")
show("w 覆盖后")            # 只剩1 行，前面的都没了！

# "r" 读取不存在的文件 -> FileNotFoundError
try:
    with open("根本不存在.txt", "r", encoding="utf-8") as f:
        f.read()
except FileNotFoundError as error:
    print("r 读取不存在的文件：", error)

# "w" 和 "a" 都会在文件不存在时自动创建
with open("新建的文件.txt", "w", encoding="utf-8") as f:
    f.write("用 w 创建的新文件")
with open("新建的文件.txt", "a", encoding="utf-8") as f:
    f.write("\n用 a 追加的内容")

print("新建的文件是否存在于当前目录：是（w 和 a 都能自动创建）")
