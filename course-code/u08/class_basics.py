# class_basics.py —— 类的定义与对象创建

class Dog:
    """一只狗。

    属性：name（名字）、age（年龄）
    方法：bark（叫）、birthday（过生日）
    """
    def __init__(self, name, age=0):
        # __init__ 在对象创建时自动执行一次
        self.name = name      # 实例属性：每个对象各有一份
        self.age = age

    def bark(self):
        """让狗叫一声。"""
        print(f"{self.name} 说：汪汪！")

    def birthday(self):
        """年龄加一。"""
        self.age += 1
        print(f"{self.name} 生日快乐，现在 {self.age} 岁了！")


# 创建对象：像调用函数一样，但造出来的是一个"实例"
dog1 = Dog("旺财", 3)
dog2 = Dog("咪咪")# age 用默认值 0

# 访问属性：不用括号
print("dog1 的名字：", dog1.name)
print("dog1 的年龄：", dog1.age)
print("dog2 的年龄：", dog2.age)

# 调用方法：用括号
dog1.bark()
dog2.bark()

# 方法可以修改属性
dog1.birthday()
dog1.birthday()
print("过完两个生日后 dog1 的年龄：", dog1.age)   # 5

# 两个对象的数据互相独立
print("dog2 的年龄没变：", dog2.age)          # 0

# 查看对象类型
print("dog1 的类型：", type(dog1))
print("类型名：", type(dog1).__name__)         # Dog
