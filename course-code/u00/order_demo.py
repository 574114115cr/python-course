# order_demo.py —— Python 严格从上往下逐行执行

print("第一步：准备开始")     # 第 1 行最先打印

name = "小明"                # 第 3 行：把"小明"这个名字存进变量 name
print("第二步：变量已赋值，name =", name)   # 第 4 行：这里才能用 name

print("第三步：程序结束")     # 最后一行
