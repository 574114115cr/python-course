# -*- coding: utf-8 -*-
"""进阶课实测基准：跑 course-fluent/bench.json 里的每个案例，产出 bench/results.json。

设计原则：
  - 案例内容（问题 + 写法 + 结论）在 bench.json，本脚本只负责「公平地跑」；
  - 计时用 timeit 的 best-of-N（取最小值），避开 GC 与系统噪声；
  - 内存案例用 tracemalloc 量峰值，只跑一次；
  - 结果是机器相关的，页面必须显示运行环境；比值（最快 = 1×）才是稳定信号。

用法：
  python tools/bench_fluent.py            # 全量
  python tools/bench_fluent.py u1-listcomp u2-deque   # 只跑指定案例
"""
import datetime
import json
import os
import platform
import sys
import timeit
import tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "course-fluent", "bench.json")
OUT_DIR = os.path.join(ROOT, "bench")
OUT = os.path.join(OUT_DIR, "results.json")

REPEAT = 5          # 每个写法重复 5 轮，取最快的一轮
MEM_REPEAT = 3


def load_cases():
    cases = json.load(open(SRC, encoding="utf-8"))
    for c in cases:
        for v in c["variants"]:
            compile(v["code"], f"<{c['id']}#{v['name']}>", "exec")
        compile(c.get("setup", ""), f"<{c['id']}#setup>", "exec")
    return cases


def time_variant(case, variant):
    """返回 (最短耗时秒, 单次耗时秒)。"""
    number = case.get("number", 1)
    timer = timeit.Timer(stmt=variant["code"], setup=case.get("setup", ""),
                         globals={})
    best = min(timer.repeat(repeat=REPEAT, number=number))
    return best, best / number


def mem_variant(case, variant):
    """返回峰值内存字节（跑一次）。"""
    ns = {}
    exec(case.get("setup", ""), ns)
    tracemalloc.start()
    try:
        exec(variant["code"], ns)
        _cur, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak


def run(cases, only=None):
    results = []
    for c in cases:
        if only and c["id"] not in only:
            continue
        print(f"· {c['id']}  {c['q']}")
        vs = []
        for v in c["variants"]:
            best, per = time_variant(c, v)
            row = {"name": v["name"], "best": round(best, 6),
                   "per": round(per, 9), "mem": None}
            if c.get("mem"):
                peaks = [mem_variant(c, v) for _ in range(MEM_REPEAT)]
                row["mem"] = max(peaks)
            vs.append(row)
            mem_txt = (f"  峰值 {row['mem'] / 1048576:.2f} MB"
                       if row["mem"] is not None else "")
            print(f"    {v['name']:<14} {per * 1000:9.3f} ms/次{mem_txt}")
        fastest = min(v["per"] for v in vs)
        for v in vs:
            v["ratio"] = round(v["per"] / fastest, 2) if fastest else None
        results.append({
            "id": c["id"], "unit": c["unit"], "q": c["q"],
            "note": c["note"], "mem": bool(c.get("mem")),
            "number": c.get("number", 1), "variants": vs,
        })
    return results


def env():
    return {
        "python": sys.version.split()[0],
        "impl": platform.python_implementation(),
        "machine": platform.machine(),
        "system": platform.system() + " " + platform.release(),
        "cpu": platform.processor() or "unknown",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def main():
    only = set(sys.argv[1:]) or None
    cases = load_cases()
    results = run(cases, only)
    os.makedirs(OUT_DIR, exist_ok=True)
    data = {"env": env(), "method": {
        "timer": "timeit.Timer.repeat",
        "repeat": REPEAT,
        "pick": "取最快一轮（best-of-N），避开 GC 与调度噪声",
        "mem": "tracemalloc 峰值，跑 3 次取最大",
    }, "cases": results}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    print(f"\n写出 {OUT}（{len(results)} 个案例）")
    print("环境：", " | ".join(f"{k}={v}" for k, v in env().items()))


if __name__ == "__main__":
    main()
