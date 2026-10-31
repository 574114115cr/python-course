# comparisons.py —— 各种比较的细节

# 数字链式比较
age = 25
if 18 <= age <= 60:
    print("适龄")
if 10 <= age < 20:
    print("少年")
else:
    print("不是少年")

# 字符串按编码逐个比较，等价于字典序
print("apple" < "banana")        # True
print("apple" > "Apple")         # True（小写 a 的编码比大写 A 大）
print("abc" < "abd")             # True（逐位比，c < d）

# 链式比较字符串：判断是否是小写字母
letter = "k"
if "a" <= letter <= "z":
    print(f"{letter} 是小写英文字母")

# 判断是否全是大写
upper_word = "HELLO"
if upper_word.isupper():
    print(f"{upper_word} 全是大写")

# 注意：列表不能做大小比较
# if [1, 2] > [1, 3]:     # TypeError: '>' not supported between 'list' and 'list'
# 但可以判断相等
print([1, 2] == [1, 2])          # True
print([1, 2] is [1, 2])          # False，不同对象

# 元组可以比较（逐元素比）
print((1, 2) < (1, 3))           # True
