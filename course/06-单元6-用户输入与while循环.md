# 单元 6：用户输入和 while 循环

> 对应教材第 7 章「用户输入和 while 循环」
> 关键词：`input()`、`int()`、`while`、`break`、`continue`、`while...else`、标志位 flag、交互式循环

---

## 一、学习目标

完成本单元后，你应该能够：

1. 用 `input()` 读取用户输入，并熟练完成「输入字符串 → 转换类型 → 参与运算」这三步。
2. 解释 `for` 与 `while` 的选择依据，能说出「循环次数未知用 `while`」这条判断规则。
3. 写出带条件的 `while` 循环，并说清条件为假时循环体一次都不执行。
4. 熟练使用 `break`（跳出）和 `continue`（跳过本轮），并用 `while ... else` 组织「循环正常结束」的逻辑。
5. 独立完成猜数字游戏，掌握 `while True` + `break` 这个交互程序的标准骨架。

---

## 二、核心知识点讲解

### 2.1 input() 的铁律：拿回来的永远是字符串

```python
age = input("请输入年龄：")
print(type(age))     # <class 'str'>   哪怕你输入 18，它也是字符串 "18"
```

这带来一个必须处理的经典问题：

```python
age = input("年龄：")       # 用户输入 18
print(age + 1)
# TypeError: can only concatenate str (not "int") to str
```

生活化类比：`input()` 相当于一个**只认字不认数的管理员**。你把数字 "18" 递过去，他不管你写的是数字还是文字，一律登记成"文字"。想让它按数字处理，你必须再翻译一次：

```python
age = int(input("年龄："))       # 用户输入 18 -> 字符串 "18" -> 整数 18
print(age + 1)                   # 19
```

**标准三步模板**：
```python
# 第1 步：用 input() 拿字符串
# 第 2 步：转成需要的类型（int / float）
# 第 3 步：参与运算或输出
```

还有个实用技巧——**给 input 加提示信息**：
```python
name = input("请输入你的名字：")          # 带提示
name = input()                          # 不带提示
```
默认没有提示，用户会一脸茫然。

### 2.2 for 还是 while：怎么选

| | `for` | `while` |
|---|---|---|
| 控制方式 | 遍历一个确定的数据序列 | 判断一个条件 |
| 循环次数 | 序列有多长就转多少圈 | 条件为真就转 |
| 适合场景 | 遍历列表、字符串、range | 次数未知、直到满足条件才停 |

选择规则一句话：**你知不知道要循环几次？知道就用 `for`，不知道就用 `while`。**

```python
# 知道次数：遍历 10 个学生 -> for
for i in range(10):
    process(i)

# 不知道次数：一直问，直到用户输对了 -> while
while True:
    answer = input("请输入正确答案：")
    if answer == "python":
        break
```

生活化类比：
- **`for` 像按清单点名**——名单上有 10 个人，念完 10 个就结束。
- **`while` 像守门等人**——你说"他来了我就开门"，所以得一直站着等，来几个人都不确定。

### 2.3 while 的核心：条件先行

```python
count = 0
while count < 3:
    print(count)
    count += 1
# 输出 0 1 2
```

**三个必须记住的点：**

1. **条件为假时，循环体一次都不执行。**

   ```python
   count = 10
   while count < 3:
       print("永远不会打印")
       count += 1
   ```

2. **必须有让条件变假的那一行**，否则进入死循环。

   ```python
   # INTENTIONALLY-BROKEN 演示死循环：运行它会停不下来，必须按 Ctrl+C 强制中断
   # 死循环：count 永远是 0，永远小于 3
   count = 0
   while count < 3:
       print(count)     # 停不下来，只能按 Ctrl+C 强制中断
   ```

   调试死循环时最直接的救命办法：**在循环里加一行 `print(count)`**，看它到底变没变。

3. **Python 允许 `while count:` 这种写法**——条件本身是整数时，0 为假、非 0 为真。

   ```python
   n = 3
   while n:
       print(n)
       n -= 1
   ```

   这个写法很地道，但初学阶段建议写完整的 `while n > 0:`，更明确。

