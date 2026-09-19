"""新增/编辑地址页 PO：/pages/address/addressManage?type=add。"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class AddressManagePage(BaseWebPage):
    PATH = "/pages/address/addressManage?type=add"

    # -- 顶部栏 --
    TITLE = ".uni-page-head__title"  # “新增收货地址”
    BACK = ".uni-page-head-btn"  # 返回
    # -- 行（按 nth 顺序：姓名/手机/邮编/区域/详细/默认） --
    ROW = ".content > .row.b-b"
    NAME_INPUT = ".content > .row.b-b >> nth=0 >> input.uni-input-input"
    MOBILE_INPUT = ".content > .row.b-b >> nth=1 >> input.uni-input-input"
    ZIP_INPUT = ".content > .row.b-b >> nth=2 >> input.uni-input-input"
    AREA_INPUT = ".content > .row.b-b >> nth=3 >> input.uni-input-input"
    DETAIL_INPUT = ".content > .row.b-b >> nth=4 >> input.uni-input-input"
    DEFAULT_SWITCH = ".content > .row.default-row > uni-switch"
    # -- 提交 --
    SUBMIT = ".content > uni-button.add-btn"  # “提交”
    # -- toast --
    TOAST = ".uni-simple-toast__text"

    def open(self, mode: str = "add") -> "AddressManagePage":
        self.goto(self.PATH if mode == "add" else "/pages/address/addressManage?type=edit")
        return self

    def fill_name(self, name: str) -> "AddressManagePage":
        self.fill(self.NAME_INPUT, name)
        return self

    def fill_mobile(self, mobile: str) -> "AddressManagePage":
        self.fill(self.MOBILE_INPUT, mobile)
        return self

    def fill_zip(self, zip_code: str) -> "AddressManagePage":
        self.fill(self.ZIP_INPUT, zip_code)
        return self

    def fill_area(self, area: str) -> "AddressManagePage":
        self.fill(self.AREA_INPUT, area)
        return self

    def fill_detail(self, detail: str) -> "AddressManagePage":
        self.fill(self.DETAIL_INPUT, detail)
        return self

    def set_default(self, on: bool = True) -> "AddressManagePage":
        """uni-switch：点按 .uni-switch-input 切换状态。"""
        if on:
            self.click(f"{self.DEFAULT_SWITCH} .uni-switch-input")
        return self

    def submit(self) -> "AddressManagePage":
        self.click(self.SUBMIT)
        return self

    def add_address(
        self,
        name: str,
        mobile: str,
        zip_code: str = "518000",
        area: str = "广东省深圳市南山区",
        detail: str = "科兴科学园",
        default: bool = True,
    ) -> "AddressManagePage":
        """填表 + 可选设默认 + 提交。"""
        self.fill_name(name)
        self.fill_mobile(mobile)
        self.fill_zip(zip_code)
        self.fill_area(area)
        self.fill_detail(detail)
        if default:
            self.set_default(True)
        self.submit()
        return self

    def get_toast_text(self) -> str:
        self.wait_for(self.TOAST)
        return self.get_text(self.TOAST).strip()