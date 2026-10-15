import allure
import pytest

from pages.baidu_page import BaiduPage


@allure.epic("Web UI")
@allure.feature("百度搜索")
@pytest.mark.regression
def test_baidu_search(page):

    baidu = BaiduPage(page)


    with allure.step("打开百度首页"):
        baidu.open()


    with allure.step("输入关键字并搜索"):
        baidu.search(
            "Playwright 自动化测试"
        )


    with allure.step("验证搜索结果"):
        baidu.verify_result(
            "Playwright"
        )