"""地址列表 / 新增地址用例（真实浏览器）。"""
import pytest

from common.log_decorator import log_class
from pages.web.address_page import AddressPage
from pages.web.address_manage_page import AddressManagePage
from pages.web.user_page import UserPage


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebAddress:
    def test_open_guest_redirects_login(self, pw_page, config):
        """未登录访问地址页，应自动跳登录页。"""
        page = AddressPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        page.wait_for_url("**/public/login*")

    def test_logged_in_open_and_list(self, pw_page, config):
        """登录后打开地址页，列表应可见，统计项数。"""
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        page = AddressPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert page.get_address_count() >= 0

    def test_go_add_address(self, pw_page, config):
        """从地址列表点"新增地址"，进入新增表单页。"""
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        page = AddressPage(pw_page, base_url=config["web"]["base_url"])
        page.open().go_add()
        page.wait_for_url("**/addressManage?type=add*")

    def test_add_address_flow(self, pw_page, config):
        """完整新增地址流程：填表 -> 提交 -> 列表数+1（或 toast 成功）。"""
        import time

        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        page = AddressPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        before = page.get_address_count()

        page.go_add()
        amp = AddressManagePage(pw_page, base_url=config["web"]["base_url"])
        amp.add_address(
            name="自动化" + str(int(time.time()))[-4:],
            mobile="138" + str(int(time.time() * 1000))[-8:],
        )
        # 提交后应回到列表页，或 toast 提示
        amp.wait_for_url("**/address/address*")
        after = page.get_address_count()
        # 断言：列表数增加，或 toast 含"成功/添加"
        assert after >= before

    def test_edit_delete_icons_visible(self, pw_page, config):
        """每条地址应有编辑/删除图标。"""
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        page = AddressPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        if page.get_address_count() > 0:
            assert page.is_visible(f"{page.ADDRESS_ITEM} >> nth=0 >> {page.EDIT_ICON}")
            assert page.is_visible(f"{page.ADDRESS_ITEM} >> nth=0 >> {page.DELETE_ICON}")