### 2.4 break 与 continue

```python
# break：立刻跳出整个循环
for i in range(10):
    if i == 3:
        break        # 直接跳出，后面的不再执行
    print(i)
# 输出 0 1 2

# continue：跳过本轮，直接进入下一轮
for i in range(10):
    if i % 2 == 0:
        continue     # 偶数跳过，只打印奇数
    print(i)
# 输出 1 3 5 7 9
```

生活化类比：
- **`break` 是"提前下课"**——举手表说"这节课剩下的不上了"，直接走人。
- **`continue` 是"这题跳过，下一题"**——留在教室里，只是跳过当前这一题。

一个常见混用错误：
```python
# 错误：continue 之后多余的代码永远执行不到
for i in range(5):
    if i == 2:
        continue
        print("这里永远不执行")   # 缩进在 if 块内，且在 continue 之后

    print(i)
```

### 2.5 while ... else：循环"没被打断"时执行

这是一个非常优雅但很少人用、却极其好用的结构：

```python
while 次数 < 3:
    ...
else:
    print("三次机会都用完了，仍然没猜对")
```

`else` 块只在**循环正常走完**（没有被 `break` 打断）时执行。一旦 `break`，`else` 就被跳过。

生活化类比：**"如果这节课没被老师叫停，就说明大家表现好，下课"**。一旦被叫停（有 break），这个"表扬"就不会发生。

```python
# 猜谜游戏的标准写法
guess = 0
while guess < 3:
    answer = int(input("1-10 猜个数："))
    if answer == 7:
        print("猜对了！")
        break
    guess += 1
else:
    print("机会用完了")
```

这段代码读起来非常自然：猜对了就 `break` 走人，猜满 3 次还没对就落进 `else`。**这是单元 11 猜数字游戏的核心结构。**

### 2.6 交互程序的骨架

任何需要"反复问用户"的程序，都是这个模式：

```python
while True:                # 无限循环
    用户输入 = input(...)
    if 输入 == "退出":       # 用户主动要求结束
        break                # 用 break 跳出无限循环
    if 输入无效:
        print("请重新输入")   # 用 continue 回到循环开头
        continue
    处理有效的输入
print("程序结束")             # 只有 break 出来才会走到这里
```

**注意这个模式的关键点**：
- `while True` 本身没有出口，**唯一**的出口是 `break`。
- 所以每一条通向"用户想退出"的路径，都必须有 `break`。
- 这也是为什么必须有"退出"这个选项——否则用户被永远困在里面。

这个骨架在单元 11 的猜数字游戏、投票分析器里会反复出现，请务必掌握到能默写。

---

## 三、可运行代码示例

### 示例 1：input 的类型陷阱与三步模板

```python
# input_demo.py —— input() 永远返回字符串

# 观察类型：无论输入什么，type 都是 str
age = input("请输入年龄：")
print(f"你输入了 {age}，类型是 {type(age)}")

# 直接做加法会报错（取消下面两行的注释运行看看）
# print(age + 1)     # TypeError: can only concatenate str to int

# 正确做法：三步模板
age = int(input("请输入年龄："))     # 第1、2 步：输入 + 转整数
next_age = age + 1# 第 3 步：参与运算
print(f"明年你{next_age} 岁")

# float 输入
price = float(input("请输入价格："))
print(f"含税价格：{price * 1.13:.2f} 元")

# ===== 三步模板的完整演示 =====
# 第 1 步：用 input() 拿字符串
raw = input("请输入两个数，用空格分隔（如 10 5）：")
# 第 2 步：用 split() 拆开，再转成数字
parts = raw.split()# 得到字符串列表 ['10', '5']
a = int(parts[0])
b = int(parts[1])
# 第 3 步：运算
print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} × {b} = {a * b}")
```

### 示例 2：while 基本循环

