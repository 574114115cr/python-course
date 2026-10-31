# list_remove.py —— remove / pop / del / clear

cars = ["小红帽", "宝马", "凯迪拉克", "雷克萨斯", "保时捷"]
print("初始：", cars)

# 1）remove()：按"值"删除，只能删掉第一个匹配的
cars.remove("宝马")
print("remove 后：", cars)         # ['小红帽', '凯迪拉克', '雷克萨斯', '保时捷']

# 删不存在的值会报 ValueError
# cars.remove("菲亚特")           # ValueError: list.remove(x): x not in list

# 2）pop()：按"位置"弹出，并返回被弹出的元素
last = cars.pop()# 弹出最后一个
print("pop 出来的：", last)         # 保时捷
print("pop 后：", cars)             # ['小红帽', '凯迪拉克', '雷克萨斯']

# pop 也可以指定位置
first_car = cars.pop(0)            # 弹出第0 个
print("pop(0) 出来的：", first_car)  # 小红帽
print("现在：", cars)               # ['凯迪拉克', '雷克萨斯']

# 3）del：按位置删除，但不返回值
del cars[1]
print("del 后：", cars)             # ['凯迪拉克']

# 4）remove 和 pop 的本质区别
numbers = [10, 20, 30]
# numbers.remove(20)   # 删掉"值为 20 的元素"
# numbers.pop(1)       # 删掉"第 1 个位置的元素"（这里恰好也是 20）

# 5）清空列表
nums = [1, 2, 3]
nums.clear()
print("clear 后：", nums, "长度", len(nums))   # [] 长度 0
