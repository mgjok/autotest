"""登录页 PO：/pages/public/login。

空提交 toast“请输入用户名和密码”；“马上注册”进注册页，“获取体验账号”进扫码页。
"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class LoginPage(BaseWebPage):
    PATH = "/pages/public/login"

    USERNAME = ".input-item >> nth=0 >> input"
    PASSWORD = ".input-item >> nth=1 >> input"
    SUBMIT = ".confirm-btn"  # uni-button“登录”
    DEMO = ".confirm-btn2"  # “获取体验账号”
    FORGET = ".forget-section"#忘记密码
    REGISTER_LINK = ".register-section uni-text"  # “马上注册”（点外层div不跳，必须点内层文字）
    TOAST = ".uni-simple-toast__text"
    WELCOME = ".welcome"  # “欢迎回来！”

    def open(self) -> "LoginPage":
        self.goto(self.PATH)
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password)
        self.click(self.SUBMIT)
        return self

    def get_toast_text(self) -> str:
        self.wait_for(self.TOAST)
        return self.get_text(self.TOAST).strip()

    def go_register(self) -> "LoginPage":
        """点“马上注册”，跳注册表单页。"""
        self.click(self.REGISTER_LINK)
        return self

    def go_demo(self) -> "LoginPage":
        """点“获取体验账号”，跳扫码页。"""
        self.click(self.DEMO)
        return self
