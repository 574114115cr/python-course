# ask_name.py —— 第一个交互程序

# input() 会暂停等待用户键盘输入，拿回来的结果永远是 str
name = input("请输入你的名字：")
age = int(input("请输入你的年龄："))   # 用 int() 把字符串转成整数

# 加 1 得到明年的年龄
next_age = age + 1

# 用 f-string 把变量嵌进句子里
print(f"你叫 {name}，你今年 {age} 岁，明年就 {next_age} 岁了。")
