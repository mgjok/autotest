"""分类用例（真实浏览器）。"""
import pytest

from common.log_decorator import log_class
from pages.web.category import CategoryPage


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebCategory:
    def test_open_default(self, pw_page, config):
        page = CategoryPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert page.count(CategoryPage.FIRST_CATE) == 6
        assert page.is_visible(CategoryPage.SUB_LIST)
        assert page.get_active_name() == "服装"
        assert page.sub_names() == ["外套", "T恤", "休闲裤", "牛仔裤", "衬衫"]

    def test_select_first(self, pw_page, config):
        page = CategoryPage(pw_page, base_url=config["web"]["base_url"])
        page.open().select_first("手机数码")
        assert page.get_active_name() == "手机数码"
        assert page.sub_names() == ["手机通讯", "手机配件", "摄影摄像", "影音娱乐", "数码配件"]
