# （片段）car.py
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year

    def describe(self):
        return f"{self.year} {self.make} {self.model}"


class ElectricCar(Car):
    def __init__(self, make, model, year, battery=75):
        super().__init__(make, model, year)
        self.battery = battery

    def describe(self):
        return super().describe() + f"（电池 {self.battery} kWh）"


if __name__ == "__main__":
    print(Car("比亚迪", "汉", 2024).describe())
    print(ElectricCar("特斯拉", "Model 3", 2024).describe())
