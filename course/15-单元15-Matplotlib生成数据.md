# 单元 15：Matplotlib 生成数据

> 对应教材第 15 章「生成数据」
> 阶段 2 · 项目 2：数据可视化
> 本单元目标：**用代码生成数据并画出第一张图——既会用 Matplotlib 存静态图，也知道什么时候该换成可交互的 Plotly**

---

## 一、学习目标

完成本单元后，你应该能够：

1. 说清 Matplotlib 和 Plotly 的分工：什么时候要静态 PNG，什么时候要可交互 HTML，并据此选库。
2. 用推荐写法 `fig, ax = plt.subplots()` 建图，并解释它为什么优于 `plt.plot()` 那种过程式写法。
3. 画折线图并调细节：`linewidth=` 加粗、`labels=`、`title=`、`plt.style.use()` 换内置样式。
4. 用 `scatter()` 画散点图，并同时用上 `s=`（点大小）、`c=`（颜色）、`cmap=`（颜色映射）三件套。
5. **用 `ax.axis([xmin, xmax, ymin, ymax])` 给坐标轴留边距**，不让点贴在边框上被裁掉，并用 `set_xticks()` / `set_xticklabels()` 定制刻度。
6. 写出 `RandomWalk` 类，理解 `fill_walk()` 里「拒绝原地不动」为什么必须写 `and` 而不是 `or`，会用 `random.seed()` 让结果可复现。
7. 写出 `Die` 类用 Plotly 模拟掷骰子，用 `results.count(value)` 统计频次、`px.bar()` 画分布图，并解释两个面数不同的骰子叠加后分布为什么更均匀。

---

## 二、核心知识点讲解

### 2.1 选型：静态图还是交互图

写下第一行 `import` 前先答：**这张图给谁看？**

| 场景 | 用什么 | 为什么 |
|---|---|---|
| 写进报告、论文，要能打印 | **matplotlib** | 存成 PNG，像素确定，到处能贴 |
| 发给同事，想拖动、悬停看数值 | **Plotly** | 存成 HTML，浏览器里能交互 |
| 做网站前端图表 | **Plotly** | 自带 JS，鼠标一动有反馈 |

类比：**matplotlib 像印在纸上的图**——定稿不变、能复印；**Plotly 像挂墙的电子展板**——观众能凑近看，但要通电和场地。

**安装**：

```bash
pip install matplotlib plotly
```

**★ 无图形界面的环境怎么办。** 服务器、WSL、某些 IDE 里没屏幕，`plt.show()` 会报 `UserWarning: Matplotlib is currently using agg`，或让程序挂住。本讲义示例统一用 `fig.savefig("xx.png")` 存文件。若连保存也要静默，在**导入 pyplot 之前**加 `matplotlib.use("Agg")`（教材未涉及，补充），写反会报错。

### 2.2 面向对象：`fig, ax = plt.subplots()` ★

教材先带你写「过程式」老写法：`plt.plot(input_values, output_values)`，所有东西都往**全局的 `plt`** 上挂。它能跑，但画三张图时标题互相覆盖、图互相顶掉，你得不停 `plt.figure()`、`plt.subplot()`。面向对象写法把「图」和「坐标轴」分成两个对象：

```text
fig（图 / figure）——整张画布：多个子图、整体标题、存盘
 └── ax（坐标轴 / axes）——一块绘图区：画线、设标题、设刻度
```

类比：**fig 是画板，ax 是画板上贴好的一张白纸**。

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()                  # 拿一块画板 + 一张纸
ax.plot([1, 2, 3], [1, 4, 9])             # 在纸上画
ax.set_title("第一个面向对象图")
fig.savefig("oo_第一张图.png", dpi=100, bbox_inches="tight")
```

中间的逗号叫**解包**：函数返回元组 `(figure, axes)`，一句话拆成两个变量。`ax` 是官方推荐的名字（`axes` 的缩写），全世界教程都在用。

### 2.3 折线图细节：线宽、标签、样式

| 参数 | 作用 | 例子 |
|---|---|---|
| `linewidth` / `lw` | 线条粗细（单位是「点」不是像素） | `lw=3` |
| `linestyle` / `ls` | 线型 | `"--"` 虚线、`":"` 点线 |
| `color` / `c` | 颜色 | `c="red"`、`c="#1f77b4"` |
| `marker` | 数据点形状 | `marker="o"` |
| `alpha` | 透明度 0~1 | `alpha=0.5` |
| `label` | 图例用的名字 | `label="实际值"` |

**内置样式**一行换肤：先 `print(plt.style.available)` 看有哪些，再 `plt.style.use("seaborn-v0_8")`。

> **版本坑（教材未涉及，补充）**：matplotlib 0.13 之后 seaborn 系列样式名都带版本后缀，要写 `"seaborn-v0_8"` 而不是 `"seaborn"`，否则抛 `ValueError: style 'seaborn' is not in the list of available styles`。而 `"ggplot"`、`"bmh"` 这些老名字仍然有效。样式只是皮肤，删掉不影响结果。

**★ `figsize` 与 `dpi`**：清晰度靠 `dpi`，物理尺寸靠 `figsize`（英寸）。想插一张不糊的图，两个一起加：`subplots(figsize=(12, 8))` 配 `savefig(..., dpi=200)`。
### 2.4 散点图三件套：s=、c=、cmap=

折线图适合**有先后顺序**的数据，散点图适合**两个量的关系**。**★ 三件套是三个独立通道**：

```text
散点图 = 点在哪（x, y）
       + 点多大（s=）      ← 第三个维度：数量级
       + 点什么色（c=）    ← 第四个维度：类别或数值
