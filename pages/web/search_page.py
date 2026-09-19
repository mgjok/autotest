"""搜索页 PO：/pages/product/search。

结果条数对 Excel“搜索关键词”表 H5 列；空态见 is_empty_state()。
"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class SearchPage(BaseWebPage):
    PATH = "/pages/product/search"

    # -- 搜索栏 --
    SEARCH_BAR = ".search-input-wrap"
    SEARCH_ICON = ".icon-sousuo"
    # 搜索输入框（uni-input 套原生 input，直接定位原生 input 最稳）
    SEARCH_INPUT = ".search-bar input"
    # 右侧“搜索”按钮（uni-text，不是原生 button）
    SEARCH_BTN = ".search-action-btn"
    # -- 空态 --
    EMPTY_SECTION = ".empty-section"
    # 无记录时的空态提示，文案“暂无搜索记录”；有结果/跳页后消失
    EMPTY_TEXT = ".empty-text"
    # -- 列表结果（search_testdata.xlsx“搜索关键词”表 H5断言用） --
    # H5列表页调 portal /product/search（DB模糊），UI条数 == “H5列表期望数(DB)”列
    RESULT_ITEM = ".goods-item"
    # 列表到底文案；无结果时列表为空，只剩它显示“没有更多了”
    LIST_EMPTY = ".loading-more"

    def open(self) -> "SearchPage":
        self.goto(self.PATH)
        return self

    def search(self, keyword: str) -> "SearchPage":
        """填词并点搜索，成功后会跳到 /pages/product/list?keyword=...。"""
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BTN)
        return self

    def get_empty_text(self) -> str:
        if not self.is_visible(self.EMPTY_TEXT):
            return ""
        return self.get_text(self.EMPTY_TEXT).strip()

    def get_result_count(self) -> int:
        """列表结果条数，对应 Excel“H5列表期望数(DB)”列。"""
        try:
            return self.count(self.RESULT_ITEM)
        except Exception:
            return 0

    def is_empty_state(self) -> bool:
        """是否空态：无结果 + 空态信号可见。对应 Excel“是否空态=是”。

        搜索页看 EMPTY_TEXT/EMPTY_SECTION；列表页无空态图，
        看到底文案 LIST_EMPTY（“没有更多了”）。
        """
        if self.get_result_count() > 0:
            return False
        return (
            self.is_visible(self.EMPTY_TEXT)
            or self.is_visible(self.EMPTY_SECTION)
            or self.is_visible(self.LIST_EMPTY)
        )

    def clear_search_history(self) -> "SearchPage":
        """对应 Excel“搜索历史状态”HIST-01：清空 localStorage 搜索历史。"""
        self.execute_js(
            "() => { const ks = []; for (let i = 0; i < localStorage.length; i++) {"
            " const k = localStorage.key(i);"
            " if (/search|history/i.test(k)) ks.push(k); }"
            " ks.forEach((k) => localStorage.removeItem(k)); }"
        )
        return self
