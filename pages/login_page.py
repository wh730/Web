from playwright.sync_api import Page, expect
from typing import Optional
class LoginPage:
    """单页对象：只封装登录页定位、交互和页面级断言。"""
    def __init__(self, page: Page):
        self.page = page
        # 这些 test id 是示例契约，请按真实应用 DOM 修改。
        self.username = page.get_by_test_id("login-username")
        self.password = page.get_by_test_id("login-password")
        self.submit = page.get_by_test_id("login-submit")
        self.error_message = page.get_by_test_id("login-error")
        self.user_menu = page.get_by_test_id("user-menu")

    def open(self, base_url: str) -> None:
        self.page.goto(f"{base_url.rstrip('/')}/login", wait_until="domcontentloaded")

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()

    def expect_logged_in(self) -> None:
        expect(self.user_menu).to_be_visible()

    def expect_login_error(self, message: Optional[str] = None) -> None:
        expect(self.error_message).to_be_visible()
        if message:
            expect(self.error_message).to_contain_text(message)
