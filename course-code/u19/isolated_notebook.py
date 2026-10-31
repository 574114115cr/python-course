# isolated_notebook.py —— 纯 Python 实现三道防线

# 内存「数据库」：{用户名: {主题ID: 主题文本}}
NOTEBOOK = {
    "eric": {1: "Python", 2: "Django"},
    "willie": {3: "私密日记"},
}

# 当前登录用户（None 表示未登录）
current_user = None

# 表单白名单：用户只能填 text，owner 一律由系统决定
FORM_FIELDS = ["text"]


def login(username):
    """登录：设置当前用户。"""
    global current_user
    if username not in NOTEBOOK:
        raise ValueError(f"用户 {username} 不存在")
    current_user = username


def logout():
    """注销。"""
    global current_user
    current_user = None


def check_login():
    """门禁：未登录就拒绝。"""
    if current_user is None:
        raise PermissionError("未登录，请先登录")


def submit_topic(submitted):
    """白名单表单：只接 text，归属由 current_user 决定。"""
    check_login()
    cleaned = {key: submitted[key] for key in FORM_FIELDS if key in submitted}
    # 用户塞的 owner 被丢弃；归属永远来自系统
    topic_id = max(
        tid for topics in NOTEBOOK.values() for tid in topics
    ) + 1
    NOTEBOOK[current_user][topic_id] = cleaned["text"]
    return topic_id


def list_topics():
    """数据隔离：只返回当前用户的主题。"""
    check_login()
    return dict(NOTEBOOK[current_user])       # 拷贝一份，防外部改动


def get_topic(topic_id):
    """详情层：查不到或不属于当前用户，一律 KeyError（相当于 404）。"""
    check_login()
    topics = NOTEBOOK[current_user]
    if topic_id not in topics:
        raise KeyError(f"主题 {topic_id} 不存在或不属于你")
    return topics[topic_id]


# ===== 演示：三道防线如何各自生效 =====
print("=== 防线一：白名单 ===")
login("eric")
malicious = {"text": "假装是别人的", "owner": "willie"}
new_id = submit_topic(malicious)
print(f"提交了 {malicious}")
print(f"实际存入：{{'text': {NOTEBOOK['eric'][new_id]!r}, 'owner': 'eric'}}")
print("=> 恶意塞的 owner=willie 被丢弃，归属由系统盖章")

print("\n=== 防线二：门禁 ===")
logout()
try:
    list_topics()
except PermissionError as error:
    print("未登录调用 list_topics() ->", error)

print("\n=== 防线三：数据隔离 ===")
login("eric")
print("eric 的主题：", list_topics())
try:
    get_topic(3)          # willie 的主题
except KeyError as error:
    print("eric 请求主题 3 ->", error)
login("willie")
print("willie 的主题：", list_topics())
print("willie 请求主题 3 ->", get_topic(3))
