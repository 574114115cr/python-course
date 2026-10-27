"""一次性生成进阶课的「总课表」页素材（由 build_fluent.py 调用）。

放在这里是为了把「周次 / 配速 / 检查点」这些规划信息集中一处，
不和渲染逻辑混在一个 3000 行的构建器里。
"""

import html
import re

PHASES = [
    (1, 4, "语言地基",
     "数据模型、序列家族、字典与文本、数据类、一等函数与类型提示。"
     "这一段决定你后面读源码时能不能看懂「为什么这行没写 if」。"),
    (5, 8, "协议与类型",
     "装饰器与闭包、对象协议与序列实现、接口继承与 ABC/Protocol、运算符重载与类型进阶。"
     "这一段是「从会写变成写得像库」的分水岭。"),
    (9, 12, "并发与元编程",
     "迭代器与生成器、线程与进程、asyncio、动态属性与描述符、类元编程。"
     "这一段最难，也最容易被跳过，所以要配走读与实测一起看。"),
]

STOP_RULES = [
    ("题库正确率 &lt; 60%", "不要进下一单元。回本单元讲义重读「关键点」，把错的题抄进笔记再重做一遍。"),
    ("走读程序跑不通", "不要看答案。先只看 traceback 最后一行，定位到具体行，再对照「逐段走读」里对应的那一段。"),
    ("合上讲义讲不出 3 个关键点", "说明只是「看过」不是「学过」。回到复习计划，先做当天复盘那一轮。"),
    ("连续两周完不成计划", "把配速从标准切到轻量（每周 3–4 小时），不要靠熬夜补。计划必须能持续。"),
]


# 单元权重（标准配速下占几周）。11/12 是并发与元编程，4 节撑不满：
# 单元 11 多一个事件循环心智模型，单元 12 有描述符 + 元类两块硬骨头。
WEIGHT = {11: 2, 12: 2}


def week_table(units, pace):
    """按权重累加周次。pace='std' 权重即周数；'light' 翻倍。返回 ({unit: 起止周}, 总周数)。"""
    out, w = {}, 0
    for u in units:
        span = WEIGHT.get(u["no"], 1) * (2 if pace == "light" else 1)
        out[u["no"]] = (w + 1, w + span)
        w += span
    return out, w


def totals(units):
    """两种配速的总周数（标题里要用，别写死 12/24）。"""
    _, a = week_table(units, "std")
    _, b = week_table(units, "light")
    return a, b


