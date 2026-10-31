# exceptions_demo.py —— try/except/else/finally

# ===== 1）最基础的 try/except =====
print("=== 1. 基础异常处理 ===")
try:
    number = int("abc")
except ValueError:
    print("捕获到 ValueError：'abc' 不是有效整数")

# ===== 2）多种异常分别处理 =====
print("\n=== 2. 多种异常 ===")
def divide(a, b):
    try:
        return float(a) / float(b)
    except ValueError:
        return "错误：必须输入数字"
    except ZeroDivisionError:
        return "错误：除数不能为 0"


print(divide(10, 2))# 5.0
print(divide("x", 2))      # 错误：必须输入数字
print(divide(10, 0))       # 错误：除数不能为 0

# ===== 3）捕获异常对象，读取错误信息 =====
print("\n=== 3. 用 as 获取异常信息 ===")
try:
    int("abc")
except ValueError as error:
    print(f"异常信息：{error}")

try:
    with open("不存在的文件.txt", "r", encoding="utf-8") as f:
        f.read()
except FileNotFoundError as error:
    print(f"文件错误信息：{error}")

# ===== 4）else：没出错才执行 =====
print("\n=== 4. else 的作用 ===")
for text in ["100", "abc"]:
    try:
        value = int(text)
    except ValueError:
        print(f"  {text!r} -> 转换失败")
    else:
        # 只有 try 块完全成功才会走这里
        print(f"  {text!r} -> 转换成功：{value * 2}")

# ===== 5）finally：无论如何都执行 =====
print("\n=== 5. finally 的作用 ===")


def process(raw):
    """演示 finally：无论成功失败都会打印收尾日志。"""
    try:
        index = int(raw)
        return ["甲", "乙", "丙"][index]     # 成功：返回对应元素
    except ValueError:
        return "输入无效"
    except IndexError:
        return "下标超出范围"
    finally:
        # 无论成功失败都会执行，常用于释放资源、记录日志
        print(f"  finally: 正在处理 {raw!r}")


print("成功的情况：", process("1"))# 乙
print("输入无效：", process("abc"))
print("下标越界：", process("99"))   # 返回友好提示而不是崩溃

# ===== 6）一个常见错误：裸 except =====
print("\n=== 6. 为什么不要用裸 except ===")
# INTENTIONALLY-BROKEN 演示：裸 except 会捕获一切，包括 Ctrl+C
# try:
#     while True:
#         print("按 Ctrl+C 应该能停下来")
# except:
#     pass
# 现象：Ctrl+C 完全无效，必须用任务管理器强杀。
# 原因：KeyboardInterrupt 也是一个异常类，被裸 except 吞掉了。

# 正确做法：明确指定异常类型
try:
    value = int("abc")
except ValueError:
    print("正确做法：只捕获 ValueError，Ctrl+C 仍然有效")

# ===== 7）主动抛出异常 =====
print("\n=== 7）主动抛出异常 ===")
def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("取款金额必须大于 0")
    if amount > balance:
        raise ValueError(f"余额不足，只有 {balance} 元")
    return balance - amount


print("正常取款：", withdraw(1000, 200))
try:
    withdraw(1000, 5000)
except ValueError as error:
    print("取款失败：", error)
