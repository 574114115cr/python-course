# dog_class.py —— Dog 类的完整实现

class Dog:
    """一只狗。

    属性：
        name: 名字（字符串）
        age:  年龄（整数），默认 1岁
    """

    def __init__(self, name, age=1):
        """初始化一只狗。"""
        self.name = name
        self.age = age

    def bark(self):
        """让狗叫一声。"""
        print(f"{self.name} 说：汪汪汪！")

    def birthday(self):
        """过生日，年龄加一。"""
        self.age += 1
        print(f"🎂 {self.name} 生日快乐，现在 {self.age} 岁了！")

    def get_info(self):
        """返回包含基本信息的字典。"""
        return {
            "name": self.name,
            "age": self.age,
            "is_adult": self.age >= 3,
        }

    def __str__(self):
        """定义对象转成字符串时的样子。"""
        return f"{self.name} 是一只 {self.age} 岁的狗"


# ===== 测试 =====
dog1 = Dog("旺财", 3)
dog2 = Dog("咪咪")             # age 用默认值 1

print("--- 属性 ---")
print("dog1:", dog1.name, dog1.age)
print("dog2:", dog2.name, dog2.age)

print("\n--- bark 方法 ---")
dog1.bark()
dog2.bark()

print("\n--- birthday 方法 ---")
dog1.birthday()
dog2.birthday()
dog2.birthday()

print("\n--- get_info 方法 ---")
info = dog1.get_info()
print(f"{dog1.name} 的信息：{info}")

print("\n--- __str__ 方法 ---")
print(dog1)
print(dog2)

print("\n--- 遍历所有狗 ---")
dogs = [Dog("豆豆", 1), Dog("球球", 5), Dog("糖糖", 2)]
for dog in dogs:
    print(f"  {dog} 成年了：{dog.get_info()['is_adult']}")
