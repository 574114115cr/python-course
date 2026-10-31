# matrix_demo.py —— 嵌套列表（矩阵）的访问

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# 1）区别：matrix[0] 拿到的是"一整个子列表"，matrix[0][0] 才是具体数字
print("matrix[0]：", matrix[0])          # [1, 2, 3]
print("matrix[0][0]：", matrix[0][0])    # 1
print("类型对比：", type(matrix[0]), type(matrix[0][0]))

# 2）取右下角元素 9，两种写法
print("写法一：", matrix[2][2])          # 9  用正索引
print("写法二：", matrix[-1][-1])# 9  用负索引

# 3）最后一行的所有元素
last_row = matrix[-1]
print("最后一行：", last_row)            # [7, 8, 9]
print("第一行：", matrix[0])

# 4）修改 matrix[1][2] 的值为 60
matrix[1][2] = 60
print("修改后：", matrix)      # [[1, 2, 3], [4, 5, 60], [7, 8, 9]]

# 顺带演示：把整个第二行换掉（不是修改，是整体替换）
matrix[1] = [40, 50, 60]
print("替换第二行后：", matrix)          # [[1, 2, 3], [40, 50, 60], [7, 8, 9]]
