# make_requirements.py —— 扫描 import 语句，列出项目用到的第三方包
# 用法：python make_requirements.py [项目根目录]
# 局限：它只猜「需要哪些包」，版本号要用 pip freeze 补上
import ast
import sys
import sysconfig
from pathlib import Path

# import 名和 PyPI 包名不一致的映射（最常踩的几个）
ALIASES = {"PIL": "Pillow", "cv2": "opencv-python",
           "sklearn": "scikit-learn", "bs4": "beautifulsoup4",
           "yaml": "PyYAML", "django_bootstrap5": "django-bootstrap5"}
INDIRECT = {"setuptools", "pip", "wheel"}
SKIP_DIRS = {".git", "__pycache__", "venv", ".venv", "env",
             "node_modules", "data", "tests"}


def known_names():
    """标准库 + 内置模块 + 已知别名，都是"不用写进 requirements"的。"""
    stdlib = Path(sysconfig.get_paths()["stdlib"])
    names = {p.stem for p in stdlib.glob("*.py")} | set(sys.builtin_module_names)
    names |= {p.name for p in stdlib.glob("*")
              if p.is_dir() and (p / "__init__.py").exists()}
    return names | set(ALIASES) | INDIRECT


def collect_imports(root, known):
    """遍历所有 .py 文件，返回 {顶层模块名: [出现位置]}（已滤掉标准库和本地模块）。"""
    found = {}
    for path in sorted(root.rglob("*.py")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [x.name.split(".")[0] for x in node.names]
            elif isinstance(node, ast.ImportFrom):
                # level > 0 是相对导入，属项目内部模块，不算依赖
                names = ([node.module.split(".")[0]]
                         if node.level == 0 and node.module else [])
            else:
                names = []
            for name in names:
                found.setdefault(name, []).append(str(path))
    return {n: p for n, p in found.items() if n not in known
            and not (root / f"{n}.py").exists()
            and not (root / n / "__init__.py").exists()}


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    imports = collect_imports(root, known_names())
    print(f"在 {root.resolve()} 中发现 {len(imports)} 个第三方依赖：")
    for name in sorted(imports):
        print(f"  {ALIASES.get(name, name):<22} ← {', '.join(imports[name][:2])}")
    print("\n下一步：在虚拟环境里执行 pip freeze，核对版本号后写成")
    print("        包名==版本号  的形式写进 requirements.txt。")


if __name__ == "__main__":
    main()
