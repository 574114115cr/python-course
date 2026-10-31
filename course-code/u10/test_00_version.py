# test_00_version.py —— 确认 pytest 环境正常
def test_pytest_works():
    """最小测试：确认 pytest 能正常发现并运行测试。"""
    assert True      # 这个测试总是通过，用来验证环境


def test_assert_message():
    """验证 assert 的消息会显示出来。"""
    value = 1 + 1
    assert value == 2, f"1 加 1 应该等于 2，实际是 {value}"