```python
# while_basics.py —— while 循环的基本形态

# 1）最基础的计数循环
count = 0
while count < 5:
    print(f"第 {count} 次")
    count += 1# 关键：这行让条件最终变假，否则死循环
print("循环结束，count =", count)

# 2）条件一开始就为假 -> 循环体一次都不执行
count = 100
while count < 5:
    print("这句话永远不会打印")
    count += 1
print("因为条件为假，直接跳过了循环体")

# 3）条件为真就停（注意 != 的用法）
password = ""
while password != "python123":
    password = input("请输入密码：")
print("密码正确，欢迎！")

# 4）条件本身是数字：Python 允许（0 为假，非 0 为真）
n = 3
while n:
    print(n)
    n -= 1
print("n 减到 0，循环自动结束")

# ===== 死循环演示（请务必自己跑一次看看）=====
# count = 0
# while count < 3:
#     print("停不下来", count)
#     # 忘了写 count += 1，永远停不了
# 按 Ctrl+C 可以强制中断
```

### 示例 3：break 与 continue

```python
# break_continue.py —— 两个跳出关键字

# break：跳出整个循环
print("--- break 演示 ---")
for i in range(10):
    if i == 3:
        print("遇到 3，停止遍历")
        break            # 直接跳出，后面 4~9 都不再处理
    print(i)

# continue：跳过本轮
print("\n--- continue 演示 ---")
for i in range(10):
    if i % 2 == 0:
        continue         # 偶数跳过，只打印奇数
    print(i)

# 两者配合：过滤并求和
print("\n--- 综合运用 ---")
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
total = 0
for n in numbers:
    if n < 3:
        continue         # 小于 3 的不要
    if n > 8:
        break            # 大于 8 就停，反正后面只会更大
    total += n
print("3 到 8 的总和：", total)   # 3+4+5+6+7+8 = 33

# 常见错误：continue 之后的代码永远执行不到
print("\n--- 常见错误 ---")
for i in range(5):
    if i == 2:
        continue
        print("这里永远不会执行，因为 continue 已经跳到下一轮了")
    print(i)

# ===== continue 在 while 里的一个重要用途：输入校验 =====
print("\n--- 输入校验（关键模式）---")
while True:
    age = input("请输入你的年龄：")
    # 如果不是纯数字，int() 会报 ValueError
    try:
        age = int(age)
        break            # 转换成功，说明输入有效，跳出循环
    except ValueError:
        print("输入的不是有效整数，请重新输入")
# try/except 属于单元 9 的内容，但这个模式先感受一下
```

### 示例 4：while ... else

```python
# while_else.py —— 循环正常结束才执行的 else

# 猜数游戏：猜对用 break，猜满次数落进 else
secret = 7
attempts = 3
guess = 0

while guess < attempts:
    answer = int(input("1-10 猜一个数："))
    if answer == secret:
        print("猜对了！")
        break                # 被 break 打断 -> else 不执行
    else:
        print("猜错了，再试一次")
        guess += 1
else:
    # 只有循环正常走完（没被 break）才会到这里
    print(f"{attempts} 次机会用完了，正确答案是 {secret}")

print("游戏结束")

# ===== 用同样的逻辑写个"密码强度检查" =====
password = "abc"

while len(password) < 8:
    print("密码太短，要求至少 8 位")
    break
else:
    print(f"密码长度合格：{'*' * len(password)}")

# short_password = "123"
# while len(short_password) < 8:
#     print("密码太短，要求至少 8 位")
#     break
# else:
#     print("长度合格")
```

### 示例 5：标志位 flag

当一个循环里需要触发多个 `break` 时，用一个变量"记账"更清晰：

