"""购物车用例（真实浏览器）。"""
import pytest

from common.log_decorator import log_class
from pages.web.carte import CartPage


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebCart:
    def test_open_shows_empty(self, pw_page, config):
        page = CartPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert "空空如也" in page.get_empty_text()
        assert page.is_visible(CartPage.EMPTY)

    def test_go_login(self, pw_page, config):
        page = CartPage(pw_page, base_url=config["web"]["base_url"])
        page.open().go_login()
        page.wait_for_url("**/public/login*")