```

- `s=`（size）控制**面积**，单位是「点」。教材里 `s=x_values * 2` 就是为了看得清。
- `c=`（color）可以传**颜色名字**（分类），也可以传**数值**（必须配 `cmap=`）。
- `cmap=`（color map）规定「数值怎么翻译成颜色」，最常用 `plt.cm.Blues`——值小则浅，值大则深。

「绘制一系列点」就是把两组数据画在同一张 `ax` 上（见示例 2），两种颜色叠着，一眼看出「谁增长得快」。

传**颜色名字**和传**数值**是两套机制：前者是「每点自己指定颜色」，后者是「让 matplotlib 按数值自动上色，并自动多一条颜色条」。初学最容易混的就是这个——`c` 里传数字却不给 `cmap`，所有点会变成同一种默认颜色，**不报错**，但你以为的渐变根本没出现。

### 2.5 ★ 校正绘图：给坐标轴留边距

这是新手最高频的坑，值得单独一节。默认坐标轴范围**贴着数据**：x 轴从最小值到最大值。但点本身有「直径」——`s=100` 的点不是没有面积的一个点，而画布边框会**切掉越界部分**，于是两端点被削掉一小块，看着像「数据缺了一头」。

**解决办法是手动指定范围**：`ax.axis([0, 1100, 0, 1_100_000])`，四个数顺序是 `[xmin, xmax, ymin, ymax]`。为什么写 1100 和 1 100 000 这种「多出来的数」？因为数据最大值正好是它们，**再留一点余量**，点才不被切。110 万写作 `1_100_000`（下划线只分组）。

```text
没校正                  校正之后（四周加了余量）
┌──────────────┐      ┌──────────────┐
│◐   ○ ○ ○   ◑ │  →   │  ◐ ○ ○ ○ ◑  │
│ ◐ ○ ○ ○ ○ ◑  │      │  ○ ○ ○ ○ ○ ○  │
└──────────────┘      └──────────────┘
 ↑ 贴边的点被削掉了      ↑ 点完整，四周留白
```

`ax.axis([...])` 这名字很怪——它既设范围又管外观。等价写法是 `ax.set_xlim()` + `ax.set_ylim()`，更直白。**关键是要知道为什么要手动设范围**；更稳的做法是用 `max(数据) * 1.05` 算余量，数据换了也不用改代码（见示例 3）。

**定制刻度标记。** 默认刻度由 matplotlib 自选，大数字上会变成 `1.0e6` 科学计数法，或标签挤成一团。`set_xticks()` 是「**刻度放在这些位置**」，`set_xticklabels()` 是「**这些位置显示什么**」（见示例 3）。

**★ `set_xticks` 与 `set_xticklabels` 必须配套调用。** 只调后者，标签会被硬贴在默认刻度上，位置不够就叠。

**★ 自动保存绘图**用 `fig.savefig()`，推荐写全两个参数：`dpi=200` 让线更细腻，`bbox_inches="tight"` 表示「**按有内容区域裁剪**」，不写就带大片白边。

### 2.6 随机游走：RandomWalk 类

**随机游走**是最简单的随机模型：一只小虫每次随机往一个方向走一步，走一千步得到一条弯曲路径。它是布朗运动、股票涨跌、扩散的数学原型。教材把它做成一个类，这个设计比代码更值得学——**「一只虫」是一个对象，`x`、`y` 是属性，「走一步」是方法**（类见示例 4）：

```python
class RandomWalk:
    def __init__(self, num_points=5000):
        self.num_points = num_points          # 属性：走多少步
        self.x_values = [0]                   # 属性：从原点出发
        self.y_values = [0]

    def fill_walk(self):
        while len(self.x_values) < self.num_points:
            x_step = random.choice([-1, 0, 1])
            y_step = random.choice([-1, 0, 1])
            if x_step == 0 and y_step == 0:
                continue                      # ★ 拒绝原地不动
            self.x_values.append(self.x_values[-1] + x_step)
            self.y_values.append(self.y_values[-1] + y_step)
```

**★ 这里最容易错：为什么要「拒绝原地不动」？** 若允许 x 和 y 同时不变，这轮什么也没发生。四种组合里「不动」占 1/4，5000 步里约 1250 步原地踏步。**这违反了随机游走「每一步都要真的移动」的定义。** 正确写法是两个**同时**为 0 才重来——所以用 `and`，不是 `or`。

`random.choice(seq)` 是「**从序列里随机挑一个**」，兄弟还有 `random.randint(a, b)`（含两端）、`random.random()`（0~1）。
**★ `random.seed(42)` 是这一章最有工程价值的一行。** 随机性是编程里的「double 难度 bug 源」：跑一遍正常、再跑一遍崩，而你复现不出来。写上种子后**随机序列完全可复现**，bug 能稳定复现、修好、再验证。**调试随机程序第一件事就是加种子。**

模拟多次随机游走就是循环创建多个对象（完整代码见示例 4），有三点值得说：`alpha=0.1` 让 500 条半透明路径叠在一起、**经过次数多的区域自然变深**（不透明会糊成一坨纯黑）；`edgecolors="none"` 是点太多时不要描边；`c=[i] * len(...)` 配 `cmap=plt.cm.Blues` 让**「第几次游走」变成深浅**（`c` 必须和点一样长）。

### 2.7 Plotly 掷骰子：Die 类

前面全是 matplotlib，从这里换成 Plotly，因为掷骰子的本质是「大量样本的**分布**」，Plotly 的 `bar` 一行出图还自带交互。**选库看需求，不看时髦程度**——要把这张图印进 PDF 的话，matplotlib 一样能画。

```bash
pip install plotly kaleido      # kaleido 只在导出 PNG/SVG 时需要
```

> `kaleido` 是 Plotly 静态导出的引擎，教材存 HTML 用不到它；本讲义统一用 `fig.write_html()`。

**`Die` 类的设计**：骰子是「能被掷的对象」，该有的是——**面数（属性）**、**记住每次结果（属性）**、**掷一次（方法）**：

```python
import random

class Die:
    """一枚 n 面骰子。"""

    def __init__(self, num_sides=6):
        self.num_sides = num_sides
        self.results = []              # 存每一次掷出的点数

    def roll(self):
        result = random.randint(1, self.num_sides)   # 含两端
        self.results.append(result)
```

**★ `results.count(value)` 是本节的关键一招。** 想知道「1 点出现了多少次」，最笨是手写循环去数；`list` 自带 `count()`，一行返回出现次数（见示例 5）。统计完还要加 `assert sum(frequencies) == len(die.results)`：这不是装饰——分布类程序最容易出的 bug 是「某个类别被漏掉了」，而它不报错、只让你看到缺一列的图。

**画分布图。** `px.bar()` 需要横纵两组数据；定制用 `fig.update_layout()`（改整体：标题、轴标题）和 `fig.update_traces()`（改柱子：颜色、描边）；还可以用 `fig.add_hline()` 画「理论平均线」，让读者一眼看出随机结果靠不靠谱。

> **★ 术语纠正**：中文常把这种图叫「直方图」（histogram），但 `px.bar()` 画的是**柱状图**。真正的直方图（`px.histogram`）是把**连续数值分箱**——比如把身高分成 160~170、170~180 两堆。骰子点数是**离散类别**，所以用 `bar`。

**同时掷两个骰子**，建两个对象、掷同样多次后**把结果相加**（2 到 12 共 11 种），核心就一行列表推导：

```python
import random

