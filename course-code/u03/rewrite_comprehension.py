# rewrite_comprehension.py —— 把传统循环改写成列表推导式

# ===== A =====
# 原写法：result = []
#       for i in range(10):
#           result.append(i * 2)
result = [i * 2 for i in range(10)]
print("A:", result)     # [0, 2, 4, ..., 18]

# ===== B =====
# 原写法：names = []
#       for w in ["apple", "banana", "cherry"]:
#           names.append(w.upper())
words = ["apple", "banana", "cherry"]
names = [w.upper() for w in words]
print("B:", names)      # ['APPLE', 'BANANA', 'CHERRY']

# ===== C =====
# 原写法：evens = []
#       for n in range(1, 21):
#           if n % 2 == 0:
#               evens.append(n)
evens = [n for n in range(1, 21) if n % 2 == 0]
print("C:", evens)      # [2, 4, 6, ..., 20]

# ===== D =====
# 原写法：short = []
#       for w in ["hi", "hello", "ok", "python"]:
#           if len(w) < 3:
#               short.append(w)
all_words = ["hi", "hello", "ok", "python"]
short = [w for w in all_words if len(w) < 3]
print("D:", short)      # ['hi', 'ok']
