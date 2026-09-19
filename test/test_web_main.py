"""商城首页用例（真实浏览器）。"""
import pytest

from common.log_decorator import log_class
from pages.web.main_page import MainPage


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebMain:
    def test_open_sections(self, pw_page, config):
        page = MainPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert page.is_visible(MainPage.SEARCH_INPUT)
        assert page.cate_count() == 4
        assert page.brand_count() == 6
        assert page.count(MainPage.CAROUSEL_ITEM) == 5
        assert page.count(MainPage.TAB_ITEM) == 4

    def test_go_search(self, pw_page, config):
        page = MainPage(pw_page, base_url=config["web"]["base_url"])
        page.open().go_search()
        page.wait_for_url("**/product/search*")

    def test_go_cart_tab(self, pw_page, config):
        page = MainPage(pw_page, base_url=config["web"]["base_url"])
        page.open().go_tab("购物车")
        page.wait_for_url("**/cart/cart*")