random.seed(42)
rolls_1 = [random.randint(1, 6) for _ in range(1000)]   # 骰子 1 的 1000 次
rolls_2 = [random.randint(1, 6) for _ in range(1000)]   # 骰子 2 的 1000 次
sums = [a + b for a, b in zip(rolls_1, rolls_2)]       # zip 把两串配对
frequencies = [sums.count(v) for v in range(2, 13)]     # 2~12 共 11 种
print(dict(zip(range(2, 13), frequencies)))
```

`zip(a, b)` 把两条等长列表「拉链」起来，一次给你一对元素，`for a, b in ...` 再把这一对拆成两个名字。**这个 `zip + 解包` 后面「两份数据逐行对照」都会用到**，务必练熟。

**同时掷两个面数不同的骰子**，用 `plotly.graph_objects` 显式画两组柱子（见示例 5）。`go.Figure() + add_trace()` 比 `px.bar()` 啰嗦，但控制力强：能画多条配置的柱子、能命名、能设透明度。`barmode="group"` 是**并排**，`"overlay"` 是**叠放**（记得配 `opacity`）。

**统计结论（比代码更重要）**：每次掷骰子各点数**等概率**，所以单个骰子的分布是**平的**。两个骰子相加时，**靠中间的点有更多组合方式凑出来**（六面+六面凑 7 有 6 种组合，凑 2 只有 1 种），分布向中间隆起；**面数越多分布越均匀**（六面+二十面有 120 种组合，几乎平坦）。这就是「大数压倒小数」。

**保存图形**——两个库不一样：matplotlib 存静态图用 `fig.savefig("x.png", bbox_inches="tight")`；Plotly 存可交互网页用 `fig.write_html("x.html")`，需要静态图（且装了 kaleido）用 `fig.write_image("x.png")`。

---

## 三、可运行代码示例

### 示例 1：折线图三连（默认 → 加粗改标签 → 换内置样式）

```python
# line_demo.py —— 折线图三连
# 跑完可以删掉生成的 png 文件

import matplotlib.pyplot as plt

input_values = [1, 2, 3, 4]
output_values = [1, 4, 9, 16]

# ===== 1. 最朴素的一张折线图（对照老写法 plt.plot）=====
fig, ax = plt.subplots()
ax.plot(input_values, output_values)
ax.set_title("朴素版")
fig.savefig("line_1_朴素版.png", dpi=100, bbox_inches="tight")
print("可用样式：", plt.style.available[:8], "...")

# ===== 2. 改线宽、改标签文字 =====
plt.style.use("seaborn-v0_8")                    # 先换皮肤
fig, ax = plt.subplots()
ax.plot(input_values, output_values, linewidth=3)   # lw=3 让线明显变粗
ax.set_title("折线图：平方增长", fontsize=16)
ax.set_xlabel("输入值", fontsize=12)
ax.set_ylabel("输出值", fontsize=12)
ax.set_xticks(input_values)
ax.set_yticks(output_values)
ax.grid(True)                                   # 网格线，方便读数
fig.savefig("line_2_加粗版.png", dpi=100, bbox_inches="tight")

# ===== 3. 换皮肤再画一张（matplotlib 自带的 bmh 样式）=====
plt.style.use("bmh")
fig, ax = plt.subplots()
ax.plot(input_values, output_values, marker="o", linewidth=2, color="tomato")
ax.set_title("折线图：换个皮肤")
fig.savefig("line_3_换皮肤版.png", dpi=100, bbox_inches="tight")
print("三张图都已保存")
```

### 示例 2：散点图三件套 + 绘制一系列点

```python
# scatter_demo.py —— s= / c= / cmap= 三件套
# 跑完可以删掉生成的 png 文件

import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8")

x_values = [1, 2, 3, 4, 5]
y_values = [1, 4, 9, 16, 25]

# ===== 1. 基础散点图：位置 = 两个列表 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=100)                 # s=100：点大小
fig.savefig("scatter_1_基础.png", dpi=100, bbox_inches="tight")

# ===== 2. 三件套同时上场 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values,
           s=[v * 30 for v in x_values],                # 点大小随 x 变化
           c=y_values,                                  # 颜色由 y 值决定
           cmap=plt.cm.Blues,                           # Blues 这套渐变色
           edgecolors="gray")                           # 灰边让点更清楚
fig.savefig("scatter_2_三件套.png", dpi=100, bbox_inches="tight")

# ===== 3. 绘制一系列点：传颜色名字 = 分类上色 =====
years = list(range(2010, 2021))
program_a = [10, 18, 26, 35, 47, 58, 70, 82, 95, 105, 118]   # 增长快
program_b = [10, 12, 15, 18, 21, 23, 26, 28, 30, 33, 35]    # 增长慢

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(years, program_a, s=60, c="red", label="方案 A", alpha=0.7)
ax.scatter(years, program_b, s=60, c="blue", label="方案 B", alpha=0.7)
ax.set_title("两个方案的用户增长对比")
ax.set_xlabel("年份")
ax.set_ylabel("用户数（万）")
ax.legend()                                            # 图例靠 label 自动生成
fig.savefig("scatter_3_两个系列.png", dpi=100, bbox_inches="tight")
print("三张散点图都已保存")
```

### 示例 3：★ 校正绘图与定制刻度（新手最高频的坑）

```python
# axis_fix_demo.py —— ax.axis([xmin, xmax, ymin, ymax]) 留边距
# 跑完可以删掉生成的 png 文件

import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8")

# ===== 1. 造数据：100 个点，最大值正好是 1100 / 1_100_000 =====
x_values = list(range(1, 101))
y_values = [x * 11000 for x in x_values]        # 100 * 11000 = 1_100_000