```python
# flag_demo.py —— 用标志位组织复杂退出条件

# 问题：如果密码错误 和 用户名不存在 都要跳出，怎么写？
username = "admin"
password = "wrong"

#===== 做法一：标志位（推荐，可读性最好）=====
username_ok = False
password_ok = False

if username == "admin":
    username_ok = True
if password == "123456":
    password_ok = True

if username_ok and password_ok:
    print("登录成功")
else:
    print("用户名或密码错误")

# ===== 做法二：逻辑运算符（更简洁）=====
if username == "admin" and password == "123456":
    print("登录成功")
else:
    print("用户名或密码错误")

# ===== 标志位的真正用武之地：在循环里 =====
numbers = [10, 25, 3, 47, 8, 91]
target = 47

# 找出目标值的下标，找不到返回 -1
found_index = -1

# 标志位：记录"找到了没有"
found = False

for i, n in enumerate(numbers):
    if n == target:
        found_index = i
        found = True
        break            # 找到了就停，不必再往下看

# 用标志位决定后续走哪条路
if found:
    print(f"在索引 {found_index} 处找到了 {target}")
else:
    print(f"列表中没有 {target}")

# 也可以不用标志位，直接判断 found_index != -1
print(f"（等价判断）索引是 {found_index}")
```

### 示例 6：交互式程序骨架

```python
# interactive_skeleton.py —— 所有交互程序的通用骨架

# ===== 骨架 1：菜单循环 =====
# while True + break + continue 的完整组合
while True:
    print("\n===== 简易计算器 =====")
    print("1. 加法")
    print("2. 减法")
    print("3. 退出")

    choice = input("请选择操作：")

    if choice == "3":
        print("再见！")
        break# 唯一的出口：用户要求退出

    if choice not in ["1", "2"]:
        print("无效的选项，请重新输入")
        continue             # 回到循环开头，菜单重新打印

    a = float(input("请输入第一个数："))
    b = float(input("请输入第二个数："))

    if choice == "1":
        print(f"结果：{a + b}")
    else:
        print(f"结果：{a - b}")

print("循环外的代码，只有 break 出来才会执行")

# ===== 骨架 2：多条退出路径 =====
# 三个不同的条件都要能退出循环，用标志位最清晰
attempts_left = 3
locked = False

for i in range(attempts_left):
    print(f"你还有 {attempts_left - i} 次机会")
    answer = input("输入 'quit' 可以放弃：")

    if answer == "quit":
        print("你选择了放弃")
        break
    if answer != "yes":
        print("答案错误")
        continue

    print("回答正确！")
    locked = True
    break
else:
    print("机会用完，锁定账户")

if locked:
    print("=== 已解锁 ===")
```

### 示例 7：倒计时与死循环的自救

```python
# countdown.py —— while 的经典应用：倒计时

# 1）从 5 数到 1
count = 5
while count > 0:
    print(count)
    count -= 1
print("起飞！")

# 2）模拟"游戏存档"：一个简单的登录重试流程
print("\n--- 登录重试 ---")
max_attempts = 3
current_attempt = 0
correct_password = "python2024"

while current_attempt < max_attempts:
    password = input("请输入密码：")
    current_attempt += 1# 先计数，这样"最后一次"的判断才准

    if password == correct_password:
        print("登录成功！")
        break
    else:
        remaining = max_attempts - current_attempt
        if remaining > 0:
            print(f"密码错误，还有 {remaining} 次机会")
        else:
            print("机会用尽，账户已锁定")

# 3）===== 调试死循环的救命技巧 =====
print("\n--- 死循环调试法 ---")
# 如果 while 停不下来，先在循环体第一行加 print 观察变量：
i = 0
while i < 3:
    print(f"当前 i = {i}")   # 关键：这行告诉你 i 到底变没变
    i += 1
# 如果输出一直是"当前 i = 0"，说明你根本没写 i += 1，
# 或者写在了缩进错误的位置（比如写到了 while 外面）。
```

---

## 四、动手练习

### 基础档

**练习 6-1【三步模板转换】**
🌐 写 `input_practice.py`，要求：
1. 读取用户输入的姓名（字符串）
2. 读取用户输入的出生年份（**要转成整数**）
3. 读取用户输入的身高（**要转成小数**）
4. 计算用户 2026 年的年龄，输出"你好，XXX，你今年 XX 岁，身高 X.XX 米"
5. 如果年龄小于 0，额外输出"年龄输入有误"

