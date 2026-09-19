"""商城首页 PO：/。

含搜索框、轮播（5）、分类（4）、品牌（6）、底部 tab（4）。
注意：.guess-section 全页 3 处，品牌/猜你喜欢须带父级作用域定位。
"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class MainPage(BaseWebPage):
    PATH = "/"

    # -- 顶部栏 --
    SEARCH_BAR = ".uni-page-head-search"
    SEARCH_INPUT = ".uni-page-head-search input"
    MSG_BTN = ".uni-page-head-btn-red-dot"

    # -- 轮播（5 张） --
    CAROUSEL_ITEM = ".carousel .carousel-item"

    # -- 分类导航（专题 / 话题 / 优选 / 特惠，共 4 个） --
    CATE_ITEM = ".cate-section .cate-item"

    # -- 品牌制造商（第 1 个 .guess-section，小米/华为/苹果/海澜之家/OPPO/三星） --
    BRAND_ITEM = ".container > .guess-section >> nth=0 >> .guess-item"
    BRAND_NAME = ".container > .guess-section >> nth=0 >> .guess-item >> .title.clamp"

    # -- 秒杀专区 --
    SECKILL_ITEM = ".seckill-section .floor-item"
    SECKILL_PRICE = ".seckill-section .price"
    SECKILL_HOUR = ".hour.timer"
    SECKILL_MINUTE = ".minute.timer"
    SECKILL_SECOND = ".second.timer"

    # -- 人气推荐（4 个） --
    HOT_ITEM = ".hot-section .guess-item"

    # -- 猜你喜欢（第 3 个 .guess-section） --
    LIKE_ITEM = ".container > .guess-section >> nth=2 >> .guess-item"

    # -- 底部 tabbar（首页 / 分类 / 购物车 / 我的） --
    TAB_ITEM = ".uni-tabbar__item"

    def open(self) -> "MainPage":
        self.goto(self.PATH)
        # 首页品牌/猜你喜欢为异步加载，等首个品牌出现再返回，否则计数读到 0
        self.wait_for(f"{self.BRAND_ITEM} >> nth=0")
        return self

    def go_search(self) -> "MainPage":
        """点顶部搜索框，进 /pages/product/search。"""
        self.click(self.SEARCH_BAR)
        return self

    def go_tab(self, name: str) -> "MainPage":
        """点底部 tab，如 "首页" / "分类" / "购物车" / "我的”。"""
        self.click(f".uni-tabbar__item:has-text('{name}')")
        return self

    def cate_count(self) -> int:
        return self.count(self.CATE_ITEM)

    def brand_count(self) -> int:
        return self.count(self.BRAND_ITEM)
