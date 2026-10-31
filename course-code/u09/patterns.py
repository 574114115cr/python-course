# patterns.py —— 三个最常用的异常处理模式

# ===== 模式1：输入重试循环 =====
print("=== 模式1：输入重试 ===")


def read_number(prompt, max_attempts=3):
    """读取一个有效数字，最多尝试 max_attempts 次。"""
    for attempt in range(1, max_attempts + 1):
        raw = input(f"{prompt}（第 {attempt}/{max_attempts} 次）：")
        try:
            return float(raw)
        except ValueError:
            print(f"  '{raw}' 不是有效数字")
    raise ValueError("尝试次数用尽，仍然没有有效输入")


# 演示：不需要真的输入，用固定值模拟
def demo_retry():
    inputs = ["abc", "12.5"]
    for raw in inputs:
        try:
            value = float(raw)
            print(f"  成功：{value}")
            return value
        except ValueError:
            print(f"  '{raw}' 无效，重试")


demo_retry()

# ===== 模式2：安全地执行可能失败的操作 =====
print("\n=== 模式2：安全操作 ===")


def safe_divide(a, b):
    """安全除法，任何问题都返回一个可读的结果。"""
    try:
        return float(a) / float(b)
    except (ValueError, ZeroDivisionError) as error:
        return f"无法计算：{error}"


print(safe_divide(10, 2))
print(safe_divide(10, 0))
# 注意 (ValueError, ZeroDivisionError) 用括号包起来，表示"任意一种"

# ===== 模式3：文件读取的标准健壮写法 =====
print("\n=== 模式3：健壮的文件读取 ===")


def read_file_lines(filename, encoding="utf-8"):
    """安全读取文件，返回行列表，出错时返回 None。"""
    try:
        with open(filename, "r", encoding=encoding) as f:
            return [line.rstrip("\n") for line in f]
    except FileNotFoundError:
        print(f"  文件 {filename} 不存在")
        return None
    except UnicodeDecodeError:
        print(f"  文件 {filename} 编码不匹配，试试换个 encoding")
        return None


# 先创建一个文件测试
with open("健壮性测试.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n第二行\n第三行")

print("读取结果：", read_file_lines("健壮性测试.txt"))
print("读取不存在的文件：", read_file_lines("没有这个文件.txt"))

import os
os.remove("健壮性测试.txt")