# ===== 2. 不校正：最左最右的点会被边框削掉 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=40, c=y_values, cmap=plt.cm.Blues)
ax.set_title("没有校正：边上的点被切了")
fig.savefig("axis_1_没校正.png", dpi=100, bbox_inches="tight")

# ===== 3. 校正：手工指定四个边界，多留 5% 余量 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=40, c=y_values, cmap=plt.cm.Blues)
ax.set_title("校正之后：四周有留白，点是完整的")
ax.axis([0, 1100, 0, 1_100_000])   # 顺序是 [xmin, xmax, ymin, ymax]
fig.savefig("axis_2_校正.png", dpi=100, bbox_inches="tight")

# ===== 4. 让代码自己算余量，并定制刻度 =====
x_max, y_max = max(x_values), max(y_values)
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=40, c=y_values, cmap=plt.cm.Blues)
ax.axis([0, x_max * 1.05, 0, y_max * 1.05])
ax.set_xticks(list(range(0, 101, 10)))           # 刻度位置
ax.set_xticklabels([str(v) for v in range(0, 101, 10)])   # 刻度文字
ax.set_yticks(list(range(0, 1_100_001, 200_000)))
ax.set_yticklabels([f"{v:,}" for v in range(0, 1_100_001, 200_000)])
ax.set_title("自动边距 + 定制刻度", fontsize=16)
fig.savefig("axis_3_自动边距.png", dpi=100, bbox_inches="tight")
print("三张图都已保存")
```

### 示例 4：`RandomWalk` 类（画一次 + 模拟多次）

```python
# random_walk_demo.py —— 教材 RandomWalk 类：单次轨迹 + 500 次叠加
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt


class RandomWalk:
    """模拟一只小虫的随机游走：每一步往四个方向之一移动一格。"""

    def __init__(self, num_points=5000):
        self.num_points = num_points       # 走多少步
        self.x_values = [0]                # 属性：位置列表，从原点出发
        self.y_values = [0]

    def step(self):
        """走一步，然后在列表末尾追加新位置。"""
        x_step = random.choice([-1, 0, 1])
        y_step = random.choice([-1, 0, 1])
        # ★ and 不是 or：只有"横竖都不动"才重来
        if x_step == 0 and y_step == 0:
            return False
        self.x_values.append(self.x_values[-1] + x_step)
        self.y_values.append(self.y_values[-1] + y_step)
        return True

    def fill_walk(self):
        """反复调用 step，直到攒够 num_points 个点。"""
        while len(self.x_values) < self.num_points:
            self.step()


plt.style.use("seaborn-v0_8")
random.seed(42)        # 固定种子：每次运行结果一样，bug 可复现

# ===== 1. 画一次游走：连线 + 标出终点 =====
walk = RandomWalk(1000)
walk.fill_walk()
print("点数:", len(walk.x_values), " 终点:", walk.x_values[-1], walk.y_values[-1])

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(walk.x_values, walk.y_values, linewidth=1, color="royalblue")   # 连线看轨迹
ax.scatter(walk.x_values[-1], walk.y_values[-1], s=120, c="red", label="终点")
ax.set_title("一次随机游走（1000 步）")
ax.legend()
ax.axis([0, 1000 * 1.05, 0, 1000 * 1.05])       # 校正绘图：留边距
fig.savefig("random_walk_一次.png", dpi=120, bbox_inches="tight")

# ===== 自检：拒绝原地不动之后，实际步数必须刚好等于 num_points =====
assert len(walk.x_values) == 1000, f"点数不对：{len(walk.x_values)}"
print("自检通过：没有原地踏步的浪费")

# ===== 2. 模拟 500 次游走并设置样式 =====
num_walks, num_points = 500, 5000
fig, ax = plt.subplots(figsize=(12, 8))
for i in range(num_walks):
    w = RandomWalk(num_points)
    w.fill_walk()
    # 用「第几次游走」当颜色值：先画的淡、后画的深，形成历史层次
    # 注意 c 必须和点一样长，所以写成 [i] * len(...) 这样的列表
    ax.scatter(w.x_values, w.y_values, s=1,
               c=[i] * len(w.x_values), cmap=plt.cm.Blues,
               alpha=0.1, edgecolors="none")

ax.set_title(f"{num_walks} 次随机游走（每次 {num_points} 步）", fontsize=16)
ax.axis([0, num_points * 1.05, 0, num_points * 1.05])
fig.savefig("random_walk_500.png", dpi=150, bbox_inches="tight")
print("两张图都已保存")
```

### 示例 5：`Die` 类 + 两个骰子 + 两种面数对比

```python
# die_plotly.py —— Plotly 模拟掷骰子（单骰 / 双六面 / 六面+二十面）
# 跑完可以删掉生成的 html 文件

import random

import plotly.express as px
import plotly.graph_objects as go


class Die:
    """一枚 n 面骰子，results 记住每一次的点数。"""

    def __init__(self, num_sides=6):
        self.num_sides = num_sides
        self.results = []

    def roll(self):
        result = random.randint(1, self.num_sides)   # 含 1 和 num_sides 两端
        self.results.append(result)


random.seed(42)

# ===== 1. 单个六面骰：results.count() 数频次 =====
die = Die()
for _ in range(1000):
    die.roll()

x_values = [str(v) for v in range(1, die.num_sides + 1)]
y_values = [die.results.count(v) for v in range(1, die.num_sides + 1)]
print("点数:", x_values, "次数:", y_values)

# ★ 自检：频次之和必须等于总投掷次数，否则说明漏统计了某个类别
assert sum(y_values) == len(die.results), "频次对不上，肯定漏了一个类别"

fig = px.bar(x=x_values, y=y_values, labels={"y": "出现次数"})
fig.update_layout(title="掷 1000 次六面骰子的点数分布", xaxis_title="骰子点数")
fig.update_traces(marker_color="royalblue", marker_line_color="black")
fig.add_hline(y=len(die.results) / die.num_sides, line_dash="dash", line_color="red",
              annotation_text="理论平均")
fig.write_html("die_六面.html")

# ===== 2. 两个六面骰：zip 把两条列表拉链配对，列表推导逐对相加 =====
d1, d2 = Die(), Die()
for _ in range(1000):
    d1.roll()
    d2.roll()

sums = [a + b for a, b in zip(d1.results, d2.results)]
freq = [sums.count(v) for v in range(2, 13)]          # 2~12 共 11 种
assert sum(freq) == len(sums), "点数和统计对不上"
print("点数和频次:", dict(zip(range(2, 13), freq)))

