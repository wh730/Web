from playwright.sync_api import Page, expect
import allure


class BaiduPage:

    def __init__(self, page: Page):
        self.page = page


    @allure.step("打开百度首页")
    def open(self):
        self.page.goto(
            "https://www.baidu.com/",
            wait_until="domcontentloaded"
        )


    @allure.step("输入搜索关键词: {keyword}")
    def search(self, keyword: str):

        # 等待页面加载
        self.page.wait_for_load_state(
            "domcontentloaded"
        )


        # 百度搜索框兼容定位
        search_box = None


        # 第一种：新版百度输入框
        if self.page.locator(
            "textarea#chat-textarea"
        ).count() > 0:

            search_box = self.page.locator(
                "textarea#chat-textarea"
            )


        # 第二种：普通百度搜索框
        elif self.page.locator(
            "input[name='wd']"
        ).count() > 0:

            search_box = self.page.locator(
                "input[name='wd']"
            )


        # 第三种：老版本
        else:

            search_box = self.page.locator(
                "#kw"
            )


        # 等待输入框可用
        expect(
            search_box.first
        ).to_be_visible(
            timeout=10000
        )


        # 输入关键字
        search_box.first.fill(
            keyword
        )

        # 使用回车提交搜索，避免百度按钮隐藏问题
        search_box.first.press("Enter")

        self.page.wait_for_url(
            "**/s?*",
            timeout=10000
        )

    @allure.step("验证搜索结果: {keyword}")
    def verify_result(self, keyword):

        expect(
            self.page.locator("body")
        ).to_contain_text(
            keyword,
            timeout=10000
        )