**练习 6-2【数字累加到 N】**
🌐 读取用户输入的一个整数 `n`，用 `while` 循环计算并输出 `1 + 2 + 3 + ... + n` 的和。
输入 `10` → 输出 `55`
进阶：用 `for` 再写一遍，对比两种写法。

**练习 6-3【倍数输出】**
用 `while` 循环输出 1–50 之间所有 7 的倍数，每个一行。
再用 `while` 输出 1–50 之间所有同时是 3 和 5 的倍数。

**练习 6-4【break 找数】**
给定 `numbers = [12, 5, 33, 7, 91, 26]`，用循环找出第一个大于 30 的数：
- 找到就用 `break` 停下，并输出它的**下标**和**值**
- 如果一个都没有，输出"没有找到"
提示：`enumerate()` 可以同时拿到下标和值。

### 进阶档

**练习 6-5🌐【猜数字游戏（完整版）】**
这是本单元最重要的练习，也是单元 11 关卡验收的项目之一。
要求：
1. 程序随机生成一个 1–100 的整数（`import random` → `random.randint(1, 100)`）
2. 用 `while True` 循环持续读取用户猜测
3. 猜对了输出"恭喜你猜对了！一共猜了 X 次"，用 `break` 跳出
4. 猜错了给出提示：
   - 猜的数字太大 → "太大了，再小一点"
   - 猜的数字太小 → "太小了，再大一点"
5. 提供退出方式：用户输入 `q` 或 `quit` 时，用 `break` 结束游戏
6. 统计用户的猜测次数

**练习 6-6【while...else 重试机制】**
设计一个"输密码"程序：
- 正确密码是 `"py2026"`，最多 3 次机会
- 用 `while ... else` 结构实现：猜满 3 次仍未正确，输出"账户锁定"并落进 `else`
- 输入 `"exit"` 可以主动放弃
- 每次失败后提示剩余机会

**练习 6-7🌐【输入校验循环】**
写一个"读入有效正整数"的健壮程序：
- 提示用户输入一个正整数
- 如果输入的不是数字（`ValueError`），输出提示并要求重新输入
- 如果输入的是 0 或负数，输出"请输入大于 0 的整数"并重新输入
- 拿到有效输入后输出"你输入的数是 X"，结束循环
要求：用 `while True` + `break` 骨架，校验逻辑先感受一下即可（单元 9 会正式讲 `try/except`，这里允许用 `try/except`，也允许用 `.isdigit()`）。

**练习 6-8【嵌套 while：九九乘法表前 3 行】**
用嵌套 `while` 循环输出九九乘法表的前 3 行：
```
1×1=1
1×2=2   2×2=4
1×3=3   2×3=6   3×3=9
```
提示：外层循环控制行号，内层循环控制每行有几个式子。
**注意观察**：内层循环的变量在每轮外层循环开始时必须重置，否则会出错——这是嵌套循环最经典的 bug。

---

## 五、参考答案

### 参考答案 6-1

```python
# input_practice.py —— input 三步模板完整应用

# 第 1 步 + 第 2 步：读取并转换类型
name = input("请输入你的姓名：")
birth_year = int(input("请输入你的出生年份："))
height = float(input("请输入你的身高（米）："))

# 第 3 步：参与运算
current_year = 2026
age = current_year - birth_year

# 用 f-string 输出
print(f"你好，{name}，你今年 {age} 岁，身高 {height:.2f} 米")

# 附加校验
if age < 0:
    print("年龄输入有误：出生年份不能大于今年")
elif age > 120:
    print("年龄输入有误：超过 120 岁")
elif height <= 0:
    print("身高数据无效")
else:
    print(f"验证通过：{name}，{age} 岁，{height:.2f} 米")
```

### 参考答案 6-2

