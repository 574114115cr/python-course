# safe_int.py —— 用 try/except 保护类型转换

def safe_int(text):
    """把字符串安全地转成整数。

    成功返回整数，失败返回 None。
    """
    try:
        return int(text)
    except ValueError:
        # int() 在无法转换时抛出 ValueError
        return None


# 测试各种输入
test_cases = ["123", "abc", "12.5", "", "  42  ", "-17", "1e5"]

print(f"{'输入':<12}{'repr':<12}{'结果':<12}")
print("-" * 36)
for text in test_cases:
    result = safe_int(text)
    print(f"{text:<12}{text!r:<12}{result!r:<12}")

print("\n结果分析：")
print('"123"   -> 123    成功')
print('"  42  " -> 42     成功（int 会自动忽略首尾空白）')
print('"-17"   -> -17    成功（负数也行）')
print('"abc"   -> None   ValueError：不是合法整数')
print('"12.5"  -> None   ValueError：带小数点的字符串不能直接转 int')
print('""      -> None   ValueError：空字符串无法转换')
print('"1e5"   -> None   ValueError：科学计数法要先 float 再 int')

# ===== 对比：如果不用 try/except =====
print("\n=== 不用 try 的后果 ===")
# print(int("abc"))    # ValueError: invalid literal for int() with base 10: 'abc'
# 程序会直接崩溃终止，后面所有代码都不执行
# try/except 的价值：把"崩溃"变成"返回一个可处理的失败标记"

# ===== 进阶：需要区分失败原因时用 else =====
def convert_with_reason(text):
    """成功时同时返回结果和说明，失败时说明原因。"""
    try:
        value = int(text)
    except ValueError as error:
        return None, f"转换失败：{error}"
    else:
        return value, "转换成功"


print("\n=== 用 else 区分成功与失败 ===")
for text in ["88", "abc"]:
    value, message = convert_with_reason(text)
    print(f"  {text!r} -> value={value}, {message}")
