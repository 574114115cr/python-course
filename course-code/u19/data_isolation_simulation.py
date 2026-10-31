# data_isolation_simulation.py —— .all() 和 .filter(owner=...) 的生死差别

# 内存「数据库」：三个主题，分属两个用户
DATABASE = [
    {"id": 1, "text": "Python", "owner": "eric"},
    {"id": 2, "text": "Django", "owner": "eric"},
    {"id": 3, "text": "私密日记", "owner": "willie"},
]


def all_topics():
    """错误示范：Topic.objects.all() —— 不管是谁的，全都捞出来。"""
    return list(DATABASE)


def filter_topics(owner):
    """正确写法：Topic.objects.filter(owner=request.user)。"""
    return [t for t in DATABASE if t["owner"] == owner]


print("=== 危险：用 .all() ===")
for t in all_topics():
    print(f"  {t['owner']} 的主题: {t['text']}")
print("  => eric 登录后看到了 willie 的「私密日记」——数据裸奔！")

print("\n=== 安全：filter(owner=request.user) ===")
for t in filter_topics("eric"):
    print(f"  {t['owner']} 的主题: {t['text']}")
print("  => eric 只看得到自己的两条")
for t in filter_topics("willie"):
    print(f"  {t['owner']} 的主题: {t['text']}")
print("  => willie 登录则只看得到自己的")

# 三层防护的另外两层：详情页和编辑页
print("\n=== 详情层/编辑层：查到之后再比对归属 ===")
topic = DATABASE[2]          # willie 的主题
current_user = "eric"
if topic["owner"] != current_user:
    print(f"  {current_user} 请求主题「{topic['text']}」-> raise Http404")
    print("  => 不是你的东西，当成不存在（连「存在但不给你看」都不透露）")