def build_body(units, bookmap):
    std, total_weeks_std = week_table(units, "std")
    light, total_weeks_light = week_table(units, "light")

    phase_map = {}
    for lo, hi, name, desc in PHASES:
        for n in range(lo, hi + 1):
            phase_map[n] = (name, desc, lo, hi)

    rows = []
    for u in units:
        n = u["no"]
        chs = []
        for L in u["lessons"]:
            g = (n - 1) * 4 + L["local"]
            book = (bookmap.get(str(g)) or {}).get("book", "")
            for ch in re.findall(r"第\s*(\d+)\s*章", book):
                if ch not in chs:
                    chs.append(ch)
        ch_txt = "、".join(f"第 {c} 章" for c in chs) or "—"
        s0, s1 = std[n]
        l0, l1 = light[n]
        wk_std = f"第 {s0} 周" if s0 == s1 else f"第 {s0}–{s1} 周"
        wk_light = f"第 {l0}–{l1} 周"
        gate = ""
        if n == 6:
            gate = '<span class="tag">关卡 1</span>'
        elif n == 12:
            gate = '<span class="tag">关卡 2</span>'
        rows.append(
            f"<tr><td><b>{n:02d}</b></td>"
            f"<td><a href='{n:02d}.html'>{html.escape(u['title'])}</a>"
            f"{('<br>' + gate) if gate else ''}</td>"
            f"<td class='s'>{ch_txt}</td>"
            f"<td class='n'>{wk_std}</td><td class='n'>{wk_light}</td>"
            f"<td class='s'>走读 u{n:02d} 跑通 · 综合案例改一版 · 题库 {n} 三题全对</td></tr>")

    phase_cards = []
    for lo, hi, name, desc in PHASES:
        n_lessons = (hi - lo + 1) * 4
        phase_cards.append(
            f'<div class="cb"><b>{name} · 单元 {lo}–{hi}</b>'
            f'<p>{html.escape(desc)}</p>'
            f'<p style="margin-top:8px;font-size:12px;color:var(--muted)">'
            f'标准第 {std[lo][0]}–{std[hi][1]} 周 · 轻量第 {light[lo][0]}–{light[hi][1]} 周 · '
            f'{n_lessons} 节 · 约 {n_lessons * 1.5:.0f} 小时</p></div>')

    stop_rows = "".join(
        f"<tr><td class='w'>{cond}</td><td>{html.escape(action)}</td></tr>"
        for cond, action in STOP_RULES)

    n_hours = len(units) * 4 * 1.5
    return f"""<div class="wrap">
  <div class="hero" style="padding:38px 40px">
    <div class="bdg">SYLLABUS · 总课表</div>
    <h1>{len(units)} 个单元，两种配速</h1>
    <p><b>标准 {total_weeks_std} 周</b>：每周 1 个单元（4 节 × 90 分钟 + 复习 1 小时，约 7 小时），
       单元 11–12 各占 2 周。<b>轻量 {total_weeks_light} 周</b>：每单元 2 周、单元 11–12 各 4 周
       （每周 3–4 小时）。两条路的<b>内容和检查点完全相同</b>，只差周次——
       先选能坚持的那条，再谈进度。</p>
    <div class="st">
      <div><b>{len(units)}</b><span>单元</span></div>
      <div><b>{len(units) * 4}</b><span>节课</span></div>
      <div><b>{n_hours:.0f}</b><span>课堂小时</span></div>
      <div><b>2</b><span>关卡</span></div>
    </div>
  </div>

  <h2>三个阶段</h2>
  <p class="sub">阶段不是装饰：每一段结束都有一个明确的能力门槛，过不了就别进下一段。</p>
  <div class="grid">{''.join(phase_cards)}</div>

  <h2>每周怎么排</h2>
  <p class="sub">按「90 分钟一节」排，一次只上一节。四节不要挤在一天——中间那几天是留给复习的。</p>
  <div class="tblwrap"><table>
    <thead><tr><th>时间</th><th>做什么</th><th>时长</th><th>完成标准</th></tr></thead>
    <tbody>
      <tr><td>第 1 次</td><td>本单元第 1–2 节：读讲义 → 跑代码 → 做「动手」</td><td>3 h</td>
        <td>两节的验收清单能全部勾上</td></tr>
      <tr><td>第 2 次</td><td>本单元第 3–4 节 + 综合案例</td><td>3 h</td>
        <td>综合案例能按自己的场景改一版并跑通</td></tr>
      <tr><td>第 3 次</td><td>题库 3 题 + 走读程序 + <a href="review.html">复习计划</a>当天那轮</td>
        <td>1 h</td><td>3 题独立做对；走读程序不参考原文能跑通</td></tr>
      <tr><td>每天 15 分钟</td><td>复习计划里今日到期的条目（含逾期）</td><td>0.5 h / 周</td>
        <td>今日条目清零，逾期不超过 1 轮</td></tr>
    </tbody>
  </table></div>

  <h2>逐单元周次</h2>
  <p class="sub">「产出」一列就是这一单元的过关标准，做不到就不算学完——不要用「看完了」当完成。</p>
  <div class="tblwrap"><table>
    <thead><tr><th>单元</th><th>标题</th><th>教材</th><th>标准</th><th>轻量</th><th>本单元产出</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>

  <h2>什么时候该停下来</h2>
  <p class="sub">以下四条是硬规则，触发任意一条就停，不要「先往下学，回头再补」——回头基本不会补。</p>
  <div class="tblwrap"><table>
    <thead><tr><th>信号</th><th>处理</th></tr></thead>
    <tbody>{stop_rows}</tbody>
  </table></div>

  <h2>时间不够时的删减顺序</h2>
  <div class="grid">
    <div class="cb"><b>先砍：设计长文 24 章</b>
      <p>它是「为什么这样设计」的纵深阅读，第一遍可以只挑与本单元相关的 1–2 篇。
      不影响动手能力，但会少一层判断力。</p></div>
    <div class="cb"><b>再砍：实测页</b>
      <p><a href="bench.html">实测</a>是给你「别信口口相传」的证据，第一遍可以只看结论表。
      做优化时再回来读方法和数据。</p></div>
    <div class="cb"><b>不能砍：走读 + 题库 + 关卡</b>
      <p>走读是唯一让你「完整读一个能跑的程序」的地方；题库暴露你以为会了其实不会；
      关卡是阶段门槛。这三样砍了，这门课就退化成读文章。</p></div>
  </div>

  <h2>两种配速怎么选</h2>
  <div class="grid">
    <div class="cb"><b>选标准 {total_weeks_std} 周，如果</b>
      <p>每周能稳定拿出 6–8 小时，且已经能用 Python 写 100 行左右的脚本。
      这是默认路线，也是和入门课（约 29 周、每周 6–8 小时）节奏一致的那条；
      总课时 48 节 × 1.5 h ≈ 72 h，摊到 {total_weeks_std} 周约 5 h/周，留 2 h 给练习与复习。</p></div>
    <div class="cb"><b>选轻量 {total_weeks_light} 周，如果</b>
      <p>在工作日只能挤出 30–60 分钟。把「每周 1 单元」拆成「每两周 1 单元」，
      周内节奏不变，只是间隔拉长——复习轮次会自动跟着你的完成时间排，不用手动改。</p></div>
  </div>

  <p style="margin-top:26px;font-size:12.5px;color:var(--muted)">
    <a href="../index.html">课程首页</a> ·
    <a href="lessons/index.html">课程目录</a> ·
    <a href="coverage.html">覆盖与自足性</a> ·
    <a href="review.html">复习计划</a> ·
    <a href="gates.html">关卡验收</a></p>
</div>"""
