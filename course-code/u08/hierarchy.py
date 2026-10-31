# hierarchy.py —— 三层继承

class Person:
    """人。"""
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        """打招呼。"""
        print(f"你好，我是{self.name}")

    def birthday(self):
        """过生日。"""
        self.age += 1

    def __str__(self):
        return f"{self.name}，{self.age} 岁"


class Employee(Person):
    """员工 —— 继承 Person。"""
    def __init__(self, name, age, company, salary):
        # 先让父类设置共有的 name 和 age
        super().__init__(name, age)
        self.company = company
        self.salary = salary            # 年薪

    def get_monthly(self):
        """返回月薪。"""
        return self.salary / 12

    def get_daily(self):
        """返回日薪（按 22 个工作日算）。"""
        return self.salary / 12 / 22

    def raise_salary(self, amount):
        """加薪。"""
        self.salary += amount
        return self.salary

    def __str__(self):
        # 用 super() 复用父类的字符串，再追加自己的信息
        return f"{super().__str__()}，在 {self.company} 工作，年薪 {self.salary} 元"


class Manager(Employee):
    """经理 —— 继承 Employee。"""
    def __init__(self, name, age, company, salary, team_size):
        # 调用祖父类的初始化（super() 会自动找对正确的父类）
        super().__init__(name, age, company, salary)
        self.team_size = team_size

    def __str__(self):
        # 复用 Employee 的 __str__，再追加团队信息
        return f"{super().__str__()}，管理 {self.team_size} 人团队"

    def performance_review(self):
        """经理独有的方法。"""
        return f"{self.name} 对 {self.team_size} 名下属进行了考核"


# ===== 测试 =====
print("--- 第一层：Person ---")
p = Person("张三", 30)
print(p)
p.greet()
p.birthday()
print(f"过完生日：{p}")

print("\n--- 第二层：Employee ---")
e = Employee("李四", 28, "腾讯", 240000)
print(e)
e.greet()                     # 继承自 Person
print(f"月薪：{e.get_monthly():.2f} 元")
print(f"日薪：{e.get_daily():.2f} 元")
print(f"加薪 20000 后年薪：{e.raise_salary(20000)}")

print("\n--- 第三层：Manager ---")
m = Manager("王五", 40, "阿里", 600000, 15)
print(m)                       # 用的是 Manager 重写的 __str__
m.greet()                     # 从 Person 一路继承下来
print(f"月薪：{m.get_monthly():.2f} 元")
print(m.performance_review())

print("\n--- super() 的调用链条 ---")
# Manager() -> Employee.__init__() -> Person.__init__()
#所以 m 同时拥有 name/age（Person）和 company/salary（Employee）
# 和 team_size（Manager）的属性
print(f"来自 Person 的属性：{m.name}, {m.age}")
print(f"来自 Employee 的属性：{m.company}, {m.salary}")
print(f"来自 Manager 的属性：{m.team_size}")

print("\n--- 层层向上调用 super().__str__() ---")
print("Person  :", Person("张三", 30))
print("Employee:", Employee("李四", 28, "腾讯", 240000))
print("Manager :", Manager("王五", 40, "阿里", 600000, 15))
