"""注册页 PO：/pages/public/register。

?mode=register 为表单（用户名/手机/密码/验证码），?mode=qrcode 为扫码页。
"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class RegisterPage(BaseWebPage):
    PATH = "/pages/public/register?mode=register"
    QR_PATH = "/pages/public/register?mode=qrcode"

    USERNAME = ".input-item >> nth=0 >> input"
    MOBILE = ".input-item >> nth=1 >> input"
    PASSWORD = ".input-item >> nth=2 >> input"
    CAPTCHA = ".input-item >> nth=3 >> input"
    GET_CODE = ".get-code-btn"
    SUBMIT = ".confirm-btn"  # uni-button“注册”
    TOAST = ".uni-simple-toast__text"
    QR_IMG = "img[src*='qrcode']"
    WELCOME = ".welcome"  # “注册账号！”
    CODE_ROW = ".auth-code-row"  # 验证码行

    def open(self) -> "RegisterPage":
        self.goto(self.PATH)
        return self

    def open_qrcode(self) -> "RegisterPage":
        self.goto(self.QR_PATH)
        return self

    def register(self, username: str, mobile: str, password: str, code: str) -> "RegisterPage":
        self.fill(self.USERNAME, username)
        self.fill(self.MOBILE, mobile)
        self.fill(self.PASSWORD, password)
        self.fill(self.CAPTCHA, code)
        self.click(self.SUBMIT)
        return self

    def get_toast_text(self) -> str:
        self.wait_for(self.TOAST)
        return self.get_text(self.TOAST).strip()

    def request_auth_code(self, mobile: str) -> str:
        """填手机号→点获取验证码→拦截 getAuthCode 接口，从返回 data 取码（测试环境直返）。"""
        self.fill(self.MOBILE, mobile)
        with self.page.expect_response("**/getAuthCode*", timeout=self.timeout_ms) as resp_info:
            self.click(self.GET_CODE)
        return str(resp_info.value.json().get("data", ""))
