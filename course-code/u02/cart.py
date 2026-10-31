# cart.py —— 购物车的增删改

cart = ["牛奶", "面包", "鸡蛋"]
print("初始：", cart)

# 在索引 1 处插入"苹果"，原来索引 1 之后的元素自动后移
cart.insert(1, "苹果")
print("insert 后：", cart)      # ['牛奶', '苹果', '面包', '鸡蛋']

# 末尾追加
cart.append("大米")
print("append 后：", cart)      # ['牛奶', '苹果', '面包', '鸡蛋', '大米']

# 按"值"删除："面包"
cart.remove("面包")
print("remove 后：", cart)      # ['牛奶', '苹果', '鸡蛋', '大米']

# 弹出第一个元素，并接住返回值
first_item = cart.pop(0)
print("第一个商品：", first_item)                # 牛奶
print("剩余商品：", cart)                # ['苹果', '鸡蛋', '大米']
