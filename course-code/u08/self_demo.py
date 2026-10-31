# self_demo.py —— 理解 self 的本质

class Cat:
    def __init__(self, name):
        self.name = name

    def speak(self):
        # self 就是"我自己"
        print(f"{self.name} 说：喵")

    def compare(self, other):
        """比较两只猫。self 是当前这只，other 是传入的那只。"""
        print(f"self 的名字：{self.name}")
        print(f"other 的名字：{other.name}")


cat1 = Cat("小白")
cat2 = Cat("小黑")

cat1.speak()        # Python 实际执行的是 Cat.speak(cat1)，所以 self=cat1
cat2.speak()        # 这里 self=cat2
cat1.compare(cat2)  # self=cat1，other=cat2

# 手动验证：普通函数 vs 方法
def manual_speak(self):
    print(f"{self.name} 说：喵")


# 直接调用方法的两种写法完全等价
manual_speak(cat1)      # 手动把 cat1 传进去
cat1.speak()            # Python 自动帮你传了 cat1

print("两种调用方式结果相同")

# 演示：同一个类造多个对象，self 各不相同
cats = [Cat("咪咪1"), Cat("咪咪2"), Cat("咪咪3")]
print("--- 三只猫依次叫 ---")
for cat in cats:
    cat.speak()

# 常见误解澄清：self 不是"关键字"，也不是"类名"
# 它就是函数的第一个普通参数，只是约定俗成写成 self
# 你完全可以叫它别的名字（虽然不要这么做）
print("\n--- 用别的名字也能工作（但请不要这样写）---")


class Weird:
    def __init__(this):       # 用 this 代替 self
        this.value = 42

    def show(this):
        print("value =", this.value)


w = Weird()
w.show()       # 能正常工作！value = 42
# 但所有 Python 代码都用 self，保持一致才让别人看得懂
