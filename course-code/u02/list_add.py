# list_add.py —— 三种添加方式

cars = ["小红帽", "凯迪拉克"]
print("初始：", cars)

# 1）append()：在列表末尾追加一个元素（最常用）
cars.append("雷克萨斯")
print("append 后：", cars)          # ['小红帽', '凯迪拉克', '雷克萨斯']

# 2）insert()：在指定索引位置插入，后面的元素自动后移
cars.insert(1, "宝马")             # 在索引 1（即"小红帽"和"凯迪拉克"之间）插入
print("insert 后：", cars)          # ['小红帽', '宝马', '凯迪拉克', '雷克萨斯']

# 3）用 + 拼接两个列表（会产生一个新列表）
more = ["本田", "福特"]
combined = cars + more
print("拼接后：", combined)
print("原列表没变：", cars)          # + 不修改原列表

# append 和 insert 的返回值都是 None，所以不能写 x = cars.append(...) 后期待 x 有值
result = cars.append("沃尔沃")
print("append 的返回值：", result)   # None
print("但列表确实变了：", len(cars)) # 5

# 常见错误：append 只能一次加一个
# cars.append("A", "B")   # TypeError: append() takes exactly one argument
# 想一次加多个，用 extend
cars.extend(["奥迪", "英菲尼迪"])
print("extend 后：", cars)
