# notepad.py —— 记事本：追加与读取

NOTES_FILE = "notes.txt"


def add_note(text):
    """用 'a' 模式追加一行，不会覆盖原有内容。"""
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")      # write 不会自动换行，必须自己加 \n


def read_all_notes():
    """读取全部内容。"""
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return f.read()


def count_lines():
    """统计行数。"""
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        # 方式A：读成列表再数
        lines = f.readlines()
        return len(lines)


def read_all_with_loop():
    """用 for 循环逐行读，也能数行数（大文件推荐）。"""
    count = 0
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            count += 1
    return count


# ===== 测试 =====
# 先清空文件
with open(NOTES_FILE, "w", encoding="utf-8") as f:
    f.write("")                  # w 模式清空文件

add_note("第一条：学习文件读写")
add_note("第二条：理解 with 语句")
add_note("第三条：掌握 try/except")

print("--- 全部内容 ---")
print(read_all_notes())
print(f"总行数：{count_lines()}（readlines 方式）")
print(f"总行数：{read_all_with_loop()}（for 循环方式）")

# ===== r / w / a 三种模式对比实验 =====
print("\n=== 模式对比实验 ===")

add_note("第四条：模式对比")

# 错误示范：想追加却用了 w，原数据全没了
# add_note 内部用的是 a，这里手动用 w 演示危害
with open(NOTES_FILE, "r", encoding="utf-8") as f:
    before = len(f.readlines())
print(f"用 w 之前：{before} 行")

with open(NOTES_FILE, "w", encoding="utf-8") as f:
    f.write("只有这一行\n")      # w 模式清空并重写！

with open(NOTES_FILE, "r", encoding="utf-8") as f:
    after = len(f.readlines())
print(f"用 w 之后：{after} 行")

# 结论：
# 'r' 读取，文件不存在会报 FileNotFoundError
# 'w' 写入，文件不存在则创建，存在则【清空】
# 'a' 追加，文件不存在则创建，存在则在末尾添加
# 所以"只想追加内容"时必须用 'a'，用 'w' 会无声地丢失原有数据
