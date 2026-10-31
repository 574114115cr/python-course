# temperature.py —— 温度转换函数

def celsius_to_fahrenheit(celsius):
    """把摄氏温度转换成华氏温度。

    参数:
        celsius: 摄氏温度，数字或数字字符串
    返回:
        华氏温度（float）
    """
    # 用 float() 转换，兼容用户输入字符串的情况
    return float(celsius) * 9 / 5 + 32


def fahrenheit_to_celsius(fahrenheit):
    """把华氏温度转换成摄氏温度。"""
    return (float(fahrenheit) - 32) * 5 / 9


# 测试：输出对照表
print(f"{'摄氏':>8} | {'华氏':>8}")
print("-" * 21)
for celsius in [0, 100, 37, -40]:
    fahrenheit = celsius_to_fahrenheit(celsius)
    print(f"{celsius:>8} | {fahrenheit:>8.1f}")

# 反向验证：来回转换应该回到原点
print("\n--- 反向转换验证 ---")
for celsius in [0, 100, 37]:
    back = fahrenheit_to_celsius(celsius_to_fahrenheit(celsius))
    print(f"{celsius} -> {celsius_to_fahrenheit(celsius):.1f} -> {back:.2f}")

# 特殊值说明：-40 摄氏正好也是 -40 华氏，这是唯一一个"两温度刻度数值相同"的点
print("\n-40 摄氏 =", celsius_to_fahrenheit(-40), "华氏")
