# me_dict.py —— 字典的增删改查全流程

me = {
    "name": "小明",
    "age": 18,
    "height": 1.75,
    "city": "杭州",
}

print("初始字典：", me)
print("长度：", len(me))# 4

# 2）取出值
print("name：", me["name"])
print("city：", me["city"])

# 3）新增键：长度会 +1
me["hobby"] = "篮球"
print("新增 hobby 后长度：", len(me))    # 5

# 4）修改已有键的值：长度不变（关键知识点）
me["age"] = 19
print("修改 age 后长度：", len(me))# 仍是 5
print("现在的字典：", me)

# 5）删除键：长度会 -1
del me["height"]
print("删除 height 后长度：", len(me))# 4
print("最终字典：", me)

# 总结这张表：新增长度加1，修改长度不变，删除长度减1