```python
# sum_to_n.py —— while 与 for 两种写法的对比

n = int(input("请输入一个正整数 n："))

# ===== while 写法 =====
total = 0
i = 1
while i <= n:
    total += i
    i += 1
print(f"while 写法：1 到 {n} 的和是 {total}")

# ===== for 写法（更简洁，因为次数已知）=====
total2 = sum(range(1, n + 1))
print(f"for 写法：1 到 {n} 的和是 {total2}")

# ===== 另一种 while 写法：用累加器技巧 =====
total3 = 0
counter = n
while counter > 0:
    total3 += counter
    counter -= 1
print(f"倒着加：{total3}")

# 验证几个固定答案
for n in [1, 5, 10, 100]:
    print(f"n={n} 时和为 {sum(range(1, n + 1))}")
# n=1 -> 1, n=5 -> 15, n=10 -> 55, n=100 -> 5050
```

### 参考答案 6-3

```python
# multiples.py —— 用 while 输出倍数

# 1）1–50 之间所有 7 的倍数
print("--- 7 的倍数 ---")
n = 1
while n <= 50:
    if n % 7 == 0:
        print(n)
    n += 1

# 更简洁的等价写法：用 while 变量本身就以 7 为步长
print("--- 7 的倍数（步长版）---")
n = 7
while n <= 50:
    print(n)
    n += 7

# 2）1–50 之间同时是 3 和 5 的倍数（即 15 的倍数）
print("--- 同时是 3 和 5 的倍数 ---")
n = 1
while n <= 50:
    if n % 3 == 0 and n % 5 == 0:
        print(n)
    n += 1
# 输出：15 30 45

# 也可以用"lcm"（最小公倍数）的思路：15 的倍数就是答案
print("--- 15 的倍数 ---")
n = 15
while n <= 50:
    print(n)
    n += 15

# 顺带做一个和：1–100 之间所有 7 的倍数之和
total = 0
n = 7
while n <= 100:
    total += n
    n += 7
print(f"7 的倍数之和：{total}")   # 7+14+...+98 = 735
```

### 参考答案 6-4

```python
# find_first.py —— 用 break 找第一个符合条件的数

numbers = [12, 5, 33, 7, 91, 26]

# ===== 写法一：用标志位（能表达"没找到"的情况）=====
target_value = 30
found = False
found_index = -1

for index, number in enumerate(numbers):
    if number > target_value:
        found_index = index
        found = True
        break                # 找到第一个就停

if found:
    print(f"第一个大于 {target_value} 的数是 {numbers[found_index]}，"
          f"下标是 {found_index}")
else:
    print(f"没有找到大于 {target_value} 的数")

# ===== 写法二：用一个哨兵值（-1）表达"没找到" =====
def find_first(items, limit):
    """返回第一个大于 limit 的元素及其下标，都找不到时返回 (None, -1)。"""
    for index, item in enumerate(items):
        if item > limit:
            return item, index
    return None, -1


result, index = find_first(numbers, 30)
if result is None:
    print("没有找到")
else:
    print(f"找到 {result}，下标 {index}")

# ===== 测试边界情况：全部都小于阈值 =====
print(find_first([1, 2, 3], 100))    # (None, -1)
print(find_first([1, 50, 3], 30))    # (50, 1)
```

### 参考答案 6-5

```python
# guess_number.py —— 完整的猜数字游戏

import random


def play_guess_number():
    """启动猜数字游戏主流程。"""
    # 生成 1–100 的随机整数
    secret = random.randint(1, 100)
    count = 0
    history = []             # 记录猜测历史，方便复盘

    print("=" * 40)
    print("欢迎来到猜数字游戏！")
    print("我已经想好了一个 1 到 100 之间的整数")
    print("输入 'quit' 可以随时退出")
    print("=" * 40)

    # ===== 标准骨架：while True + 唯一出口 break =====
    while True:
        raw = input("请输入你的猜测（1-100）：")

        # 退出通道：用户主动结束
        if raw in ["quit", "q", "exit"]:
            print("游戏已退出，答案是", secret)
            print("你的猜测记录：", history)
            break

        # 把字符串转成整数，转换失败就重新问
        try:
            guess = int(raw)
        except ValueError:
            print(f"'{raw}' 不是有效数字，请重新输入")
            continue

        # 超出范围提示
        if guess < 1 or guess > 100:
            print("请输入 1 到 100 之间的数字")
            continue

        count += 1
        history.append(guess)

        if guess < secret:
            print(f"太小了，再大一点（第 {count} 次猜测）")
        elif guess > secret:
            print(f"太大了，再小一点（第 {count} 次猜测）")
        else:
            print("=" * 40)
            print(f"恭喜你猜对了！答案就是 {secret}")
            print(f"你一共猜了 {count} 次")
            print(f"你的猜测记录：{history}")
            print("=" * 40)
            break                   # 猜对了，唯一的正常出口

    return count


# 游戏结束后统计一下平均猜测次数
counts = [play_guess_number()]
print(f"本次游戏共猜了 {counts[0]} 次")
```