fig2 = px.bar(x=list(range(2, 13)), y=freq, labels={"x": "点数和", "y": "出现次数"})
fig2.update_layout(title="掷两个六面骰子 1000 次：点数和分布（钟形）")
fig2.update_traces(marker_color="royalblue", marker_line_color="black")
fig2.add_hline(y=len(sums) / 11, line_dash="dash", line_color="red",
               annotation_text="理论平均")
fig2.write_html("die_两个六面.html")

# ===== 3. 两个面数不同的骰子：六面 vs 二十面（graph_objects 画两组柱子）=====
d6, d20 = Die(6), Die(20)
for _ in range(2000):
    d6.roll()
    d20.roll()

fig3 = go.Figure()
fig3.add_trace(go.Bar(x=list(range(1, 21)),
                      y=[d6.results.count(v) / len(d6.results) for v in range(1, 21)],
                      name="六面骰子", marker_color="royalblue", opacity=0.8))
fig3.add_trace(go.Bar(x=list(range(1, 21)),
                      y=[d20.results.count(v) / len(d20.results) for v in range(1, 21)],
                      name="二十面骰子", marker_color="tomato", opacity=0.8))
fig3.update_layout(barmode="group",
                   title="六面 vs 二十面：面数越多，分布越平（2000 次）",
                   xaxis_title="点数", yaxis_title="频率")
fig3.write_html("die_六面vs二十面.html")
print("已生成三张 html：单个骰子平坦，叠加后中间隆起，面数越多越平坦")
```

---

## 四、动手练习

### 基础档

**练习 15-1【折线图三连】**
写 `line_three.py`：
1. 生成 20 个点：`x = list(range(1, 21))`，`y = [i * i for i in x]`
2. 画折线，`linewidth=3`、`marker="o"`，标题「20 以内的平方」
3. `set_xticks(x[::2])`（只标奇数位避免重叠），`set_yticks(list(range(0, 401, 50)))`
4. 换三种内置样式各存一张图
5. **验收**：三张 png 都生成；换样式后图确实变了；刻度不叠字

**练习 15-2【散点三件套】**
写 `scatter_trio.py`：
1. 造 30 个点：`y = [i * i + random.randint(-20, 20) for i in range(30)]`
2. 一张图用 `s=`、`c=y`、`cmap=plt.cm.Blues`，加 `edgecolors="gray"`
3. 另一张图画**两个系列**：偶数下标红、奇数下标蓝，加 `label` 出图例
4. 用 `ax.set_facecolor("#f0f0f0")` 把底色调浅灰
5. **验收**：图例上有两项；第一张图点有大有小、颜色有深浅

**练习 15-3【校正绘图演练】**
写 `axis_fix.py`：
1. 生成 200 个随机点：`x = [random.uniform(0, 100) for _ in range(200)]`，`y = [random.uniform(0, 1_000_000) for _ in range(200)]`
2. 先**不校正**存 `axis_before.png`，再用 `ax.axis([0, 110, 0, 1_100_000])` 校正后存 `axis_after.png`
3. 打印两个列表的 `max()`，确认为什么要留余量
4. **验收**：对比两图能看出「贴边的点被切」；说清四个数的顺序
### 进阶档

**练习 15-4【可复现的随机游走】**
写 `walk_reproducible.py`：
1. 写 `RandomWalk` 类（含「拒绝原地不动」），`num_points=2000`
2. 第一次**不写** `random.seed()` 存 `walk_a.png`；第二次开头写 `random.seed(42)` 存 `walk_b.png`
3. 第三段：同样 `seed(42)`，连建两个 `RandomWalk` 并 `fill_walk()`，打印两个终点——应**完全相同**
4. **验收**：第 2、3 步终点相同；能解释「固定种子」为何是调试随机程序的必备手段

**练习 15-5【多系列随机游走对照】**
写 `walk_compare.py`：
1. `seed(42)`，做 3 组实验：每组 100 次游走、每条 2000 步，步长分别 1、2、3（`random.choice([-1,0,1])` 乘步长）
2. 三组各画一张图，都用 `alpha=0.1` + `cmap=plt.cm.Blues`
3. 用 `fig, axes = plt.subplots(1, 3, figsize=(18, 5))` 把三张图排成一行（**第一次用到多个坐标轴**），加 `fig.suptitle()` 存 `walk_三组对比.png`
4. **验收**：步长越大范围越大；一行三图保存成功；能说出 `plt.subplots(1, 3)` 返回什么

**练习 15-6【骰子实验台】**
写 `die_lab.py`：
1. `Die` 类 + `random.seed(2024)`
2. 掷 2 个六面骰 1000 次，打印点数和频次表（2~12），加 `assert sum == 1000`
3. 掷 1 个六面 + 1 个二十面 2000 次，统计点数和（2~26 共 25 种），用 `px.bar` 存 html
4. 计算两个分布的**方差**（提示：`sum((v - mean) ** 2 for v in data) / len(data)`）
5. **验收**：第 3 题分布比第 2 题更平（方差更小、峰更矮）；能解释原因

---

## 五、参考答案

### 参考答案 15-1

```python
# line_three.py —— 折线图三种样式
# 跑完可以删掉生成的 png 文件

import matplotlib.pyplot as plt

x = list(range(1, 21))
y = [i * i for i in x]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y, linewidth=3, marker="o", color="royalblue")
ax.set_title("20 以内的平方数", fontsize=16)
ax.set_xlabel("数字", fontsize=12)
ax.set_ylabel("平方", fontsize=12)

# ===== 定制刻度：x 轴只标奇数位，y 轴每 50 一格 =====
ax.set_xticks(x[::2])                              # 1, 3, 5, ... 隔一个取一个
ax.set_yticks(list(range(0, 401, 50)))
ax.grid(True, linestyle=":", alpha=0.6)             # 点状网格，不抢主体
fig.savefig("square_默认样式.png", dpi=100, bbox_inches="tight")

# ===== 换三种内置样式各存一张 =====
styles = [s for s in plt.style.available
          if s in ("seaborn-v0_8", "ggplot", "bmh", "dark_background")]
