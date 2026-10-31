# slicing.py —— 切片 list[start:stop:step]

letters = ["a", "b", "c", "d", "e", "f"]
print("原列表：", letters)

print("letters[:]      ", letters[:])       # 全部
print("letters[2:]     ", letters[2:])      # ['c','d','e','f']
print("letters[:3]     ", letters[:3])      # ['a','b','c']
print("letters[1:4]    ", letters[1:4])     # ['b','c','d']
print("letters[::2]    ", letters[::2])     # ['a','c','e']
print("letters[::-1]   ", letters[::-1])    # 反转
print("letters[-2:]    ", letters[-2:])     # ['e','f']
print("letters[-4:-1]  ", letters[-4:-1])   # ['c','d','e']

# 左闭右开：切片的秘密
# len(a[b:c]) == c - b，用这个公式快速预测结果
print("letters[2:5] 的长度：", len(letters[2:5]))    # 3 = 5 - 2

# 切片对字符串同样有效
url = "https://example.com/page"
print("协议：", url[:8])                # https://
print("主机名：", url[8:19])             # example.com
print("去掉末尾斜杠：", url.rstrip("/"))

# 切片是浅拷贝：外层是新的，内层元素还是同一批
matrix = [[1, 2], [3, 4]]
copy = matrix[:]
copy[0].append(99)
print("原matrix：", matrix)          # [[1, 2, 99], [3, 4]]  内层被影响！
print("copy：", copy)

# 深拷贝要显式 import copy
import copy
deep = copy.deepcopy(matrix)
deep[0].append(77)
print("深拷贝后原 matrix：", matrix)  # [[1, 2, 99], [3, 4]]  完全没变