### 参考答案 6-6

```python
# password_retry.py —— 用 while...else 实现重试机制

correct_password = "py2026"
max_attempts = 3
attempt = 0

while attempt < max_attempts:
    password = input(f"请输入密码（还可尝试 {max_attempts - attempt} 次）：")
    attempt += 1

    # 主动放弃
    if password == "exit":
        print("你选择了放弃本次输入")
        break

    if password == correct_password:
        print(f"密码正确！你在第 {attempt} 次尝试时成功登录")
        break
    else:
        print("密码错误")
else:
    # 只有循环正常走完（尝试满 3 次都没 break）才会到这里
    print("-" * 30)
    print("错误次数已达上限，账户被锁定")
    print("-" * 30)

# ===== 对比：如果不用 while...else，长什么样 =====
# 需要一个额外的标志位来记住"是不是正常走完的"
# attempt < max_attempts 这个循环结束后，
# 如果 attempt == max_attempts，说明三次都错了
attempt2 = 0
while attempt2 < max_attempts:
    pwd = input("密码：")
    if pwd == "exit":
        break
    if pwd == correct_password:
        print("成功")
        break
    attempt2 += 1

if attempt2 == max_attempts:
    print("账户锁定")
# 结论：while...else 把"是否正常结束"这件事表达得干净得多
```

### 参考答案 6-7

```python
# input_validation.py —— 读入一个有效的正整数

print("请输入一个正整数：")

while True:
    raw = input("> ")

    # ===== 方式一：try/except（推荐，单元 9 会正式讲）=====
    try:
        number = int(raw)
    except ValueError:
        print(f"'{raw}' 不是有效的整数，请重新输入")
        continue             # 回到循环开头重新要一次

    # 整数校验通过，再检查范围
    if number <= 0:
        print("请输入大于 0 的整数")
        continue

    # 到这里说明输入完全合法，用 break 跳出无限循环
    print(f"你输入的数是 {number}")
    break

print("程序继续往下执行，说明已经拿到了有效输入")

# ===== 方式二：不用 try，用 str.isdigit() =====
# 注意 isdigit() 的局限：
#   "12".isdigit()    -> True
#   "-12".isdigit()   -> False  （负号不是数字字符）
#   "1.5".isdigit()   -> False  （小数点不是数字字符）
print("\n--- 用 isdigit 的版本 ---")
while True:
    raw = input("> ")
    if not raw.isdigit():
        print("请输入纯数字")
        continue
    number = int(raw)
    if number <= 0:
        print("请输入大于 0 的整数")
        continue
    print(f"你输入的数是 {number}")
    break
```

### 参考答案 6-8

