# project_doctor.py —— 检查一个项目该有的工程件是否齐全
# 用法：python project_doctor.py [项目根目录，默认为当前目录]
import sys
from pathlib import Path

REQUIRED = ["README.md", "requirements.txt", ".gitignore"]
IGNORE_KEYWORDS = ["__pycache__", "venv", "db.sqlite3"]
SECRET_NAMES = ["SECRET_KEY", "PASSWORD", "API_KEY", "TOKEN"]
SKIP_DIRS = {".git", "__pycache__", "venv", ".venv", "env", "node_modules"}
FILE_LIMIT = 300


def read_text(path):
    """读文件；不存在或编码不对就返回空字符串。"""
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def check_requirements(root):
    """依赖清单有没有锁版本。返回 None 表示通过。"""
    path = root / "requirements.txt"
    if not path.exists():
        return "requirements.txt 不存在"
    unpinned = [ln.strip() for ln in read_text(path).splitlines()
                if ln.strip() and not ln.strip().startswith("#")
                and "==" not in ln]
    return f"有 {len(unpinned)} 个依赖没锁版本，例如：{unpinned[:3]}" if unpinned else None


def check_gitignore(root):
    """.gitignore 有没有覆盖关键条目。"""
    path = root / ".gitignore"
    if not path.exists():
        return ".gitignore 不存在"
    missing = [k for k in IGNORE_KEYWORDS if k not in read_text(path)]
    return f".gitignore 缺少：{missing}" if missing else None


def report(root):
    """跑完全部检查并打印报告，返回问题总数。"""
    files = [p for p in root.rglob("*.py")
             if not any(part in SKIP_DIRS for part in p.parts)]
    problems = 0
    print(f"体检对象：{root.resolve()}\n【必备工程件】")
    for name in REQUIRED:
        ok = (root / name).exists()
        print(f"  [{'OK' if ok else '缺'}] {name}")
        problems += 0 if ok else 1

    print("\n【内容检查】")
    for label, result in [("依赖清单", check_requirements(root)),
                          ("忽略清单", check_gitignore(root))]:
        print(f"  [{'OK' if result is None else '问题'}] {label}"
              + ("检查通过" if result is None else f"：{result}"))
        problems += 0 if result is None else 1

    print(f"\n【代码扫描】（共 {len(files)} 个 .py 文件）")
    # 扫硬编码密钥：排除从环境变量读的、名单字面量、没赋值的行
    secrets = []
    for path in files:
        for lineno, line in enumerate(read_text(path).splitlines(), 1):
            if not any(k in line for k in SECRET_NAMES):
                continue
            if "os.environ" in line or "getenv" in line:
                continue
            if "=" not in line or "[" in line or "{" in line:
                continue
            if len(line.split("=", 1)[1].strip()) > 8:
                secrets.append(f"{path}:{lineno}")
    long_files = [f"{p}（{len(read_text(p).splitlines())} 行）" for p in files
                  if len(read_text(p).splitlines()) > FILE_LIMIT]
    for label, found in [("硬编码密钥检查", secrets),
                         (f"{FILE_LIMIT} 行检查", long_files)]:
        print(f"  [{'OK' if not found else '问题'}] {label}"
              + ("" if not found else f"：{found}"))
        problems += len(found)

    print()
    print(f"共发现 {problems} 个必须修的问题。" if problems
          else "体检通过：工程件齐全，可以推仓库 / 部署了。")
    return problems


if __name__ == "__main__":
    report(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("."))
