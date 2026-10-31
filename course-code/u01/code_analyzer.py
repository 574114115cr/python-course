# code_analyzer.py —— 用字符串方法分析一个编号

code = "PY-2024-Basic-01"

# 替换分隔符：把 - 换成 |
print("处理后：", code.replace("-", "|"))

# 统计分隔符个数
print("分隔符个数：", code.count("-"))

# 大写形式
print("大写：", code.upper())

# 倒序形式：切片 [::-1] 表示"从末尾到开头每隔 1 个取一次"
print("倒序：", code[::-1])

# 顺带演示其他常用方法
print("去掉所有短横线：", code.replace("-", ""))   # PY2024Basic01
print("首字符：", code[0])                          # P
print("是否以 PY 开头：", code.startswith("PY"))    # True
print("是否以 01 结尾：", code.endswith("01"))      # True
print("长度：", len(code))# 14
