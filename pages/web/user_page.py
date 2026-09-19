"""我的页 PO：/pages/user/user。

未登录用户名为“游客”；统计 3 项，订单 4 项，功能菜单 6 项。
"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class UserPage(BaseWebPage):
    PATH = "/pages/user/user"
    LOGIN_PATH = "/pages/public/login"

    # -- 用户头 --
    USERNAME = ".username"  # 未登录显示“游客”
    VIP_OPEN = ".b-btn"  # “立即开通”
    VIP_TITLE = ".tit"  # “黄金会员”

    # -- 统计（积分 / 成长值 / 优惠券） --
    STAT_ITEM = ".tj-item"
    STAT_VALUE = ".tj-item .num"  # 未登录都是“暂无”

    # -- 订单（全部订单 / 待付款 / 待收货 / 退款/售后） --
    ORDER_SECTION = ".order-section"
    ORDER_ITEM = ".order-item"

    # -- 功能列表（地址管理 / 足迹 / 关注 / 收藏 / 评价 / 设置） --
    MENU_SECTION = ".history-section"
    MENU_CELL = ".mix-list-cell"
    MENU_TITLE = ".mix-list-cell .cell-tit"

    def open(self) -> "UserPage":
        self.goto(self.PATH)
        return self

    def get_username(self) -> str:
        return self.get_text(self.USERNAME).strip()

    def order_names(self) -> list[str]:
        return [loc.inner_text().strip() for loc in self.find_all(self.ORDER_ITEM)]

    def menu_names(self) -> list[str]:
        return [loc.inner_text().strip() for loc in self.find_all(self.MENU_TITLE)]

    # -- 登录/登出辅助 --
    def is_logged_in(self) -> bool:
        """判断是否已登录（用户名不为“游客”）。"""
        return self.get_username() != "游客"

    def login(self, username: str, password: str) -> "UserPage":
        """若未登录则去登录页登录，登录后自动回到我的页。"""
        if self.is_logged_in():
            return self
        # 记录当前 URL，登录后自动跳回
        self.goto(self.LOGIN_PATH)
        self.fill(".input-item >> nth=0 >> input", username)
        self.fill(".input-item >> nth=1 >> input", password)
        self.click(".confirm-btn")
        # 登录成功会自动跳转回首页或我的页
        self.wait_for_url("**/pages/user/user*")
        return self

    def ensure_login(self, username: str = "test", password: str = "123456") -> "UserPage":
        """确保已登录；未登录则用默认凭据登录。"""
        if not self.is_logged_in():
            self.login(username, password)
        return self

    # -- 功能菜单跳转 --
    def go_address(self) -> "UserPage":
        """点“地址管理”，进 /pages/address/address。"""
        self.click(".mix-list-cell:has-text('地址管理')")
        return self

    def go_read_history(self) -> "UserPage":
        """点“我的足迹”，进 /pages/user/readHistory。"""
        self.click(".mix-list-cell:has-text('我的足迹')")
        return self

    def go_brand_attention(self) -> "UserPage":
        """点“我的关注”，进 /pages/user/brandAttention。"""
        self.click(".mix-list-cell:has-text('我的关注')")
        return self

    def go_product_collection(self) -> "UserPage":
        """点“我的收藏”，进 /pages/user/productCollection。"""
        self.click(".mix-list-cell:has-text('我的收藏')")
        return self

    def go_evaluation(self) -> "UserPage":
        """点“我的评价”，进评价页（若有）。"""
        self.click(".mix-list-cell:has-text('我的评价')")
        return self

    def go_settings(self) -> "UserPage":
        """点“设置”，进设置页。"""
        self.click(".mix-list-cell:has-text('设置')")
        return self

    # -- 使用 nth 索引的备用方法（避免文本定位不稳定） --
    def go_address_nth(self) -> "UserPage":
        self.click(".mix-list-cell >> nth=0")
        return self

    def go_read_history_nth(self) -> "UserPage":
        self.click(".mix-list-cell >> nth=1")
        return self

    def go_brand_attention_nth(self) -> "UserPage":
        self.click(".mix-list-cell >> nth=2")
        return self

    def go_product_collection_nth(self) -> "UserPage":
        self.click(".mix-list-cell >> nth=3")
        return self

    def go_evaluation_nth(self) -> "UserPage":
        self.click(".mix-list-cell >> nth=4")
        return self

    def go_settings_nth(self) -> "UserPage":
        self.click(".mix-list-cell >> nth=5")
        return self