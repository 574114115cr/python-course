# multiline.py —— 字符串的换行与特殊字符

# 三引号可以写多行文本
poem = """床前明月光，
疑是地上霜。
举头望明月，
低头思故乡。"""
print(poem)

# 反斜杠开头的三引号不参与缩进，适合保持代码原样
code_sample = r"""
def hello():
    print("这里面的缩进原样保留")
    if True:
        print("4 个空格")
"""
print(code_sample)

# 转义字符
print("第一行\n第二行")      # \n 换行
print("制表符：\t|结束")# \t 水平制表符
print("他说：\"你好\"")       # \" 表示双引号本身
print("路径：C:\\new\\test")  # \\ 表示一个反斜杠
print("使用 \a 响一声：\a")  # \a 终端响铃

# 一行太长时用 \ 续行，或者直接用括号
long_text = "这是一段很长很长的文字，" \
            "用来演示续行拼接的效果"
print(long_text)

long_text2 = ("这是一段很长很长的文字，"
              "用括号代替反斜杠，更推荐这种写法，因为括号内的换行会被自动忽略")
print(long_text2)
