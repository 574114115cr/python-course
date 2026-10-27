# -*- coding: utf-8 -*-
"""生成 course-fluent/bank.json（36 题：每单元 3 题，概念/代码/设计各一）。

单独成脚本是为了让答案里的代码块保持可读；改题改这里，再运行本脚本。
"""
import json
import os
from textwrap import dedent

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "course-fluent", "bank.json")


def Q(qid, unit, level, q, a):
    return {"id": qid, "unit": unit, "level": level,
            "q": dedent(q).strip(), "a": dedent(a).strip()}


DATA = [
    Q("F1-1", 1, "概念", """
为什么 Python 用 `len(x)` 而不是 `x.len()`？从数据模型和实现两个角度解释。
""", """
**数据模型**：`len()` 是语言级协议的一部分。任何实现 `__len__` 的对象都能被 `len()`、`bool()`、`list()` 等内置函数统一处理，调用方不需要知道具体类型。

**实现**：CPython 在 `PyObject` 的类型槽位里直接缓存了长度函数的指针，`len()` 走 C 层快路径，不做属性查找，也不创建绑定方法。`x.__len__()` 反而绕过了这层优化。
"""),

    Q("F1-2", 1, "代码", """
实现 `Vector` 类：支持 `len()`、下标、切片、`for`、`repr()`，且 `repr` 输出形如 `Vector([1, 2, 3])`。
""", """
```python
class Vector:
    def __init__(self, data):
        self._data = list(data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return Vector(self._data[i])
        return self._data[i]

    def __repr__(self):
        return f"Vector({self._data!r})"

v = Vector([1, 2, 3])
print(len(v), v[0], v[1:], repr(v))
```

`__getitem__` 同时接收下标和 `slice`。如果希望切片仍返回 `Vector`，必须显式判断 `isinstance(i, slice)`。
"""),

    Q("F1-3", 1, "设计", """
下面的代码为什么三行会联动？给出两种正确写法，并说明各自适用场景。

```python
grid = [[0] * 3] * 3
grid[0][0] = 1
```
""", """
`[[0] * 3] * 3` 只创建了**一个**内层列表，外层三次 `*` 复制的是同一个引用，所以三行共享。

写法一（需要独立行）：

```python
grid = [[0] * 3 for _ in range(3)]
```

写法二（只读矩阵）：

```python
grid = [[0] * 3] * 3   # 不写入内层时可用
```

判断标准：只要会写入内层结构，就必须用推导式。
"""),

    Q("F2-1", 2, "概念", """
`dict` 的键为什么必须可哈希？3.7 起为什么可以依赖插入顺序？
""", """
**可哈希**：dict 是哈希表，插入和查找都靠 `hash(key)` 定位槽位，冲突时再用 `==` 比较。可变对象（list/dict/set）的哈希会随内容变化，一旦变化就再也找不到原来的槽位，所以被设计为不可哈希。

**顺序**：3.6 起 CPython 改用紧凑布局——条目数组按插入顺序连续存放，另有一张稀疏索引表指向条目。3.7 把它写进语言规范，因此可以依赖「遍历顺序 = 插入顺序」。
"""),

    Q("F2-2", 2, "代码", """
给定 `words` 列表：用 `Counter` 输出词频前 3；用 `defaultdict` 按首字母分组，只保留组内至少 2 个词的组。
""", """
```python
from collections import Counter, defaultdict

words = ["apple", "avocado", "banana", "blueberry",
         "cherry", "apple", "banana", "apple"]

print(Counter(words).most_common(3))

groups = defaultdict(list)
for w in words:
    groups[w[0]].append(w)

print({k: v for k, v in groups.items() if len(v) >= 2})
```
"""),

    Q("F2-3", 2, "设计", """
处理用户上传的 CSV：HTTP 层拿到的是 `bytes`，如何保证中文不乱码？说明每一步的编码边界。
""", """
1. **HTTP → 文本**：`raw.decode("utf-8-sig")`，`utf-8-sig` 会顺带吃掉 BOM；不要用 `errors="ignore"`，它会静默丢数据。
2. **解析**：用 `csv.reader(io.StringIO(text))` 或 `io.TextIOWrapper`，全程保持 `str`。
3. **落库/输出**：统一 UTF-8；如果要给 Excel 打开，写回时用 `utf-8-sig` 带 BOM。
4. **失败处理**：捕获 `UnicodeDecodeError`，记录出错字节位置并提示用户另存为 UTF-8，而不是猜编码。

关键是：**只在入口解码一次，内部全程 str，出口再编码**。
"""),

    Q("F3-1", 3, "概念", """
为什么 `@dataclass` 不允许 `tags: list = []`？`field(default_factory=list)` 解决了什么？
""", """
dataclass 生成的 `__init__` 会把默认值直接写进函数签名，而函数默认参数**只在定义时求值一次**，所有实例会共享同一个 list。dataclass 检测到 list/dict/set 这类可变默认值会直接抛 `ValueError`。

`field(default_factory=list)` 传入的是工厂函数，每次实例化时调用一次，得到独立的 list。
"""),

    Q("F3-2", 3, "代码", """
写一个 `frozen=True` 的 `Range(lo, hi)`：构造时校验 `lo <= hi`，支持哈希与模式匹配。
""", """
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Range:
    lo: int
    hi: int

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError(f"lo({self.lo}) > hi({self.hi})")

r = Range(1, 5)
print(hash(r))

match r:
    case Range(lo=1, hi=h):
        print("starts at 1, ends", h)
```

注意 frozen 是浅冻结：字段不能重新赋值，但字段指向的可变对象仍可修改。
"""),

    Q("F3-3", 3, "设计", """
函数把内部 list 直接返回给调用方，调用方 append 后内部状态被意外修改。给出三种防御方案及代价。
""", """
1. **返回副本**：`return list(self._items)`。最简单，但每次调用都复制，大列表有成本。
2. **返回不可变视图**：`return tuple(self._items)`。零拷贝风险，但调用方失去 list 接口，且嵌套元素仍共享。
3. **返回只读代理**：`types.MappingProxyType`（映射）或自定义只读序列。语义最清晰，实现成本最高。

若内部数据会被并发修改，还要考虑加锁或返回快照；方案选择取决于「调用频率 × 数据规模 × 是否需要 list 接口」。
"""),

    Q("F4-1", 4, "概念", """
「函数是一等对象」具体体现在哪些操作上？为什么 `sorted(key=len)` 不能写成 `key=len(x)`？
""", """
体现在：函数可以赋值给变量、作为参数传递、作为返回值、存进容器、带属性（`__name__`、`__doc__`）。

`key` 接收的是一个**可调用对象**，`sorted` 会在内部对每个元素调用它。写 `key=len(x)` 会先求值成一个整数，`sorted` 拿到 int 后尝试调用，直接 `TypeError: 'int' object is not callable`。
"""),

    Q("F4-2", 4, "代码", """
写 `tag(name, /, content, *, cls="", **attrs)`：`name` 仅限位置，`cls` 仅限关键字，其余关键字变成 HTML 属性。
""", """
```python
def tag(name, /, content, *, cls="", **attrs):
    extra = "".join(f' {k}="{v}"' for k, v in attrs.items())
    return f'<{name} class="{cls}"{extra}>{content}</{name}>'

print(tag("p", "hi", cls="lead", id="x1"))
# <p class="lead" id="x1">hi</p>
```
"""),

    Q("F4-3", 4, "设计", """
给一个没有类型注解的第三方库写包装层，`Any`、`object`、`cast`、`Protocol` 应该怎么选？
""", """
- **Protocol**：先用它描述「我用到的那些方法」，包装层的入参尽量用协议，不绑定具体类。
- **object**：确实只需要「任意对象」时用，比 `Any` 安全，因为它不允许任意属性访问。
- **Any**：只在边界处（调用三方库返回值）短暂使用，并立刻用 `isinstance` 或 `cast` 收窄。
- **cast**：最后手段，等于向检查器承诺；写错只会在运行时炸，必须配测试。

原则：`Any` 只出现在最外层的适配函数里，不让它渗进业务代码。
"""),

    Q("F5-1", 5, "概念", """
闭包捕获的是变量还是值？`[lambda: i for i in range(3)]` 输出什么？如何修复？
""", """
捕获的是**变量**（cell），不是创建时的值。三个 lambda 共享同一个 `i`，循环结束后 `i == 2`，所以输出 `[2, 2, 2]`。

修复一：默认参数固化当前值。

```python
funcs = [lambda i=i: i for i in range(3)]
```

修复二：用 `functools.partial` 或工厂函数把值包进去。
"""),

    Q("F5-2", 5, "代码", """
写 `@retry(times=3, exceptions=(TimeoutError,))`：失败重试，最后一次仍失败则抛出，必须保留被装饰函数的元数据。
""", """
```python
import functools

def retry(times=3, exceptions=(TimeoutError,)):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if i == times - 1:
                        raise
        return wrapper
    return deco

@retry(times=2)
def fetch():
    raise TimeoutError("boom")
```

`functools.wraps` 保留 `__name__`、`__doc__` 与签名，否则框架按名字/签名注入时会失效。
"""),

    Q("F5-3", 5, "设计", """
一段 6 个分支的计费 `if/elif` 如何改成策略注册？新增一种计费方式时改动哪里？
""", """
```python
PRICING = {}

def pricing(name):
    def deco(fn):
        PRICING[name] = fn
        return fn
    return deco

@pricing("normal")
def normal(qty, unit):
    return qty * unit

@pricing("bulk")
def bulk(qty, unit):
    return qty * unit * 0.9

def charge(mode, qty, unit):
    try:
        return PRICING[mode](qty, unit)
    except KeyError:
        raise ValueError(f"unknown pricing mode: {mode}") from None
```

新增方式只需加一个函数 + 装饰器，不改 `charge`；`if/elif` 的修改点则集中在函数体里，越长越容易漏分支。
"""),

    Q("F6-1", 6, "概念", """
为什么重写 `__eq__` 之后 `__hash__` 会变成 `None`？相等、哈希、可变三者是什么关系？
""", """
Python 认为：一旦你按值定义相等，默认的「按身份哈希」就不再成立——两个相等对象必须有相同哈希，否则放进 set 会出现两个「相等」元素。

规则：
- `a == b` 为真 ⇒ `hash(a) == hash(b)` 必须为真；
- 可哈希对象必须不可变（或至少哈希所依赖的字段不可变）；
- 重写 `__eq__` 后需要哈希就显式重写 `__hash__`，例如 `hash((self.x, self.y))`。
"""),

    Q("F6-2", 6, "代码", """
实现 `Playlist`：支持 `len`、下标、切片（返回 `Playlist`）、`for`、`in`。
""", """
```python
class Playlist:
    def __init__(self, songs):
        self._songs = list(songs)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return Playlist(self._songs[i])
        return self._songs[i]

    def __iter__(self):
        return iter(self._songs)

    def __contains__(self, song):
        return song in self._songs
```
"""),

    Q("F6-3", 6, "设计", """
`repr` 与 `str` 在日志、调试器、用户界面三处应该怎么分工？给出判断标准。
""", """
- **调试器 / 容器打印 / 日志的对象字段**：用 `repr`，要求准确、可重建、带引号。容器打印元素时调用的就是 `repr`。
- **面向用户的界面**：用 `str`，要求可读，可以本地化。
- **只定义 `repr`**：`str` 自动回退，适合绝大多数内部对象。
- **两者都定义**：当对象既有「开发者视角」又有「用户视角」时，例如 `Decimal("1.20")` 与 `1.20`。

判断标准：这段输出是给「排查问题的人」还是「使用产品的人」看。
"""),

    Q("F7-1", 7, "概念", """
鸭子类型、Protocol、ABC 三者的约束强度和侵入性有什么不同？
""", """
| 方式 | 约束发生时机 | 是否要求继承 | 侵入性 |
|---|---|---|---|
| 鸭子类型 | 运行时（调用到才报错） | 否 | 无 |
| Protocol | 静态检查时（mypy/pyright） | 否（结构化） | 无 |
| ABC | 实例化时（抽象方法未实现则报错） | 是，或 `register()` | 高 |

给第三方类加约束用 Protocol；自己掌控的类层级用 ABC 明确契约；脚本和内部工具用鸭子类型即可。
"""),

    Q("F7-2", 7, "代码", """
定义 `Closeable` 协议（含 `close()`），加 `@runtime_checkable`，并让一个没有继承关系的 `Conn` 通过 `isinstance`。
""", """
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

class Conn:
    def close(self):
        print("closed")

print(isinstance(Conn(), Closeable))   # True
```

`runtime_checkable` 只检查成员名是否存在，不检查签名与返回类型。
"""),

    Q("F7-3", 7, "设计", """
有 `class A`、`class B(A)`、`class C(A)`、`class D(B, C)`，且 B、C 的 `ping()` 都调用 `super().ping()`。写出 MRO 与 `D().ping()` 的输出，并说明什么时候该改成组合。
""", """
MRO：`D → B → C → A → object`，输出：

```
B
C
A
```

`super()` 是「沿 MRO 的下一个类」，不是「父类」，所以 B 的 `super()` 命中 C。

该改组合的信号：B/C 与 D 不是 is-a 关系、只是为了复用实现、继承层级超过 2 层、父类会独立变化。
"""),

    Q("F8-1", 8, "概念", """
为什么 `list[Dog]` 不能当作 `list[Animal]` 使用，而 `Sequence[Dog]` 可以？
""", """
`list` 是**不变（invariant）**的：它既可读又可写。若允许 `list[Dog]` 冒充 `list[Animal]`，就能往里 append 一只 `Cat`，原列表的类型契约被破坏。

`Sequence` 是**协变（covariant）**的：它只读，不提供写入方法，所以 `Sequence[Dog]` 可以安全地当 `Sequence[Animal]` 用。

记法：只读容器协变，可变容器不变，只作为输入的 Callable 参数逆变。
"""),

    Q("F8-2", 8, "代码", """
给 `Vector(x, y)` 实现 `+`、标量 `*`、反射 `*`、一元 `-`；类型不匹配时返回 `NotImplemented`。
""", """
```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, k):
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector(self.x * k, self.y * k)

    __rmul__ = __mul__

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
```

返回 `NotImplemented` 让解释器去尝试对方的反射方法；直接抛 `TypeError` 会阻断这条回退链。
"""),

    Q("F8-3", 8, "设计", """
TypedDict、dataclass、pydantic BaseModel 三者怎么选？
""", """
- **TypedDict**：数据本质是 dict（JSON、API 响应），只需要静态形状检查，不想要运行时开销。
- **dataclass**：内部领域对象，需要方法、默认值、相等/哈希，字段可信，不需要运行时校验。
- **pydantic**：边界输入（HTTP 请求、配置文件），需要运行时解析、类型转换与详细报错。

组合用法很常见：HTTP 层用 pydantic 校验，转成 dataclass 进业务层，出站再序列化成 TypedDict/JSON。
"""),

    Q("F9-1", 9, "概念", """
可迭代对象与迭代器有什么区别？`for` 循环的展开步骤是什么？
""", """
- **可迭代对象**：实现 `__iter__`，每次调用返回一个迭代器；可重复遍历。
- **迭代器**：实现 `__next__`，且 `__iter__` 返回 `self`；只能遍历一次，耗尽后抛 `StopIteration`。

`for` 的展开：

```python
it = iter(obj)
while True:
    try:
        x = next(it)
    except StopIteration:
        break
```
"""),

    Q("F9-2", 9, "代码", """
用生成器展平任意嵌套的 list，再用 `islice` 取前 5 项。
""", """
```python
from itertools import islice

def flatten(items):
    for it in items:
        if isinstance(it, list):
            yield from flatten(it)
        else:
            yield it

print(list(flatten([1, [2, [3, 4]], 5])))       # [1, 2, 3, 4, 5]
print(list(islice(flatten([[1, [2]], 3, 4, 5, 6]), 5)))  # [1, 2, 3, 4, 5]
```

`yield from` 不只是省一层循环，它还负责把 `send`、`throw`、`close` 委派给子生成器。
"""),

    Q("F9-3", 9, "设计", """
用 `@contextmanager` 实现「临时切换工作目录」，要求异常时也能切回。
""", """
```python
import os
from contextlib import contextmanager

@contextmanager
def chdir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)
```

`yield` 必须放在 `try/finally` 里；否则 `with` 块内抛异常时不会执行恢复逻辑。上下文管理器不要吞异常——`finally` 只负责清理，不负责 `return True`。
"""),

    Q("F10-1", 10, "概念", """
GIL 是什么？为什么多线程不能加速纯 Python 计算，却适合 IO 密集任务？
""", """
GIL 是 CPython 解释器的全局锁：同一进程内，同一时刻只有一个线程执行 Python 字节码。

- 纯 Python 计算几乎全程持有 GIL，多线程只是轮流执行，还有切换开销，所以不加速。
- IO 操作（网络、文件、`sleep`）在等待时会释放 GIL，其他线程可以继续跑，所以总等待时间被重叠。

GIL 不保证线程安全：`x += 1` 仍是读—改—写三步，可能被切换。
"""),

    Q("F10-2", 10, "代码", """
用 `ThreadPoolExecutor` 并发抓取 10 个 URL：5 秒超时，单个失败不影响整体，最后输出成功数与失败列表。
""", """
```python
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url, timeout=5):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status

def crawl(urls, workers=8):
    ok, failed = 0, []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(fetch, u): u for u in urls}
        for f in as_completed(futs):
            try:
                f.result()
                ok += 1
            except Exception as e:
                failed.append((futs[f], repr(e)))
    return ok, failed
```

异常存在 Future 里，只有 `result()` 时才抛出；`with` 退出会等待所有任务结束。
"""),

    Q("F10-3", 10, "设计", """
1000 张图片需要压缩，单张耗时约 0.2 秒，其中 90% 是 CPU。选线程、进程还是协程？说明理由与并发度。
""", """
选**进程池**。压缩是 CPU 密集，GIL 会让多线程退化为串行；协程更不行，阻塞计算会卡死事件循环。

- 并发度：`max_workers = os.cpu_count()`，通常 4–16；IO 写盘占比高时可略高于核数。
- 成本：进程启动与 pickle 传输有开销，所以按批提交（每批 20–50 张）比单张提交更划算。
- 注意：任务函数要在模块顶层，参数与返回值必须可 pickle；写盘用主进程统一做，避免多进程争抢同一文件。
"""),

    Q("F11-1", 11, "概念", """
协程对象、Task、Future 三者的关系是什么？
""", """
- **协程对象**：调用 `async def` 函数得到的东西，本身不会运行，必须被 `await` 或被调度。
- **Task**：把协程包装成「已排入事件循环」的调度单元，创建后立即开始推进，可以取消、可以查询状态。
- **Future**：更底层的「未来结果」占位符，Task 是 Future 的子类；一般不用手写，库内部使用。

关系：`Task(coro)` 包装协程，事件循环驱动 Task，Task 完成后其结果就是一个 Future 结果。
"""),

    Q("F11-2", 11, "代码", """
用 `TaskGroup` 并发 3 个任务，整体 2 秒超时；其中一个抛 `ValueError`，捕获 `ExceptionGroup`。
""", """
```python
import asyncio

async def work(name, delay):
    await asyncio.sleep(delay)
    if name == "bad":
        raise ValueError("boom")
    return name

async def main():
    try:
        async with asyncio.timeout(2):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(work("a", 0.1))
                tg.create_task(work("bad", 0.2))
                tg.create_task(work("c", 0.3))
    except TimeoutError:
        print("timeout")
    except ExceptionGroup as eg:
        for e in eg.exceptions:
            if isinstance(e, ValueError):
                print("value error:", e)

asyncio.run(main())
```

`TaskGroup` 在任一任务失败时会取消同组其他任务，并把异常包成 `ExceptionGroup`（Python 3.11+）。要按类型分别处理可以用 `except* ValueError`，但**不能在同一个 `try` 里混用 `except` 和 `except*`**。
"""),

    Q("F11-3", 11, "设计", """
异步服务里必须调用一个阻塞库（比如 `requests` 或 `psycopg2` 同步驱动），有哪三种处理方式？各自代价是什么？
""", """
1. **`await asyncio.to_thread(fn, ...)`**：把阻塞调用丢到默认线程池。改动最小，代价是占用线程、线程池默认上限较小，高并发时要调大。
2. **专用 `ThreadPoolExecutor` + `run_in_executor`**：可以控制池大小、隔离慢调用，代价是要自己管理生命周期。
3. **换异步库**：`httpx` / `asyncpg`。性能最好，代价是改造成本高、生态兼容性要验证。

不要直接在协程里调用阻塞函数——它会卡住整个事件循环，所有并发任务一起停摆。
"""),

    Q("F12-1", 12, "概念", """
`obj.x` 的属性查找顺序是什么？`__getattr__` 在哪一步生效？
""", """
1. 类型上的**数据描述符**（实现 `__set__` 或 `__delete__`）
2. 实例 `__dict__`
3. 类型上的**非数据描述符**（只实现 `__get__`）
4. 类属性
5. `__getattr__`（以上全部失败才调用）

`__getattribute__` 拦截整个流程，`__getattr__` 只是最后的兜底。`property` 是数据描述符，所以能覆盖实例字典。
"""),

    Q("F12-2", 12, "代码", """
写一个 `Positive` 描述符：通过 `__set_name__` 拿到属性名，赋值时校验必须为正数。
""", """
```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError("must be positive")
        setattr(obj, self.name, value)

class Order:
    qty = Positive()
    price = Positive()

o = Order()
o.qty = 3
print(o.qty)      # 3
```

数据描述符优先于实例字典，所以 `o.qty = -1` 一定走 `__set__`。
"""),

    Q("F12-3", 12, "设计", """
`__init_subclass__`、类装饰器、元类，三者在什么场景下该用哪个？
""", """
- **`__init_subclass__`**：子类创建时做注册、校验、注入默认值。最轻，优先选它。
- **类装饰器**：对已创建的类做批量改造（加 `__repr__`、包方法），显式、可组合、易测试。
- **元类**：需要控制类创建过程本身（改命名空间、`__prepare__`、强制结构），或框架要兼容多个 Python 版本时。

判断：能用 `__init_subclass__` 解决就不写元类；元类应作为实现细节，不要写进公开 API。
"""),
]


def main():
    assert len(DATA) == 36, len(DATA)
    units = sorted({d["unit"] for d in DATA})
    assert units == list(range(1, 13)), units
    for u in units:
        assert sum(1 for d in DATA if d["unit"] == u) == 3, u
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)
    print(f"写入 {OUT}：{len(DATA)} 题")


if __name__ == "__main__":
    main()
