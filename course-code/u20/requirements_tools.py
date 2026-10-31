# requirements_tools.py —— 检查依赖清单：版本锁、重复项、关键包是否齐全
from pathlib import Path

# 云端跑起来必不可少的包（gunicorn/psycopg2 在 requirements_remote.txt 里）
NEEDED = {"django", "django-bootstrap5", "gunicorn", "psycopg2", "platformshconfig"}

REQUIREMENTS_TXT = """asgiref==3.7.2
Django==4.2.10
django-bootstrap5==23.4
platformshconfig==2.4.0
sqlparse==0.4.4
"""

REQUIREMENTS_REMOTE_TXT = """# Requirements for live project.
gunicorn
psycopg2
"""


def parse(text, source):
    """解析一份依赖清单，返回 {包名: 版本} 和问题列表。"""
    packages, problems = {}, []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            problems.append(f"{source} 第{lineno}行「{line}」没锁版本，云端可能装到不兼容的新版")
            continue
        name, version = line.split("==", 1)
        name = name.strip().lower()
        if name in packages:
            problems.append(f"{source} 第{lineno}行「{name}」重复了")
        packages[name] = version.strip()
    return packages, problems


def check():
    packages, problems = parse(REQUIREMENTS_TXT, "requirements.txt")
    remote_packages, _ = parse(REQUIREMENTS_REMOTE_TXT, "requirements_remote.txt")
    print(f"共解析出 {len(packages)} 个本地依赖、{len(remote_packages)} 个线上依赖")

    missing = NEEDED - set(packages) - set(remote_packages)
    if missing:
        problems.append(f"缺少部署必需包：{sorted(missing)}")
    if problems:
        print(f"发现 {len(problems)} 个问题：")
        for item in problems:
            print(f"  [问题] {item}")
    else:
        print("体检通过：版本都已锁定，部署必需包齐全。")

    # 反面教材：requests 没锁版本 + Django 重复出现
    _, bad = parse("requests\nDjango==4.2\nDjango==5.0\n", "坏例子.txt")
    for item in bad:
        print(f"  [反面教材] {item}")


if __name__ == "__main__":
    check()
