# score_analyzer.py —— 综合项目 2：成绩管理分析器
# 设计要点：分析逻辑是纯函数（不碰文件、不碰 input），所以最容易测试

import json
import csv
import os

DATA_FILE = "scores.json"
REPORT_FILE = "report.csv"


# ===== 数据加载 =====
def load_scores(filename=DATA_FILE):
    """读取成绩数据。文件不存在或损坏时返回空列表。"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"找不到文件 {filename}，将使用空数据集")
        return []
    except json.JSONDecodeError:
        print(f"{filename} 不是合法的 JSON 文件")
        return []
    except OSError as error:
        print(f"读取失败：{error}")
        return []

    # 校验每一项：必须有 name，且各科成绩是数字
    valid = []
    for index, item in enumerate(data):
        try:
            record = {
                "name": str(item["name"]),
                "math": float(item["math"]),
                "english": float(item["english"]),
            }
            valid.append(record)
        except (KeyError, TypeError, ValueError):
            print(f"  第 {index + 1} 条数据格式有误，已跳过")
    return valid


# ===== 纯函数：所有分析逻辑都在这里 =====
def subject_stats(scores, subject):
    """返回某科目的平均分、最高分、最低分。

    subject: "math" 或 "english"
    """
    values = [s[subject] for s in scores]
    if not values:
        return {"平均分": 0.0, "最高分": 0.0, "最低分": 0.0, "人数": 0}
    return {
        "平均分": sum(values) / len(values),
        "最高分": max(values),
        "最低分": min(values),
        "人数": len(values),
    }


def add_total(scores):
    """返回带总分字段的成绩列表（不修改入参）。"""
    return [
        {**s, "total": s["math"] + s["english"]}
        for s in scores
    ]


def ranking(scores):
    """总分排名榜（降序）。"""
    with_total = add_total(scores)
    return sorted(with_total, key=lambda s: s["total"], reverse=True)


def subject_toppers(scores, subject):
    """某科目的第一名（并列时返回全部）。"""
    if not scores:
        return []
    best = max(s[subject] for s in scores)
    return [s["name"] for s in scores if s[subject] == best]


def failed_students(scores, pass_line=60):
    """需要补考的学生（任一科 < 60）。"""
    failed = []
    for s in scores:
        subjects = [name for name in ("math", "english") if s[name] < pass_line]
        if subjects:
            failed.append({
                "name": s["name"],
                "failed_subjects": subjects,
            })
    return failed


def class_overview(scores):
    """班级总览。"""
    if not scores:
        return {"人数": 0, "班级平均总分": 0.0}
    with_total = add_total(scores)
    return {
        "人数": len(scores),
        "班级平均总分": sum(s["total"] for s in with_total) / len(scores),
        "最高总分": max(s["total"] for s in with_total),
        "最低总分": min(s["total"] for s in with_total),
    }


# ===== 报告导出 =====
def export_report(scores, filename=REPORT_FILE):
    """把排名导出为 CSV。"""
    try:
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["排名", "姓名", "数学", "英语", "总分"])
            for rank, s in enumerate(ranking(scores), 1):
                writer.writerow([
                    rank, s["name"], s["math"], s["english"], s["total"],
                ])
        print(f"报告已导出到 {filename}")
        return True
    except Exception as error:
        print(f"导出失败：{error}")
        return False


def generate_sample_data(filename=DATA_FILE):
    """生成一份示例数据，方便演示。"""
    data = [
        {"name": "小明", "math": 92, "english": 88},
        {"name": "小红", "math": 78, "english": 95},
        {"name": "小刚", "math": 65, "english": 72},
        {"name": "小丽", "math": 88, "english": 91},
        {"name": "小强", "math": 55, "english": 48},
        {"name": "小美", "math": 100, "english": 97},
    ]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已生成示例数据：{filename}")
    return data


# ===== 主流程 =====
def main():
    print("=" * 50)
    print("成绩管理分析器")
    print("=" * 50)

    scores = load_scores()

    if not scores:
        print("\n没有可分析的数据。")
        generate_sample_data()
        scores = load_scores()

    while True:
        print("\n1. 班级总览")
        print("2. 各科统计")
        print("3. 总分排名")
        print("4. 单科第一名")
        print("5. 补考名单")
        print("6. 导出 CSV 报告")
        print("0. 退出")

        choice = input("请选择：").strip()

        try:
            if choice == "1":
                print("\n--- 班级总览 ---")
                for key, value in class_overview(scores).items():
                    print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")

            elif choice == "2":
                print("\n--- 各科统计 ---")
                for subject, cn in [("math", "数学"), ("english", "英语")]:
                    stats = subject_stats(scores, subject)
                    print(f"  {cn}：平均 {stats['平均分']:.2f}，"
                          f"最高 {stats['最高分']:.1f}，"
                          f"最低 {stats['最低分']:.1f}")

            elif choice == "3":
                print("\n--- 总分排名 ---")
                print(f"  {'排名':<6}{'姓名':<10}{'总分':>8}")
                for rank, s in enumerate(ranking(scores), 1):
                    print(f"  {rank:<6}{s['name']:<10}{s['total']:>8.1f}")

            elif choice == "4":
                print("\n--- 单科第一名 ---")
                for subject, cn in [("math", "数学"), ("english", "英语")]:
                    toppers = subject_toppers(scores, subject)
                    print(f"  {cn}：{'、'.join(toppers) if toppers else '无'}")

            elif choice == "5":
                print("\n--- 补考名单（低于 60 分）---")
                failed = failed_students(scores)
                if not failed:
                    print("  全员通过！")
                for item in failed:
                    print(f"  {item['name']}：{'、'.join(item['failed_subjects'])}")

            elif choice == "6":
                export_report(scores)

            elif choice == "0":
                print("再见！")
                break
            else:
                print("无效选项")

        except KeyboardInterrupt:
            print("\n正在退出...")
            break
        except Exception as error:
            print(f"发生错误：{error}")


if __name__ == "__main__":
    main()