for style in styles[:3]:
    plt.style.use(style)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, linewidth=3, marker="o")
    ax.set_title(f"平方数（{style}）")
    ax.set_xticks(x[::2])
    ax.set_yticks(list(range(0, 401, 50)))
    fig.savefig(f"square_{style}.png", dpi=100, bbox_inches="tight")
    print("已生成", f"square_{style}.png")

plt.style.use("default")        # 换回默认，免得影响后面画的东西
```

### 参考答案 15-2

```python
# scatter_trio.py —— s / c / cmap 三件套 + 两个系列
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt

random.seed(42)

x = list(range(30))
y = [i * i + random.randint(-20, 20) for i in x]

plt.style.use("seaborn-v0_8")

# ===== 1. 三件套同时上场 =====
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(x, y,
           s=[i * 8 + 20 for i in x],     # 点大小随 x 递增
           c=y, cmap=plt.cm.Blues,        # 颜色由 y 决定 + Blues 渐变
           edgecolors="gray")             # 灰边让密集的点分得开
ax.set_title("散点图三件套：s / c / cmap")
fig.savefig("trio_三件套.png", dpi=100, bbox_inches="tight")

# ===== 2. 两个系列：偶数下标红色、奇数下标蓝色 =====
even = [(xi, yi) for i, (xi, yi) in enumerate(zip(x, y)) if i % 2 == 0]
odd = [(xi, yi) for i, (xi, yi) in enumerate(zip(x, y)) if i % 2 == 1]

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter([p[0] for p in even], [p[1] for p in even],
           s=70, c="red", label="偶数下标", alpha=0.7)
ax.scatter([p[0] for p in odd], [p[1] for p in odd],
           s=70, c="blue", label="奇数下标", alpha=0.7)
ax.set_title("两个系列一起画：靠 label + legend() 出图例")
ax.set_facecolor("#f0f0f0")            # 坐标区底色调浅灰，散点更跳
ax.legend()
fig.savefig("trio_两个系列.png", dpi=100, bbox_inches="tight")
print("两张图都已保存")
```

### 参考答案 15-3

```python
# axis_fix.py —— 校正绘图前后对比
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt

random.seed(7)

# ===== 1. 造 200 个随机点 =====
x_values = [random.uniform(0, 100) for _ in range(200)]
y_values = [random.uniform(0, 1_000_000) for _ in range(200)]
print(f"数据最大值: x={max(x_values):.1f}, y={max(y_values):.0f}")
print("所以边界设成 x:0~110、y:0~1_100_000 —— 比最大值多留约 10% 余量")

plt.style.use("seaborn-v0_8")

# ===== 2. 不校正：贴着边框的点会被切掉 =====
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(x_values, y_values, s=35, c=y_values, cmap=plt.cm.Blues)
ax.set_title("before：没有校正，边上的点被切掉")
fig.savefig("axis_before.png", dpi=100, bbox_inches="tight")

# ===== 3. 校正：ax.axis([xmin, xmax, ymin, ymax]) =====
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(x_values, y_values, s=35, c=y_values, cmap=plt.cm.Blues)
ax.set_title("after：校正过，四周留白，点是完整的")
ax.axis([0, 110, 0, 1_100_000])
fig.savefig("axis_after.png", dpi=100, bbox_inches="tight")

# ===== 4. 等价写法：set_xlim / set_ylim，名字更直白 =====
fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=35, c=y_values, cmap=plt.cm.Blues)
ax.set_xlim(0, 110)
ax.set_ylim(0, 1_100_000)
fig.savefig("axis_after_setlim.png", dpi=100, bbox_inches="tight")
print("三张图都已保存")
```

### 参考答案 15-4

```python
# walk_reproducible.py —— random.seed() 让随机程序可复现
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt


class RandomWalk:
    def __init__(self, num_points=2000):
        self.num_points = num_points
        self.x_values = [0]
        self.y_values = [0]

    def fill_walk(self):
        while len(self.x_values) < self.num_points:
            x_step = random.choice([-1, 0, 1])
            y_step = random.choice([-1, 0, 1])
            if x_step == 0 and y_step == 0:
                continue                     # ★ and 不是 or
            self.x_values.append(self.x_values[-1] + x_step)
            self.y_values.append(self.y_values[-1] + y_step)


plt.style.use("seaborn-v0_8")

# ===== 1. 不设种子：结果随机 =====
walk_a = RandomWalk(2000)
walk_a.fill_walk()
print("第一次运行终点:", (walk_a.x_values[-1], walk_a.y_values[-1]))

# ===== 2. 设种子：结果被固定 =====
random.seed(42)
walk_b = RandomWalk(2000)
walk_b.fill_walk()
print("第二次运行终点(seed 42):", (walk_b.x_values[-1], walk_b.y_values[-1]))

# ===== 3. 同一个种子跑两次，终点必须完全一样 =====
random.seed(42)
w1 = RandomWalk(2000)
w1.fill_walk()
random.seed(42)
w2 = RandomWalk(2000)
w2.fill_walk()
assert w1.x_values == w2.x_values, "同种子却给出了不同路径，seed 用法错了"
print("自检通过：random.seed(42) 之后随机序列完全可复现")

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(w1.x_values, w1.y_values, linewidth=1, color="royalblue")
ax.set_title("random.seed(42) 的随机游走")
ax.axis([0, 2000 * 1.05, 0, 2000 * 1.05])
fig.savefig("walk_reproducible.png", dpi=120, bbox_inches="tight")
```

### 参考答案 15-5

```python
# walk_compare.py —— 三种步长对照，一行三张图
# 跑完可以删掉生成的 png 文件

import random

import matplotlib.pyplot as plt


class RandomWalk:
    def __init__(self, num_points=2000, step_size=1):
        self.num_points = num_points
        self.step_size = step_size          # 新属性：一步走几格
        self.x_values = [0]
        self.y_values = [0]

    def fill_walk(self):
        while len(self.x_values) < self.num_points:
            x_step = random.choice([-1, 0, 1]) * self.step_size
            y_step = random.choice([-1, 0, 1]) * self.step_size
            if x_step == 0 and y_step == 0:
                continue
            self.x_values.append(self.x_values[-1] + x_step)
            self.y_values.append(self.y_values[-1] + y_step)


plt.style.use("seaborn-v0_8")
random.seed(42)

step_sizes = [1, 2, 3]
num_walks = 100
num_points = 2000

