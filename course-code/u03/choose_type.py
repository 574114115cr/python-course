# choose_type.py —— 列表 vs 元组：按"会不会变"来选

# 1）课程学生名单：会有人退课/转学 -> 列表
class_students = ["小明", "小红", "小刚"]
class_students.append("小丽")
print("1. 名单用列表：", class_students)

# 2）经纬度坐标：位置固定 -> 元组
beijing = (116.40, 39.90)
print("2. 坐标用元组：", beijing)

# 3）购物车：随时增删 -> 列表
shopping_cart = ["牛奶", "面包"]
shopping_cart.remove("面包")
print("3. 购物车用列表：", shopping_cart)

# 4）生日：年/月/日不会变 -> 元组
birthday = (1998, 5, 20)
year, month, day = birthday
print(f"4. 生日用元组：{year}年{month}月{day}日")

# 5）字典的键：必须不可变，否则改了就找不到值 -> 元组
city_by_coord = {
    (116.40, 39.90): "北京",
    (121.47, 31.23): "上海",
    (113.26, 23.13): "广州",
}
print("5. 字典键用元组：")
print("  (116.40, 39.90) ->", city_by_coord[(116.40, 39.90)])
print("  (113.26, 23.13) ->", city_by_coord[(113.26, 23.13)])
print("  字典共有", len(city_by_coord), "个键")
