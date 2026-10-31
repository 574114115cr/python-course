# tip.py —— 第 3 步：实现功能，让测试通过

def calculate_tip(bill, rate):
    """根据账单金额和小费率计算小费。

    参数:
        bill: 账单金额，数字，必须 >= 0
        rate: 小费率，0 到 1 之间，0.1 表示 10%

    返回:
        小费金额（float）
    """
    if bill < 0:
        raise ValueError("账单金额不能为负数")
    if not 0 <= rate <= 1:
        raise ValueError("小费率必须在 0 到 1 之间")
    return bill * rate
