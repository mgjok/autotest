"""我的页用例（真实浏览器）。"""
import pytest

from common.log_decorator import log_class
from pages.web.user_page import UserPage


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebUser:
    def test_open_guest(self, pw_page, config):
        page = UserPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert page.get_username() == "游客"
        assert page.count(UserPage.STAT_ITEM) == 3
        assert page.is_visible(UserPage.VIP_OPEN)
        assert page.get_text(UserPage.VIP_TITLE).strip() == "黄金会员"
        assert page.count(UserPage.STAT_VALUE) == 3

    def test_orders_and_menus(self, pw_page, config):
        page = UserPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert page.order_names() == ["全部订单", "待付款", "待收货", "退款/售后"]
        assert page.menu_names() == ["地址管理", "我的足迹", "我的关注", "我的收藏", "我的评价", "设置"]
