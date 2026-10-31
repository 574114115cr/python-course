# list_modify.py —— 列表元素可以直接赋值修改

cars = ["小红帽", "二手柯尼塞格", "凯迪拉克"]
print("修改前：", cars)

# 直接给某个索引赋值 —— 这是列表"可变"的标志
cars[0] = "特斯拉"
print("修改第 0 个：", cars)      # ['特斯拉', '二手柯尼塞格', '凯迪拉克']

cars[-1] = "保时捷"
print("修改最后一个：", cars)      # ['特斯拉', '二手柯尼塞格', '保时捷']

# 对比字符串：字符串不能这样改
name = "tom"
# name[0] = "T"  # TypeError: 'str' object does not support item assignment
# 字符串必须"生成新的再赋回"
name = "T" + name[1:]
print("字符串的替代做法：", name)   # Tom

# 注意：直接把一个字符串塞进列表是可以的
mixed = ["hello", 18, 1.75, True]
print(mixed)
print(type(mixed[1]))    # <class 'int'> 列表可以装不同类型
