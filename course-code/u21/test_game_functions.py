# test_game_functions.py —— 关卡 2 第 3 条的验收材料：自己写的测试
import pytest

from game_functions import check_collision, check_ship_limit, update_score


# ===== 一个只提供 colliderect 的替身，够测试用了 =====
class FakeRect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def colliderect(self, other):
        return (self.x < other.x + other.w and self.x + self.w > other.x
                and self.y < other.y + other.h and self.y + self.h > other.y)


def far_apart():
    """飞船和外星人相距很远，谁也碰不到谁。"""
    return FakeRect(0, 0, 10, 10), FakeRect(500, 500, 50, 50)


class TestCheckShipLimit:
    def test_normal(self):
        """正常：还有 2 艘。"""
        assert check_ship_limit([1, 2]) == 2

    def test_zero_ships_means_game_over(self):
        """★ 边界：0 艘必须返回 0，调用方据此结束游戏。"""
        assert check_ship_limit([]) == 0

    @pytest.mark.parametrize("ships,expected", [([], 0), ([1], 1), ([1, 2, 3], 3)])
    def test_parametrized(self, ships, expected):
        """参数化：一次测多个输入。"""
        assert check_ship_limit(ships) == expected


class TestCheckCollision:
    def test_ship_hits_alien(self):
        """飞船和外星人位置重叠 → 碰撞。"""
        assert check_collision(FakeRect(100, 100, 50, 50),
                              FakeRect(120, 120, 50, 50), []) is True

    def test_bullet_hits_alien(self):
        """★ 飞船没撞到，但子弹撞到了 → 也算碰撞。"""
        ship, alien = far_apart()
        assert check_collision(ship, alien, [FakeRect(510, 510, 10, 10)]) is True

    def test_no_collision(self):
        """谁都没碰到 → 不碰撞。"""
        ship, alien = far_apart()
        assert check_collision(ship, alien, []) is False


class TestUpdateScore:
    def test_one_alien(self):
        """★ 断言具体数值：1 个外星人 = 10 分。"""
        assert update_score(0, 1) == 10

    def test_none_hit_adds_zero(self):
        """边界：没击落任何外星人，分数不变。"""
        assert update_score(30, 0) == 30

    def test_custom_points(self):
        """改成每只 20 分。"""
        assert update_score(0, 2, points_per_alien=20) == 40

    def test_negative_score_is_allowed(self):
        """★ 业务约定：分数可以减（踩到外星人扣分），不是 bug。"""
        assert update_score(5, -1) == -5
