# bmi_advice.py —— BMI 计算与健康建议

weight = 70# 千克
height = 1.75  # 米

# ===== 异常输入检查必须放最前面 =====
# 否则 height = 0 会导致除以零，或者算出一个荒谬的数字
if height <= 0:
    print("身高数据无效")
elif weight <= 0:
    print("体重数据无效")
else:
    # 异常都排除了，才放心做除法
    bmi = weight / height ** 2

    # 用 elif 链给建议，条件从严格到宽松
    if bmi < 18.5:
        advice = "偏瘦，建议加强营养"
    elif bmi < 24:
        advice = "正常，保持运动"
    elif bmi < 28:
        advice = "偏重，需要控制饮食"
    else:
        advice = "肥胖，建议咨询医生"

    print(f"BMI: {bmi:.2f}")
    print(f"建议: {advice}")

# ===== 批量测试各种情况 =====
test_data = [
    (50, 1.75),    # 偏瘦
    (70, 1.75),    # 正常
    (80, 1.75),    # 偏重
    (90, 1.70),    # 肥胖
    (70, 0),       # 异常：身高为0
    (0, 1.75),     # 异常：体重为 0
    (70, -1.8),    # 异常：负身高
]

for w, h in test_data:
    print("---")
    if h <= 0:
        print(f"体重{w} 身高{h} -> 身高数据无效")
    elif w <= 0:
        print(f"体重{w} 身高{h} -> 体重数据无效")
    else:
        bmi = w / h ** 2
        if bmi < 18.5:
            adv = "偏瘦，建议加强营养"
        elif bmi < 24:
            adv = "正常，保持运动"
        elif bmi < 28:
            adv = "偏重，需要控制饮食"
        else:
            adv = "肥胖，建议咨询医生"
        print(f"体重{w} 身高{h} -> BMI {bmi:.2f}，{adv}")
