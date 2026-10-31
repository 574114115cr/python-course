# pizzas/models.py —— 比萨与配料（多对一）
from django.db import models


class Pizza(models.Model):
    """一种比萨。"""

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Topping(models.Model):
    """比萨上的一种配料，通过外键关联到特定比萨。"""

    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
