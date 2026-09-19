"""我的足迹页 PO：/pages/user/readHistory（需登录）。"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class ReadHistoryPage(BaseWebPage):
    PATH = "/pages/user/readHistory"

    TITLE = ".uni-page-head__title"
    CLEAR_BTN = 'text="清空"'
    MODAL = ".uni-modal:visible"
    MODAL_CONFIRM = ".uni-modal:visible .uni-modal__btn_primary"
    EMPTY_CONTENT = ".empty-content"
    LOAD_MORE = ".load-more"
    HISTORY_ITEM = ".hot-section .guess-item"

    def open(self) -> "ReadHistoryPage":
        """打开足迹页。

        同 hash 跳转会保留页面栈，uni-app H5 会把头部“清空”按钮事件
        派发到栈内上一页（实测跳设置页），故 goto 后 reload 重置为单页栈。
        """
        self.goto(self.PATH)
        self.reload()
        return self

    def clear(self, tries: int = 3) -> "ReadHistoryPage":
        """清空足迹：点清空→确认；带重试，防列表未渲染时首击丢失。"""
        for _ in range(tries):
            self.sleep(800)
            self.wait_for(self.CLEAR_BTN, state="visible")
            self.click(self.CLEAR_BTN)
            self.sleep(900)
            if not self.is_visible(self.MODAL):
                continue
            self.click(self.MODAL_CONFIRM)
            self.sleep(1500)
            if self.history_count() == 0:
                break
        return self

    def history_count(self) -> int:
        return self.count(self.HISTORY_ITEM)

    def get_history_count(self) -> int:
        """别名：兼容 test_web_product_workflow.py 调用。"""
        return self.history_count()

    def get_history_texts(self) -> list[str]:
        """足迹列表文本，供 Excel 会员资产联动 product_name 断言。"""
        try:
            return [loc.inner_text().strip() for loc in self.find_all(self.HISTORY_ITEM)]
        except Exception:
            return []

    def is_empty_state(self) -> bool:
        try:
            self.wait_for(self.LOAD_MORE, state="visible")
        except Exception:
            pass
        return self.history_count() == 0