# ★ plt.subplots(1, 3) 返回 1 个 figure + 3 个 ax，参数是行数、列数
fig, axes = plt.subplots(1, 3, figsize=(19, 5))

for index, step_size in enumerate(step_sizes):
    ax = axes[index]                       # 逐个取出坐标轴对象
    for i in range(num_walks):
        walk = RandomWalk(num_points, step_size)
        walk.fill_walk()
        # c 必须是和点等长的列表，所以写成 [i] * len(...) 这样的列表
        ax.scatter(walk.x_values, walk.y_values, s=1,
                   c=[i] * len(walk.x_values), cmap=plt.cm.Blues,
                   alpha=0.1, edgecolors="none")
    ax.set_title(f"步长 = {step_size}", fontsize=14)
    ax.axis([0, num_points * step_size * 1.05, 0, num_points * step_size * 1.05])

fig.suptitle(f"三种步长对比：每张图 {num_walks} 次游走 × {num_points} 步", fontsize=16)
fig.tight_layout()                          # 自动排版，标题和图不重叠
fig.savefig("walk_三组对比.png", dpi=120, bbox_inches="tight")
print("已保存 walk_三组对比.png：步长越大，游走范围越大")
```

### 参考答案 15-6

```python
# die_lab.py —— 骰子实验平台
# 跑完可以删掉生成的 html 文件

import random

import plotly.express as px


class Die:
    def __init__(self, num_sides=6):
        self.num_sides = num_sides
        self.results = []

    def roll(self):
        self.results.append(random.randint(1, self.num_sides))


random.seed(2024)

# ===== 1. 两个六面骰：点数和 =====
d1, d2 = Die(), Die()
for _ in range(1000):
    d1.roll()
    d2.roll()

sums_6 = [a + b for a, b in zip(d1.results, d2.results)]
freq_6 = [sums_6.count(v) for v in range(2, 13)]
assert sum(freq_6) == len(sums_6), "统计对不上"
mean_6 = sum(sums_6) / len(sums_6)
var_6 = sum((v - mean_6) ** 2 for v in sums_6) / len(sums_6)
print(f"两个六面骰：均值 {mean_6:.2f}（理论 7），方差 {var_6:.3f}（理论 5.83）")
print("频次:", dict(zip(range(2, 13), freq_6)))

fig = px.bar(x=list(range(2, 13)), y=freq_6, labels={"x": "点数和", "y": "出现次数"})
fig.update_layout(title="两个六面骰：点数和分布（钟形）")
fig.update_traces(marker_color="royalblue", marker_line_color="black")
fig.add_hline(y=len(sums_6) / 11, line_dash="dash", line_color="red",
              annotation_text="理论平均")
fig.write_html("lab_两个六面.html")

# ===== 2. 六面 + 二十面：面数越多，分布越平 =====
d6, d20 = Die(6), Die(20)
for _ in range(2000):
    d6.roll()
    d20.roll()

sums_mix = [a + b for a, b in zip(d6.results, d20.results)]
freq_mix = [sums_mix.count(v) for v in range(2, 27)]
assert sum(freq_mix) == len(sums_mix), "统计对不上"
mean_mix = sum(sums_mix) / len(sums_mix)
var_mix = sum((v - mean_mix) ** 2 for v in sums_mix) / len(sums_mix)
print(f"\n六面 + 二十面：均值 {mean_mix:.2f}（理论 13.5），方差 {var_mix:.3f}")
print(f"最高点 {2 + freq_mix.index(max(freq_mix))}，方差对比："
      f"两个六面 {var_6:.2f} vs 六面+二十面 {var_mix:.2f}")

fig2 = px.bar(x=list(range(2, 27)), y=freq_mix, labels={"x": "点数和", "y": "出现次数"})
fig2.update_layout(title="六面 + 二十面：点数和分布（更平、峰更矮）")
fig2.update_traces(marker_color="tomato", marker_line_color="black")
fig2.write_html("lab_六面加二十面.html")
```
---

## 六、常见错误清单（务必逐条自查）

### 错误 1：★ 忘记校正绘图，点被边框切掉

数据范围正好等于坐标轴范围时，最边缘的点被裁掉一半，像「数据少了两头」。修法：`ax.axis([0, x_max * 1.05, 0, y_max * 1.05])`，四个数顺序是 `[xmin, xmax, ymin, ymax]`，写反会出现「图空白」。

### 错误 2：★ `fill_walk()` 里把 `and` 写成 `or`

写成 `if x_step == 0 or y_step == 0: continue`，等于要求「每一步必须同时改变 x 和 y」，图会退化成一条直线——不报错，只是图很怪。正确条件是两个都不动才重来，必须用 `and`。

### 错误 3：`c=` 传了数字却忘了 `cmap=`

所有点画成同一种默认蓝色，渐变根本没出现，**却不报错**。传数字必须配 `cmap`。

### 错误 4：`set_xticklabels` 不配 `set_xticks`

标签被硬贴在默认刻度上，数量一多就叠成团。**位置和文字必须配套调用。**

### 错误 5：样式名写老版本，报 `ValueError: style 'seaborn' is not in available styles`

matplotlib 0.13 之后 seaborn 系列加了版本后缀，写 `"seaborn-v0_8"` 而不是 `"seaborn"`；拿不准就先 `print(plt.style.available)` 看现装的。样式只是皮肤。

### 错误 6：`matplotlib.use("Agg")` 写在 `import matplotlib.pyplot` 之后

会报 `RuntimeError: Cannot switch to Agg after importing pyplot`，因为后端在导入 pyplot 时就定死了。顺序必须先 `matplotlib.use`、后 `import pyplot`。

### 错误 7：忘了 `assert sum(frequencies) == len(results)`

`range(1, die.num_sides + 1)` 少写 `+ 1`，最后一个面的频次永远是 0，图上少一根柱子，程序一声不吭。凡「按类别统计」都该加这行断言。
---

## 七、本单元验收自测

**1. 简答题**：Matplotlib 和 Plotly 分别在什么场景下选？为什么不能「一个库走天下」？
> **要点**：Matplotlib 适合**静态图**——要打印、贴进报告/论文，需要确定的像素。Plotly 适合**可交互图**——在浏览器里悬停看数值、缩放、开关图例。两者不是谁更高级，而是**输出形态不同**：前者输出「一张图」，后者输出「一个可以操作的小程序」。

**2. 判断题**：`fig, ax = plt.subplots()` 里 `fig`、`ax` 各代表什么？把 `ax.axis([0, 1100, 0, 1_100_000])` 里四个数的顺序说对。
> **要点**：`fig` 是 figure（整张画板），负责存盘与多子图排版；`ax` 是 axes（一张纸），负责画线、设标题、设刻度。逗号左边是解包：函数返回 `(figure, axes)` 元组被拆成两个变量。`ax.axis([...])` 四个数依次是 **`[xmin, xmax, ymin, ymax]`**。写反不报错但图会莫名其妙。

**3. 简答题**：散点三件套 `s=`、`c=`、`cmap=` 各控制什么？`c` 传名字和传数字有何不同？
> **要点**：`s`（size）控制点的**面积**；`c`（color）控制颜色；`cmap` 规定「数值 → 颜色」的翻译表。`c` 传**颜色名字**是逐点指定，不会有颜色条；`c` 传**数值列表**必须配 `cmap=`，此时自动上色并生成颜色条。**传数字忘配 `cmap` 是最高频的错误**——不报错，但点全同色。

**4. 改错题**：下面两段代码各有一处错误，先自己找，再看答案。

```python
# INTENTIONALLY-BROKEN 演示用：拒绝原地不动的条件写错了
import random

