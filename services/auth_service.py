from playwright.sync_api import Page
from pages.login_page import LoginPage

class AuthService:
    """业务封装：把页面动作组合成可复用业务能力。"""
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def login_as(self, username: str, password: str) -> LoginPage:
        login_page = LoginPage(self.page)
        login_page.open(self.base_url)
        login_page.login(username, password)
        login_page.expect_logged_in()
        return login_page
