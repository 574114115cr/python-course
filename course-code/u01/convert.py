# convert.py —— 四种类型之间的转换

# str 转 int：常见且安全（前提是字符串确实是整数）
s = "18"
print(int(s) + 1)              # 19

# str 转 float
print(float("3.9") + 0.1)      # 4.0

# 注意：float 转回 int 会丢失小数部分（不是报错，是截断）
print(int(3.9))                # 3   直接丢弃小数
print(round(3.9))              # 4   四舍五入
print(round(2.5))              # 2   注意：Python 的 round 用"银行家舍入"
print(round(3.456, 2))         # 3.46  保留两位小数

# 数字转 str
print(str(100) + "元")          # 100元

# bool 转换：空/零为 False，其余为 True
print(bool(0))# False
print(bool(0.0))     # False
print(bool(""))      # False
print(bool("0"))# True  ← 字符串 "0" 非空，所以是 True！
print(bool(5))       # True
print(bool(-1))      # True  负数也是 True

# 转换失败会报 ValueError，下面两行会崩
# print(int("abc"))          # ValueError
# print(int("3.9"))          # ValueError：带小数点的字符串不能直接转 int
# 想让 "3.9" 变 3，必须分两步
print(int(float("3.9")))     # 3先转小数，再转整数
