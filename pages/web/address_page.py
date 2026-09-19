"""地址列表页 PO：/pages/address/address（需登录，未登录跳登录页）。"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class AddressPage(BaseWebPage):
    PATH = "/pages/address/address"
    ADD_PATH = "/pages/address/addressManage?type=add"

    TITLE = ".uni-page-head__title"
    ADDRESS_ITEM = ".content.b-t > .list.b-b"
    ADDRESS_TEXT = ".address-box .address"
    NAME_TEXT = ".u-box .name"
    MOBILE_TEXT = ".u-box .mobile"
    DEFAULT_TAG = ".address-box .tag"
    EDIT_ICON = ".yticon.icon-bianji"
    DELETE_ICON = ".yticon.icon-iconfontshanchu1"
    ADD_BTN = ".content.b-t > uni-button.add-btn"
    TOAST = ".uni-simple-toast__text"
    MODAL = ".uni-modal:visible"
    MODAL_CONFIRM = ".uni-modal:visible .uni-modal__btn_primary"
    MODAL_CANCEL = ".uni-modal:visible .uni-modal__btn_default"

    def open(self) -> "AddressPage":
        self.goto(self.PATH)
        return self

    def go_add(self) -> "AddressPage":
        self.click(self.ADD_BTN)
        return self

    def get_address_count(self) -> int:
        try:
            return self.count(self.ADDRESS_ITEM)
        except Exception:
            return 0

    def address_count(self) -> int:
        return self.get_address_count()

    def names(self) -> list[str]:
        return [loc.inner_text().strip() for loc in self.find_all(self.NAME_TEXT)]

    def mobiles(self) -> list[str]:
        return [loc.inner_text().strip() for loc in self.find_all(self.MOBILE_TEXT)]

    def default_count(self) -> int:
        return self.count(self.DEFAULT_TAG)

    def delete_nth(self, n: int = 0) -> "AddressPage":
        self.click(f"{self.ADDRESS_ITEM} >> nth={n} >> {self.DELETE_ICON}")
        return self

    def get_toast_text(self) -> str:
        self.wait_for(self.TOAST)
        return self.get_text(self.TOAST).strip()