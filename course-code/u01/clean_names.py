# clean_names.py —— 去前缀 / 去后缀 / 按扩展名筛选
files = ["report_2026_q1.csv", "report_2026_q2.csv", "notes.txt", "report_2026_q3.csv"]

noprefix = [f.removeprefix("report_") for f in files]
print("去前缀：" + " | ".join(noprefix))          # notes.txt 原样保留

nosuffix = [f.removesuffix(".csv").removesuffix(".txt") for f in files]
print("去后缀：" + " | ".join(nosuffix))

csv_only = [f for f in files if f.endswith(".csv")]
print("CSV  ：" + " | ".join(csv_only))
