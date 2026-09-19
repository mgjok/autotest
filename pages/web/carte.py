"""购物车页 PO：/pages/cart/cart。

未登录为空态；登录态支持：条目勾选、数量步进器、单条删除、清空、去结算。
"""
from __future__ import annotations

import re

from common.base_web_page import BaseWebPage


class CartPage(BaseWebPage):
    PATH = "/pages/cart/cart"

    # -- 未登录空态 --
    EMPTY = ".empty"
    EMPTY_TIPS = ".empty-tips"
    LOGIN_NAV = ".navigator"  # "去登陆"

    # -- 登录态（选择器来自真实 DOM 实测） --
    CART_LIST = ".cart-list"
    CART_ITEM = ".cart-item"
    ITEM_TITLE = ".item-right .title"
    ITEM_ATTR = ".item-right .attr"  # 规格文案（颜色/版本…）
    ITEM_PRICE = ".item-right .price"
    ITEM_CHECK = ".image-wrapper .checkbox"  # 条目勾选框（选中加 .checked）
    ITEM_DELETE = ".del-btn"  # 单条删除（icon-fork）
    QTY_MINUS = ".uni-numbox-minus"
    QTY_PLUS = ".uni-numbox-plus"
    QTY_INPUT = ".uni-numbox-value input"
    CLEAR_BTN = ".clear-btn"
    SETTLE_BTN = "text=去结算"
    MODAL = ".uni-modal:visible"
    MODAL_CONFIRM = ".uni-modal:visible .uni-modal__btn_primary"

    def open(self) -> "CartPage":
        self.goto(self.PATH)
        return self

    def get_empty_text(self) -> str:
        if not self.is_visible(self.EMPTY_TIPS):
            return ""
        return self.get_text(self.EMPTY_TIPS).strip()

    def go_login(self) -> "CartPage":
        """点“去登陆”，跳登录页。"""
        self.click(self.LOGIN_NAV)
        return self

    def get_item_titles(self) -> list[str]:
        """获取所有购物车商品的标题。"""
        titles = []
        for item in self.find_all(self.CART_ITEM):
            try:
                titles.append(item.locator(self.ITEM_TITLE).inner_text().strip())
            except Exception:
                pass
        return titles

    def get_item_attrs(self) -> list[str]:
        """获取所有条目的规格文案（如 颜色:金色;容量:16G;）。"""
        attrs = []
        for item in self.find_all(self.CART_ITEM):
            try:
                attrs.append(item.locator(self.ITEM_ATTR).inner_text().strip())
            except Exception:
                pass
        return attrs

    def item_price_amount(self, n: int = 0) -> float:
        """第 n 条商品单价（数值）。"""
        text = self.find_all(self.CART_ITEM)[n].locator(self.ITEM_PRICE).inner_text()
        m = re.search(r"[0-9]+(?:\.[0-9]+)?", text or "")
        return float(m.group()) if m else -1.0

    def get_total_amount(self) -> float:
        """底部合计金额（解析“¥xxxx元”）。"""
        body = self.page.inner_text("body") or ""
        found = re.findall(r"¥([0-9]+(?:\.[0-9]+)?)元", body)
        return float(found[-1]) if found else -1.0

    def has_items(self) -> bool:
        """购物车是否有商品（等数据加载后再判断，避免过渡态误判）。"""
        try:
            return self.count(self.CART_ITEM) > 0
        except Exception:
            return False

    def toggle_item_check(self, n: int = 0) -> "CartPage":
        """切换第 n 条的勾选状态。"""
        self.click(f"{self.CART_ITEM} >> nth={n} >> {self.ITEM_CHECK}")
        self.sleep(600)
        return self

    def qty_value(self, n: int = 0) -> int:
        """第 n 条的购买数量。"""
        try:
            return int(self.page.input_value(f"{self.CART_ITEM} >> nth={n} >> {self.QTY_INPUT}") or 0)
        except Exception:
            return -1

    def qty_plus(self, n: int = 0) -> "CartPage":
        """第 n 条数量 +1。"""
        self.click(f"{self.CART_ITEM} >> nth={n} >> {self.QTY_PLUS}")
        self.sleep(800)
        return self

    def qty_minus(self, n: int = 0) -> "CartPage":
        """第 n 条数量 -1。"""
        self.click(f"{self.CART_ITEM} >> nth={n} >> {self.QTY_MINUS}")
        self.sleep(800)
        return self

    def delete_item(self, n: int = 0) -> "CartPage":
        """删除第 n 条商品（弹窗自动确认）。"""
        self.click(f"{self.CART_ITEM} >> nth={n} >> {self.ITEM_DELETE}")
        self.sleep(600)
        if self.is_visible(self.MODAL):
            self.click(self.MODAL_CONFIRM)
        self.sleep(1200)
        return self

    def clear_cart(self) -> "CartPage":
        """清空购物车（仅在有商品时点击清空并确认）。"""
        if self.has_items() and self.is_visible(self.CLEAR_BTN):
            self.click(self.CLEAR_BTN)
            self.sleep(500)
            # 确认弹窗（只点当前可见弹窗，历史页面遗留的隐藏 modal 会触发 strict 冲突）
            if self.is_visible(self.MODAL):
                self.click(self.MODAL_CONFIRM)
        return self

    def go_settle(self) -> "CartPage":
        """点击“去结算”，跳创建订单页。"""
        self.click(self.SETTLE_BTN)
        return self