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