random.seed(1)
x, y = [0], [0]
for _ in range(20):
    x_step = random.choice([-1, 0, 1])
    y_step = random.choice([-1, 0, 1])
    if x_step == 0 or y_step == 0:
        continue
    x.append(x[-1] + x_step)
    y.append(y[-1] + y_step)
print("点数:", len(x), " y 的取值:", sorted(set(y)))
```

```python
# INTENTIONALLY-BROKEN 演示用：漏了 cmap，渐变不会出现
import matplotlib.pyplot as plt

x_values = [1, 2, 3, 4, 5]
y_values = [10, 40, 90, 160, 250]

fig, ax = plt.subplots()
ax.scatter(x_values, y_values, s=100, c=y_values)
ax.set_xticklabels(["一", "二", "三", "四", "五"])
ax.axis([0, 4, 0, 250])
fig.savefig("broken_刻度与边距.png", dpi=100, bbox_inches="tight")
```

> **要点**：第一处，`and` 被写成 `or`。只要 `x_step` 或 `y_step` 任意一个为 0 就重来，等于要求「每一步必须同时改变 x 和 y」——`y_step` 拿不到非零机会，图退化；更糟的是若 `x_step` 恰好一直为 0，整个循环一次都不执行，`len(x)` 只有 1。正确条件是「两个都不动才重来」：`if x_step == 0 and y_step == 0: continue`。第二处有两个问题：一是 `c=y_values` 没给 `cmap=`，颜色渐变根本不会出现（不报错，最隐蔽）；二是 `set_xticklabels` 没配 `set_xticks`，5 个标签被硬贴在默认刻度上，很可能重叠。另外 `ax.axis([0, 4, 0, 250])` 的上界正好等于数据最大值，最后一个点会被边框切掉，应留余量写成 `[0, 5.5, 0, 275]`。**5. 简答题**：`random.seed()` 解决什么问题？为何调试随机程序应该**最先**加它？
> **要点**：随机数**不可复现**——同样的代码跑两遍结果不同，出现「跑一遍正常、再跑一遍崩」的 bug 时根本无从下手。`random.seed(n)` 把随机数发生器初始化到一个确定起点，之后的**随机序列完全可复现**。所以调试第一步就是加种子：先把「随机性」这个变量消掉，剩下的行为就是确定的。

**6. 简答题**：`results.count(value)` 在干什么？为什么统计完要 `assert sum(frequencies) == len(results)`？为什么两个面数不同的骰子叠加后分布更均匀？
> **要点**：`results.count(value)` 是 `list` 的内置方法，返回该值出现了多少次——一行代替手写统计循环。断言确认「各类别频次之和 = 总投掷次数」，防止 `range(1, die.num_sides + 1)` 漏写 `+ 1` 导致最后一个面频次恒为 0——这类 bug 不报错，只是图上少一根柱子。统计结论：单枚骰子各点等概率、分布是平的；两个骰子相加时**靠中间的点有更多组合方式凑出来**（凑 7 有 6 种组合，凑 2 只有 1 种），分布向中间隆起；面数越多分布越平坦——**面数多 → 组合多 → 分布均匀**。

---

## 本单元小结与产出检查

- [ ] 能说清 Matplotlib（静态 PNG）与 Plotly（交互 HTML）选型
- [ ] 能默写 `fig, ax = plt.subplots()`，并解释它为何优于 `plt.plot()`
- [ ] 会用 `linewidth=`、`labels=`、`plt.style.use()` 定制折线图，知道老样式名要加 `-v0_8` 后缀
- [ ] 能同时用上 `s=`、`c=`、`cmap=plt.cm.Blues`，说出 `c` 传名字和传数字的差别
- [ ] **能用 `ax.axis([xmin, xmax, ymin, ymax])` 校正绘图留边距**，并解释点被裁掉的原因
- [ ] 会用 `set_xticks()` + `set_xticklabels()` 配套定制刻度，只调后者叠字
- [ ] 存图记得加 `bbox_inches="tight"`（可选 `dpi=200`），无图形界面时先 `matplotlib.use("Agg")` 再导入 pyplot
- [ ] 能写出带「拒绝原地不动」的 `RandomWalk` 类，解释为何用 `and` 而非 `or`，会用 `random.seed()` 让结果可复现
- [ ] 能写出 `Die` 类，用 `results.count()` 统计频次、`px.bar()` 画分布图
- [ ] 练习 15-1、15-4、15-6 跑通
**下一单元预告**：本单元的数据全是**我们自己造出来的**。下一单元讲「下载真实数据」：数据从网上的 CSV（锡特卡机场气温）和 GeoJSON（USGS 地震）里来。你会学 `csv` 读表头、`datetime.strptime` 解析日期、处理缺失值的 `try/except ValueError` + `else` 套路，并用 `px.scatter_geo()` 画全球地震图。本单元练「造数据 + 画图」，下一单元练「拿数据 + 洗数据」。