# copy_semantics.py —— Python 列表的"引用"语义（重要）

import copy

# 1）直接赋值 = 给同一个列表贴第二张标签，不是复制
original = ["苹果", "香蕉"]
alias = original
alias.append("橙子")

print("original：", original)     # ['苹果', '香蕉', '橙子']  ← 也变了！
print("alias：", alias)           # ['苹果', '香蕉', '橙子']
print("是不是同一个对象：", original is alias)   # True

# 2）正确的浅拷贝：copy.copy() 或 original[:]
shallow = original[:]# 外层列表是新对象
shallow.append("葡萄")
print("original：", original)     # ['苹果', '香蕉', '橙子']  ← 没变，好
print("shallow：", shallow)       # ['苹果', '香蕉', '橙子', '葡萄']

# 3）嵌套列表时，浅拷贝只保护外层！
nested = [["a", "b"], ["c", "d"]]
outer = nested[:]# 浅拷贝
outer[0].append("X")             # 修改的是内层那个列表
print("nested：", nested)         # [['a', 'b', 'X'], ['c', 'd']]  ← 内层被改了！

# 4）完全独立的副本需要 deepcopy
deep = copy.deepcopy(nested)
deep[0].append("Y")
print("nested：", nested)         # [['a', 'b', 'X'], ['c', 'd']]  ← 完全没变
print("deep：", deep)             # [['a', 'b', 'X', 'Y'], ['c', 'd']]
