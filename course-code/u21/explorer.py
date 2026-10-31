# explorer.py —— 30 秒速读一个陌生项目
# 用法：python explorer.py [项目根目录]
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", "venv", ".venv", "env", "node_modules",
             ".idea", ".vscode", "static", "migrations"}
TEXT_SUFFIXES = {".py", ".txt", ".md", ".cfg", ".toml", ".yaml", ".yml",
                 ".json", ".ini", ".env"}
ENTRY_MARKERS = ('if __name__ == "__main__"', "def main(")
READ_ORDER = ["项目说明", "依赖清单", "★ 程序入口", "★ Django 入口",
              "配置文件", "业务逻辑", "测试"]


def read_text(path):
    """读文件；编码不对就返回空字符串。"""
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def guess_role(path, source):
    """根据文件名和内容猜这个文件的角色。"""
    name = path.name
    if name == "manage.py":
        return "★ Django 入口"
    if name in ("settings.py", "config.py", ".env"):
        return "配置文件"
    if name == "requirements.txt":
        return "依赖清单"
    if name.startswith("test_") or "tests" in path.parts:
        return "测试"
    if name.lower().startswith("readme"):
        return "项目说明"
    if any(m in source for m in ENTRY_MARKERS):
        return "★ 程序入口"
    return "业务逻辑" if "def " in source or "class " in source else "数据/其他"


def scan_files(root):
    """★ 第 2–4 步：所有源码文件按角色归类，并打印依赖清单。"""
    print("\n【文件角色】")
    roles = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        if rel == "requirements.txt":
            continue                      # 依赖清单单独打印
        roles.setdefault(guess_role(path, read_text(path)), []).append(rel)
    for role in sorted(roles):
        print(f"\n{role}：")
        for name in roles[role][:8]:
            print(f"    {name}")

    print("\n【依赖清单】")
    lines = [ln.strip() for ln in read_text(root / "requirements.txt").splitlines()]
    print("\n".join(f"  {ln}" for ln in lines if ln and not ln.startswith("#"))
          or "  没有 requirements.txt —— 这本身就是一个工程问题")
    return roles


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/unknown_project")
    if not root.exists():
        print(f"目录不存在：{root}（可以先随便传一个已有目录试试）")
        return
    print(f"速读目标：{root.resolve()}\n")
    roles = scan_files(root)
    print("\n【建议阅读顺序】")
    for role in READ_ORDER:
        if role in roles:
            print(f"  {role}：{roles[role][0]}")


if __name__ == "__main__":
    main()
