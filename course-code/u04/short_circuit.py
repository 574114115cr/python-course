# short_circuit.py —— 短路求值的安全价值

data = [10, 20, 30]

# ===== 安全版：先问长度，再问内容 =====
if len(data) > 0 and data[0] == 10:
    print("安全版：列表非空，且第一个数是 10")
else:
    print("安全版：条件不满足")

# 换成空列表再试一次
empty = []

# ===== 安全版在空列表上依然安全 =====
if len(empty) > 0 and empty[0] == 10:
    print("空列表：不应该走到这里")
else:
    print("安全版处理空列表：条件不满足，程序继续正常运行")

# ===== 危险版：先访问元素 =====
# 下面这行如果真的运行，会崩溃（IndexError: list index out of range）
# if empty[0] == 10 and len(empty) > 0:
#     print("危险版：条件满足")

# 解释为什么崩溃：
# Python 执行 and 时是从左往右的。它必须先算出左边 empty[0] == 10 的结果，
# 但 empty 是空列表，取第0 个元素直接 IndexError，
# 右边的 len(empty) > 0 根本没机会被计算。

# ===== 更简洁的安全写法：利用空列表本身为假 =====
# Python 认为空列表、0、空字符串、None 都是"假"，所以可以直接判断
if empty and empty[0] == 10:
    print("第一个数是 10")
else:
    print("列表为空，无需检查（短路了，没访问 empty[0]）")
