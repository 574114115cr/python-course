# code_metrics.py —— 统计文件行数、函数长度和圈复杂度近似值
# 用法：python code_metrics.py [项目根目录]
# 只用标准库，不会导入你的项目代码
import ast
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", "venv", ".venv", "env", "node_modules", "data"}
FILE_LIMIT, FUNC_LIMIT, COMPLEXITY_LIMIT = 300, 50, 8
BRANCH_NODES = (ast.If, ast.IfExp, ast.While, ast.For, ast.AsyncFor,
                ast.ExceptHandler, ast.With, ast.AsyncWith, ast.Assert,
                ast.comprehension)


def count_decisions(node):
    """数一遍「会改变控制流」的节点数量，作为圈复杂度的近似。"""
    total = 0
    for child in ast.walk(node):
        if isinstance(child, BRANCH_NODES):
            total += 1
        elif isinstance(child, ast.BoolOp):
            total += max(0, len(child.values) - 1)   # a and b：每多一项 +1
        elif isinstance(child, ast.Match):
            total += len(child.cases)
    return total


def analyze_source(source, filename):
    """解析一个文件，返回 {文件, 总行数, 函数列表}（按复杂度降序）。"""
    result = {"文件": filename, "总行数": len(source.splitlines()), "函数": []}
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        result["错误"] = str(error)
        return result
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            length = getattr(node, "end_lineno", start) - start + 1
            result["函数"].append({
                "名字": node.name, "行号": start, "长度": length,
                "复杂度": count_decisions(node) + 1})   # 圈复杂度 = 决策点 + 1
    result["函数"].sort(key=lambda f: f["复杂度"], reverse=True)
    return result


def report(root):
    """扫描并打印报告，返回值得重构的处数。"""
    reports = []
    for path in sorted(root.rglob("*.py")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            reports.append(analyze_source(path.read_text(encoding="utf-8"),
                                          str(path)))
        except UnicodeDecodeError:
            continue
    if not reports:
        print(f"{root} 下没找到 .py 文件")
        return 0
    print(f"共 {len(reports)} 个文件、{sum(r['总行数'] for r in reports)} 行、"
          f"{sum(len(r['函数']) for r in reports)} 个函数\n")
    problems = 0
    print(f"【超过 {FILE_LIMIT} 行的文件（建议拆分）】")
    big = [r for r in reports if r["总行数"] > FILE_LIMIT]
    for r in sorted(big, key=lambda x: x["总行数"], reverse=True):
        print(f"  {r['文件']}：{r['总行数']} 行")
    if not big:
        print("  无")
    problems += len(big)

    print("\n【复杂度最高的 5 个函数】")
    all_funcs = [(r["文件"], f) for r in reports for f in r["函数"]]
    for filename, func in sorted(all_funcs, key=lambda x: x[1]["复杂度"],
                                 reverse=True)[:5]:
        flag = (" ← 超标" if func["复杂度"] > COMPLEXITY_LIMIT else "") \
               + (" ← 太长" if func["长度"] > FUNC_LIMIT else "")
        print(f"  复杂度{func['复杂度']:>3}  {func['长度']:>4} 行  "
              f"{func['名字']}()  ({filename}:{func['行号']}){flag}")
        if flag:
            problems += 1
    print(f"\n共 {problems} 处值得重构。先挑「复杂度最高」的那个函数下手。"
          if problems else "\n全部在阈值以内，规模控制得不错。")
    return problems


if __name__ == "__main__":
    report(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("."))
