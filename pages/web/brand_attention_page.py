"""我的关注页 PO：/pages/user/brandAttention（需登录）。"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class BrandAttentionPage(BaseWebPage):
    PATH = "/pages/user/brandAttention"

    TITLE = ".uni-page-head__title"
    CLEAR_BTN = 'text="清空"'
    MODAL = ".uni-modal:visible"
    MODAL_CONFIRM = ".uni-modal:visible .uni-modal__btn_primary"
    EMPTY_CONTENT = ".empty-content"
    LOAD_MORE = ".load-more"
    BRAND_ITEM = ".hot-section .guess-item"

    def open(self) -> "BrandAttentionPage":
        """打开关注页；reload 重置页面栈，避免头部“清空”事件派发到上一页。"""
        self.goto(self.PATH)
        self.reload()
        return self

    def clear(self, tries: int = 3) -> "BrandAttentionPage":
        """清空关注：点清空→确认；带重试，防列表未渲染时首击丢失。"""
        for _ in range(tries):
            self.sleep(800)
            self.wait_for(self.CLEAR_BTN, state="visible")
            self.click(self.CLEAR_BTN)
            self.sleep(900)
            if not self.is_visible(self.MODAL):
                continue
            self.click(self.MODAL_CONFIRM)
            self.sleep(1500)
            if self.brand_count() == 0:
                break
        return self

    def brand_count(self) -> int:
        return self.count(self.BRAND_ITEM)

    def get_brand_names(self) -> list[str]:
        """关注品牌名，供 Excel 会员资产联动 brand 断言。"""
        try:
            return [loc.inner_text().strip() for loc in self.find_all(self.BRAND_ITEM)]
        except Exception:
            return []

    def is_empty_state(self) -> bool:
        try:
            self.wait_for(self.LOAD_MORE, state="visible")
        except Exception:
            pass
        return self.brand_count() == 0