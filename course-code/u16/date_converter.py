# date_converter.py —— 多格式日期解析

from datetime import datetime

FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]
WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

def parse_date(text):
    """依次尝试多种格式解析日期。

    成功返回 (True, 日期对象)，全部失败返回 (False, None)。
    """
    for fmt in FORMATS:
        try:
            return True, datetime.strptime(text, fmt)
        except ValueError:
            continue                     # 这种格式不行，换下一种
    return False, None

test_inputs = ["2021-07-01", "2021/07/01", "2021年7月1日", "07-01-2021", "乱七八糟"]

for text in test_inputs:
    ok, date_obj = parse_date(text)
    if ok:
        weekday = WEEKDAYS[date_obj.weekday()]      # weekday(): 周一=0
        pretty = f"{date_obj.year}年{date_obj.month:02d}月{date_obj.day:02d}日 {weekday}"
        print(f"{text!r:12} -> 解析成功: {date_obj.date()}, 格式化: {pretty}")
    else:
        print(f"{text!r:12} -> 解析失败（三种格式都不匹配）")

# 失败原因分析：
# "07-01-2021"：格式要求年份在前，它把 07 当年份、01 当月、2021 当日 -> 日越界
# "乱七八糟"：没有数字，三种格式全部 ValueError
