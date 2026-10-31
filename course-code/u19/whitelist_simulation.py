# whitelist_simulation.py —— fields 白名单为什么是安全闸门

# 数据库里一条主题记录的真实长相
topic_data = {"id": 1, "text": "Python", "owner_id": 1, "date_added": "2026-10-15"}

# 表单声明的白名单：只允许用户填 text
FORM_FIELDS = ["text"]

# 恶意用户提交的表单数据：除了 text，还偷偷塞了 owner_id
submitted = {"text": "Django", "owner_id": 999}

# ===== 有白名单时：只取白名单内的字段，其余统统丢弃 =====
cleaned = {key: submitted[key] for key in FORM_FIELDS if key in submitted}
print("白名单清洗后的数据：", cleaned)
print("=> owner_id 被丢弃，用户无法把数据挂到别人名下")

# ===== 反面：把 owner_id 也加进白名单 =====
FORM_FIELDS_BAD = ["text", "owner_id"]
cleaned_bad = {key: submitted[key] for key in FORM_FIELDS_BAD if key in submitted}
print("\n白名单含 owner_id 时：", cleaned_bad)
print("=> 恶意提交的 owner_id=999 被接受，这条数据就归别人了！")

# 结论：fields = ['text'] 这行不是省事，是安全闸门
print("\nowner_id 从来不由用户填写，而由系统根据 request.user 盖章：")
topic_data.update(cleaned)
topic_data["owner_id"] = 1      # 系统盖章：当前登录用户的 ID
print("最终存入数据库的记录：", topic_data)
