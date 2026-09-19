"""登录用例"""
import pytest

from common.log_decorator import log_class
from pages.web.login_page import LoginPage


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebLogin:
    def test_open_fields(self, pw_page, config):
        page = LoginPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert page.is_visible(LoginPage.USERNAME)
        assert page.is_visible(LoginPage.PASSWORD)
        assert page.is_visible(LoginPage.SUBMIT)
        assert page.get_text(LoginPage.WELCOME).strip() == "欢迎回来！"

    def test_empty_login_toast(self, pw_page, config):
        page = LoginPage(pw_page, base_url=config["web"]["base_url"])
        page.open().click(LoginPage.SUBMIT)
        assert page.get_toast_text() == "请输入用户名和密码"

    def test_go_register(self, pw_page, config):
        page = LoginPage(pw_page, base_url=config["web"]["base_url"])
        page.open().go_register()
        page.wait_for_url("**/register?mode=register*")

    def test_go_demo_qrcode(self, pw_page, config):
        page = LoginPage(pw_page, base_url=config["web"]["base_url"])
        page.open().go_demo()
        page.wait_for_url("**/register?mode=qrcode*")
