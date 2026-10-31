# （片段）main.py —— 长函数名用别名
from geometry import area, is_square
from geometry import perimeter as peri

w, h = 3, 4
print("面积", area(w, h))
print("周长", peri(w, h))          # 少写 7 个字符，但读起来仍然清楚
print("是正方形？", is_square(w, h))
