"""我的收藏页 PO：/pages/user/productCollection（需登录）。"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class ProductCollectionPage(BaseWebPage):
    PATH = "/pages/user/productCollection"

    TITLE = ".uni-page-head__title"
    CLEAR_BTN = 'text="清空"'
    MODAL = ".uni-modal:visible"
    MODAL_CONFIRM = ".uni-modal:visible .uni-modal__btn_primary"
    EMPTY_CONTENT = ".empty-content"
    LOAD_MORE = ".load-more"
    COLLECT_ITEM = ".hot-section .guess-item"
    ITEM_NAME = ".txt .title"

    def open(self) -> "ProductCollectionPage":
        """打开收藏页；reload 重置页面栈，避免头部“清空”事件派发到上一页。"""
        self.goto(self.PATH)
        self.reload()
        return self

    def item_names(self) -> list[str]:
        """各收藏卡片的商品名（精确到卡片标题）。"""
        names = []
        for item in self.find_all(self.COLLECT_ITEM):
            try:
                names.append(item.locator(self.ITEM_NAME).inner_text().strip())
            except Exception:
                pass
        return names

    def click_item(self, n: int = 0) -> "ProductCollectionPage":
        """点击第 n 个收藏卡片，进入商品详情。"""
        self.click(f"{self.COLLECT_ITEM} >> nth={n}")
        return self

    def clear(self, tries: int = 3) -> "ProductCollectionPage":
        """清空收藏：点清空→确认；带重试，防列表未渲染时首击丢失。"""
        for _ in range(tries):
            self.sleep(800)
            self.wait_for(self.CLEAR_BTN, state="visible")
            self.click(self.CLEAR_BTN)
            self.sleep(900)
            if not self.is_visible(self.MODAL):
                continue
            self.click(self.MODAL_CONFIRM)
            self.sleep(1500)
            if self.collect_count() == 0:
                break
        return self

    def collect_count(self) -> int:
        return self.count(self.COLLECT_ITEM)

    def get_product_names(self) -> list[str]:
        """收藏列表商品名，供 Excel 会员资产联动 product_name 断言。"""
        try:
            return [loc.inner_text().strip() for loc in self.find_all(self.COLLECT_ITEM)]
        except Exception:
            return []

    def is_empty_state(self) -> bool:
        try:
            self.wait_for(self.LOAD_MORE, state="visible")
        except Exception:
            pass
        return self.collect_count() == 0