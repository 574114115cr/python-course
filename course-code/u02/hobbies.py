# hobbies.py —— 我的收藏清单

hobbies = ["阅读", "篮球", "烹饪", "摄影", "吉他"]
print("我的爱好：", hobbies)
print("一共有", len(hobbies), "个爱好")            # 5 个

print("第一个爱好：", hobbies[0])                # 阅读
print("最后一个爱好：", hobbies[-1])               # 吉他
print("最后一个爱好的长度：", len(hobbies[-1]))      # 2

hobbies.append("爬山")
print("追加后：", hobbies)
