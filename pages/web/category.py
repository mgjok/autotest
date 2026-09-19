"""分类页 PO：/pages/category/category。左侧一级（6 个），右侧二级随点击异步刷新。"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class CategoryPage(BaseWebPage):
    PATH = "/pages/category/category"

    # -- 左侧一级（服装 / 手机数码 / 家用电器 / 家具家装 / 汽车用品 / 电脑办公） --
    FIRST_CATE = ".f-item"
    FIRST_ACTIVE = ".f-item.active"
    # -- 右侧二级 --
    SUB_LIST = ".s-list"
    SUB_ITEM = ".s-item"

    def open(self) -> "CategoryPage":
        self.goto(self.PATH)
        # 分类数据异步加载，等左右两栏都出来再返回，否则读到空/残留
        self.wait_for(f"{self.FIRST_CATE} >> nth=0")
        self.wait_for(f"{self.SUB_ITEM} >> nth=0")
        return self

    def select_first(self, name: str) -> "CategoryPage":
        """点左侧一级分类，如“手机数码”，并等右侧二级列表刷新。

        右侧列表异步更新，不等会读到上一个分类的残留。
        """
        if self.get_active_name() == name:
            return self
        subs = self.sub_names()
        old = subs[0] if subs else ""
        self.click(f".f-item:has-text('{name}')")
        self.page.wait_for_function(
            "(old) => document.querySelector('.s-item')?.innerText?.trim() !== old",
            arg=old,
            timeout=self.timeout_ms,
        )
        return self

    def get_active_name(self) -> str:
        return self.get_text(self.FIRST_ACTIVE).strip()

    def sub_names(self) -> list[str]:
        return [loc.inner_text().strip() for loc in self.find_all(self.SUB_ITEM)]