```python
# multiplication_table.py —— 嵌套 while 循环

# 完整九九乘法表
print("--- 完整九九乘法表 ---")
i = 1
while i <= 9:
    j = 1
    while j <= i:                     # 内层：每行输出 i 个式子
        print(f"{j}×{i}={j * i}", end="\t")
        j += 1
    print()# 换行，让下一个 i 另起一行
    i += 1

# 只输出前 3 行
print("\n--- 前 3 行 ---")
i = 1
while i <= 3:
    j = 1
    while j <= i:
        print(f"{j}×{i}={j * i}", end="\t")
        j += 1
    print()
    i += 1

# ===== 嵌套循环的经典 bug：内层变量没重置 =====
# 下面这段会输出错误结果
# i = 1
# while i <= 3:
#     j = 1
#     while j <= i:
#         print(j, end=" ")
#         j += 1
#     print()
#     # 忘记写 j = 1，第二轮 i=2 时 j 已经是 2，循环一次都不执行
#     i += 1

# 正确写法：内层循环的变量必须在每轮外层循环里重新初始化
print("\n--- 固定版---")
i = 1
while i <= 3:
    j = 1                 # 关键：每轮外层循环开始时重置
    while j <= i:
        print(f"{j}×{i}={j * i}", end="\t")
        j += 1
    print()
    i += 1

# 观察输出：
# 1×1=1
# 1×2=2   2×2=4
# 1×3=3   2×3=6   3×3=9
```

---

## 六、本单元验收自测

**1. 简答题**：下面代码输出什么？
```python
# INTENTIONALLY-BROKEN 演示：字符串不能直接和整数相加，会抛 TypeError
age = "20"
print(age + 5)
```
> **要点**：会报 `TypeError: can only concatenate str (not "int") to str`。`input()` 返回的永远是字符串，`"20"` + `5` 是字符串拼接的意图但类型不允许。正确做法：`age = int(input(...))`，即 `int("20") + 5` 得 `25`。

**2. 简答题**：下面代码会输出什么？为什么？
```python
count = 10
while count < 5:
    print("你好")
    count += 1
```
> **要点**：什么都不输出。`while` 是**先判断条件再执行**，第一次判断 `10 < 5` 就是假，所以循环体一次都不执行。这是 `while` 和 `for` 的重要差别之一（`for` 在序列为空时同样不执行，但 `while` 的"不执行"发生在任何一行代码之前）。

**3. 判断题**：`break` 和 `continue` 的区别在于：`break` 结束整个循环，`continue` 只跳过本次循环。
> **要点**：正确。`break` 一旦执行，整个最内层循环立即结束，控制流跳到循环之后；`continue` 立刻开始下一轮循环，本次循环体中 `continue` 之后的所有代码都不会执行。两者都只作用于**最内层**循环——嵌套循环里的 `break` 只能跳出内层。

**4. 简答题**：`while ... else` 中的 `else` 在什么情况下会被执行？什么情况下会被跳过？
> **要点**：`else` 块只在循环**自然结束**（条件变假而退出）时执行。一旦循环被 `break` 打断，`else` 就被跳过。典型用途：游戏重试机制——猜对了 `break` 走人，猜满次数没 `break` 就落进 `else` 执行"机会用完"的逻辑。

**5. 简答题**：为什么 `while True` 循环必须设计"退出"选项？写出这个骨架的关键组成部分。
> **要点**：因为 `while True` 的条件永远是真，循环**没有任何自动出口**，唯一的出口是 `break`。如果不提供退出方式，用户会被永久困在循环里，程序也无法结束。骨架四个部分：① `while True:` 开始无限循环；② 用 `input()` 读取用户输入；③ `if 输入 == "退出"` 则 `break`；④ `if 输入无效` 则 `continue`（或 `continue` 让流程回到循环开头），末尾放一句"程序结束"作为 break 之后的出口标记。

---

## 本单元小结与产出检查

- [ ] 能默写 `while True` + `break` + `continue` 的交互骨架
- [ ] 能解释 `while` 与 `for` 各自的适用场景
- [ ] 能说出 `while ... else` 的执行条件
- [ ] 猜数字游戏（练习 6-5）已能独立跑通
- [ ] 知道死循环时怎么用 `print` 自救

**下一单元预告**：单元 7 讲函数——把反复写的代码打包成一个"有名字的积木"，从此不用复制粘贴。学习 `def` 定义、`return` 返回值、参数（位置参数、关键字参数、默认参数、可变参数）、以及本单元重点：**参数传递的副本语义**（为什么函数里修改列表会改到原列表）以及一节「常见错误清单」。