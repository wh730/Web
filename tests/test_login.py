import os
import pytest
import allure
from services.auth_service import AuthService

@allure.epic("Web UI")
@allure.feature("登录")
@pytest.mark.smoke
@pytest.mark.critical
def test_valid_user_can_login(page, app_config, test_credentials):
    """示例用例：请按真实应用的 data-testid 和登录路径调整。"""
    username, password = test_credentials
    with allure.step("使用独立测试账号登录"):
        AuthService(page, app_config["base_url"]).login_as(username, password)
    with allure.step("验证登录成功"):
        assert "/login" not in page.url, f"登录后仍停留在登录页：{page.url}"
