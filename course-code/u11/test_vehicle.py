# test_vehicle.py —— 关卡验收 3：给验收 2 的类写测试

import pytest

from vehicle import Car, ElectricCar


class TestCar:
    """测试汽车类。"""

    def test_fuel_cost(self):
        """正常情况：300 公里、7.5L/100km、油价 8 元。"""
        car = Car("测试车", 100000, 7.5)
        # 300/100 * 7.5 = 22.5 升，22.5 * 8 = 180 元
        assert car.fuel_cost(300) == 180.0

    def test_zero_distance(self):
        """★ 边界：不走就不花钱。"""
        car = Car("测试车", 100000, 7.5)
        assert car.fuel_cost(0) == 0.0


class TestElectricCar:
    """测试电动汽车类。"""

    def test_inherits_from_car(self):
        """★ 验证继承关系。"""
        ec = ElectricCar("测试电动车", 200000, 60)
        assert isinstance(ec, Car)

    def test_fuel_cost_is_overridden(self):
        """★ 验证方法重写：电动车不走油费逻辑。"""
        car = Car("燃油车", 100000, 7.5)
        ec = ElectricCar("电动车", 200000, 60)

        # 同样跑 300 公里，电动车成本应该远低于燃油车
        car_cost = car.fuel_cost(300)
        electric_cost = ec.fuel_cost(300)

        assert electric_cost == 27.0      # 300/100*15*0.6 = 27
        assert electric_cost < car_cost
