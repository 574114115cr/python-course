# leap_year.py —— 闰年判断

# 规则：能被 400 整除，或者能被 4 整除但不能被 100 整除
def is_leap(year):
    if year % 400 == 0:
        return True
    elif year % 4 == 0 and year % 100 != 0:
        return True
    else:
        return False


for year in [2000, 1900, 2024, 2023, 2400]:
    if is_leap(year):
        print(f"{year} 是闰年")
    else:
        print(f"{year} 不是闰年")

# 输出：
# 2000 是闰年
# 1900 不是闰年
# 2024 是闰年
# 2023 不是闰年
# 2400 是闰年

# 纯 if 版本（不用函数，直接循环判断）
print("--- 不用函数的版本 ---")
for year in [2000, 1900, 2024, 2023]:
    if year % 4 == 0 and year % 100 != 0:
        print(f"{year} 是闰年")
    elif year % 400 == 0:
        print(f"{year} 是闰年")
    else:
        print(f"{year} 不是闰年")

# 注意：上面的顺序也正确，因为能被 400 整除的数也一定被 4 整除，
# 所以第一个条件不会误伤它们。两种顺序都可以，但函数版本更清晰。
