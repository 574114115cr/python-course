# rate_limit_guard.py —— 看配额 + 缓存；需要网络，没网走 except 分支
import json
import time
from pathlib import Path

import requests

URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}
CACHE = Path("github_repos.json")   # 跑完会删掉


def get_json(url, headers=None):
    """try/except + 状态码检查，失败返回 None——本单元的通用取数套路。"""
    try:
        response = requests.get(url, headers=headers or {}, timeout=10)
    except requests.exceptions.RequestException as error:
        print(f"  请求失败：{error}")        # 网络断了、DNS 失败、超时……
        return None
    if response.status_code != 200:
        # 403/404/429/500 一律先打印出来，别静默跳过
        print(f"  状态码 {response.status_code}，剩余配额 "
              f"{response.headers.get('X-RateLimit-Remaining', '未知')}")
        return None
    # ★ 配额只在响应对象上有，顺便查一下，低于 5 就收手
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining is not None and int(remaining) < 5:
        print(f"  警告：配额只剩 {remaining}")
    return response.json()


for query in ["language:python", "language:javascript"]:
    time.sleep(1)              # 主动限速，别把人家服务器打爆
    data = get_json(f"{URL}?q={query}&sort=stars&per_page=3", HEADERS)
    if data is None:
        break                  # 网络断了就别试下一轮
    print(f"[{query}] 拿回", [item["name"] for item in data["items"]])
    CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    break

print("已缓存到", CACHE, "，下次调试直接读它，不用再请求网络")
CACHE.unlink(missing_ok=True)     # 清理；真做项目时把缓存留着
print("说明：未认证每小时 60 次；403 和 429 都可能是限流信号。")
