# inheritance.py —— 继承：子类复用父类的属性和方法

class Animal:
    """动物基类：定义所有动物共有的东西。"""
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name}，{self.age} 岁"

    def speak(self):
        """动物都会发声，但发声方式各不相同。"""
        print(f"{self.name} 发出了一声不明的声音")

    def birthday(self):
        """过生日。"""
        self.age += 1
        print(f"{self.name} 生日快乐，现在 {self.age} 岁了")


class Dog(Animal):
    """狗继承动物，自己追加"汪汪"和"fetch"。"""
    def __init__(self, name, age, breed):
        super().__init__(name, age)      # 先让父类设置 name 和 age
        self.breed = breed               # 再设置子类自己的属性

    def speak(self):                     # 重写父类的方法
        print(f"{self.name}（{self.breed}）说：汪汪汪！")

    def fetch(self):                     # 子类独有的方法
        print(f"{self.name} 去捡球了")


class Cat(Animal):
    """猫继承动物。"""
    def __init__(self, name, age, indoor=True):
        super().__init__(name, age)
        self.indoor = indoor

    def speak(self):                     # 重写
        print(f"{self.name} 说：喵~")


# 使用
dog = Dog("旺财", 3, "柴犬")
cat = Cat("咪咪", 2)

print("--- 继承来的属性 ---")
print(dog.name, dog.age, dog.breed)     # name/age 来自父类，breed 来自子类
print(cat.name, cat.age, cat.indoor)

print("\n--- 重写的方法 ---")
dog.speak()
cat.speak()

print("\n--- 继承来的方法 ---")
dog.birthday()
print(str(dog))                        # 用的是父类的 __str__

print("\n--- 子类独有的方法 ---")
dog.fetch()
# cat.fetch()                          # AttributeError：猫没有这个方法

print("\n--- super() 复用父类的 __str__ ---")


class Puppy(Dog):
    """小狗继承狗。"""
    def __str__(self):
        parent = super().__str__()      # 拿到父类生成的字符串
        return f"【幼犬】{parent}"


puppy = Puppy("豆豆", 1, "比熊")
print(puppy)      # 【幼犬】豆豆，1 岁
puppy.speak()     # 继承了狗的 speak
