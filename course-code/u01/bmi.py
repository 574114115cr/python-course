# bmi.py —— 计算 BMI

weight = 70    # 体重，单位千克（整数）
height = 1.75  # 身高，单位米（小数）

# BMI = 体重 / 身高平方，** 是幂运算符
bmi = weight / height ** 2

# 用 f-string 输出，:.2f 表示保留两位小数
print(f"你的身高是 {height} 米，体重是 {weight} 千克，BMI 是 {bmi:.2f}。")

# 顺带解释一下数值的含义
if bmi < 18.5:
    print("偏瘦")
elif bmi < 24:
    print("正常范围")
elif bmi < 28:
    print("偏重")
else:
    print("肥胖")
