# host_check.py —— 复现 Django 的主机校验，看懂 400 从哪来

def is_host_allowed(host, allowed_hosts):
    """Django 校验 Host 的核心规则（教学简化版）。"""
    if "*" in allowed_hosts:
        return True
    host = host.split(":")[0]          # 去掉端口号：localhost:8000 → localhost
    for pattern in allowed_hosts:
        if pattern == host:
            return True
        if pattern.startswith(".") and host.endswith(pattern):
            return True                # ".platformsh.site" 匹配所有子域名
    return False


if __name__ == "__main__":
    local_only = ["localhost", "127.0.0.1"]
    online = "learning-log-main-abc123.us-3.platformsh.site"
    print("场景一：ALLOWED_HOSTS =", local_only)
    print("  本地域名 ->", "200 OK" if is_host_allowed("localhost:8000", local_only) else "400")
    print("  线上域名 ->", "200 OK" if is_host_allowed(online, local_only) else "400 Bad Request（DisallowedHost）")

    # 场景二：加上 .platformsh.site（对应 settings.py 里 append 的那行）
    fixed = local_only + [".platformsh.site"]
    print("\n场景二：ALLOWED_HOSTS =", fixed)
    print("  线上域名 ->", "200 OK" if is_host_allowed(online, fixed) else "400 Bad Request")
