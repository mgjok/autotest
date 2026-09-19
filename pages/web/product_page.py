"""商品详情页 PO（旧版）：/pages/product/product?id=44。收藏/加购/购买需登录。"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class ProductPage(BaseWebPage):
    PATH = "/pages/product/product?id=44"

    # -- 顶部自定义导航栏 --
    NAV_TITLE = ".custom-navbar .nav-title"  # "详情展示"
    NAV_BACK = ".custom-navbar .nav-back"  # 返回
    # -- 轮播 --
    CAROUSEL = ".carousel > uni-swiper"
    CAROUSEL_ITEM = ".swiper-item"
    # -- 商品介绍区 --
    INTRO_SECTION = ".introduce-section"
    PRODUCT_TITLE = ".introduce-section > uni-text.title"  # 商品标题
    PRODUCT_SUBTITLE = ".introduce-section > uni-text.title2"  # 副标题/营销文案
    PRICE_BOX = ".introduce-section > .price-box"
    PRICE_NOW = ".price-box > uni-text.price"  # 现价（如 369）
    PRICE_MARKET = ".price-box > uni-text.m-price"  # 划线价（如 ¥369）
    BOT_ROW = ".introduce-section > .bot-row"  # 销量/库存/浏览量
    # -- 分享 --
    SHARE_SECTION = ".share-section"
    SHARE_BTN = ".share-section > .share-btn"  # "立即分享"
    # -- 规格/参数/优惠/服务 --
    C_LIST = ".c-list"
    SKU_ROW = ".c-list > .c-row.b-b >> nth=0"  # 购买类型（规格）
    SKU_SELECTED = ".c-row.b-b .con .selected-text >> nth=0"  # 当前选中的规格文案（第一个 .c-row 是购买类型）
    PARAM_ROW = ".c-list > .c-row.b-b >> nth=1"  # 商品参数
    COUPON_ROW = ".c-list > .c-row.b-b >> nth=2"  # 优惠券
    COUPON_GET = ".c-list > .c-row.b-b >> nth=2 .con.t-r"  # "领取优惠券"
    PROMO_ROW = ".c-list > .c-row.b-b >> nth=3"  # 促销活动
    SERVICE_ROW = ".c-list > .c-row.b-b >> nth=4"  # 服务
    # -- 评价 --
    EVA_SECTION = ".eva-section"
    EVA_COUNT = ".e-header > uni-text:nth-of-type(2)"  # (86)
    EVA_RATE = ".e-header > uni-text.tip"  # 好评率 100%
    EVA_ITEM = ".eva-box"
    # -- 品牌信息 --
    BRAND_INFO = ".brand-info"
    BRAND_NAME = ".brand-box > .title > uni-text:nth-of-type(1)"  # 三星
    # -- 图文详情 --
    DETAIL_DESC = ".detail-desc"
    # -- 底部操作栏 --
    BOTTOM = ".page-bottom"
    # 底部 3 个 icon 按钮（首页/购物车/收藏）都是 .p-b-btn
    HOME_BTN = ".page-bottom .p-b-btn >> nth=0"  # 首页
    CART_BTN = ".page-bottom .p-b-btn >> nth=1"  # 购物车
    FAV_BTN = ".page-bottom .p-b-btn >> nth=2"  # 收藏（非 navigator）
    # 立即购买 / 加入购物车（大按钮）
    BUY_NOW = ".action-btn-group > uni-button.action-btn >> nth=0"  # 立即购买
    ADD_CART = ".action-btn-group > uni-button.action-btn >> nth=1"  # 加入购物车
    # -- toast --
    TOAST = ".uni-simple-toast__text"

    def open(self, product_id: int = 44) -> "ProductPage":
        self.goto(f"/pages/product/product?id={product_id}")
        return self

    def get_title(self) -> str:
        return self.get_text(self.PRODUCT_TITLE).strip()

    def get_price(self) -> str:
        return self.get_text(self.PRICE_NOW).strip()

    def get_sku_text(self) -> str:
        return self.get_text(self.SKU_SELECTED).strip()

    def click_sku(self) -> "ProductPage":
        """点规格行，弹规格选择弹窗（若有）。"""
        self.click(self.SKU_ROW)
        return self

    def click_param(self) -> "ProductPage":
        self.click(self.PARAM_ROW)
        return self

    def click_coupon(self) -> "ProductPage":
        self.click(self.COUPON_GET)
        return self

    def click_fav(self) -> "ProductPage":
        """点收藏（心形图标）。"""
        self.click(self.FAV_BTN)
        return self

    def click_cart(self) -> "ProductPage":
        """点底部栏购物车图标，跳购物车页。"""
        self.click(self.CART_BTN)
        return self

    def click_buy_now(self) -> "ProductPage":
        self.click(self.BUY_NOW)
        return self

    def click_add_cart(self) -> "ProductPage":
        self.click(self.ADD_CART)
        return self

    def get_toast_text(self) -> str:
        self.wait_for(self.TOAST)
        return self.get_text(self.TOAST).strip()

    def eva_count(self) -> int:
        return self.count(self.EVA_ITEM)