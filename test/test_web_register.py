"""注册用例（真实浏览器）。"""
import pytest

from common.log_decorator import log_class
from pages.web.register_page import RegisterPage


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebRegister:
    def test_open_fields(self, pw_page, config):
        page = RegisterPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert page.count(".input-item input") == 4
        assert page.is_visible(RegisterPage.GET_CODE)
        assert page.is_visible(RegisterPage.SUBMIT)
        assert page.get_text(RegisterPage.WELCOME).strip() == "注册账号！"
        assert page.is_visible(RegisterPage.CODE_ROW)

    def test_empty_register_toast(self, pw_page, config):
        page = RegisterPage(pw_page, base_url=config["web"]["base_url"])
        page.open().click(RegisterPage.SUBMIT)
        assert page.get_toast_text() == "请输入用户名"

    def test_qrcode_visible(self, pw_page, config):
        page = RegisterPage(pw_page, base_url=config["web"]["base_url"])
        page.open_qrcode()
        page.sleep(1500)  # 二维码异步生成，直接断言会偶发失败
        assert page.is_visible(RegisterPage.QR_IMG)

    def test_register_success(self, pw_page, config):
        import time

        ms = str(int(time.time() * 1000))
        page = RegisterPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        page.fill(RegisterPage.USERNAME, "e2e" + ms[-6:])
        page.fill(RegisterPage.PASSWORD, "test123456")
        code = page.request_auth_code("134" + ms[-8:])
        assert len(code) >= 4
        assert "后重试" in page.get_text(RegisterPage.GET_CODE)
        page.fill(RegisterPage.CAPTCHA, code)
        page.click(RegisterPage.SUBMIT)
        page.wait_for_url("**/public/login*")
