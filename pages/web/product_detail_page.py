"""商品详情页 PO：/pages/product/product?id={id}。

动作：SKU 选择、加购、立即购买（跳创建订单页）、收藏/关注、领券。
未登录收藏/关注弹登录引导。
"""
from __future__ import annotations

from common.base_web_page import BaseWebPage


class ProductDetailPage(BaseWebPage):
    PATH = "/pages/product/product"

    # -- 基础信息 --
    TITLE = ".uni-page-head__title"  # 顶部导航标题
    PRODUCT_TITLE = ".introduce-section .title"  # 商品名
    PRICE = ".price-box .price"  # 当前价格
    ORIGINAL_PRICE = ".price-box .original-price"  # 划线价
    SALES = ".sales"  # 销量
    COLLECT_BTN = ".page-bottom .p-b-btn >> nth=2"  # 收藏按钮（底部栏第3个图标）
    COLLECTED = ".page-bottom .p-b-btn >> nth=2"  # 已收藏状态（同按钮）
    CART_BADGE = ".cart-badge"  # 购物车角标数量

    # -- 轮播 --
    SWIPER = ".goods-swiper"
    SWIPER_ITEM = ".swiper-item"

    # -- SKU 选择弹窗（点规格行弹出；选项行 .attr-list，值 .tit，确定 .btn）
    # 注意：页面同时存在“参数”弹窗（.layer.attr-content.no-padding），需用 :not 区分
    SKU_ROW = ".c-list > .c-row.b-b >> nth=0"  # “购买类型”规格行
    SKU_DRAWER = ".popup .layer.attr-content:not(.no-padding)"  # SKU 弹窗层
    SKU_SPEC_ITEM = f"{SKU_DRAWER} .attr-list"  # 规格项（颜色/容量/版本…）
    SKU_SPEC_VALUE = ".tit"  # 规格值（可点击）
    SKU_SELECTED = f"{SKU_DRAWER} .selected"  # 已选文案
    SKU_CONFIRM_BTN = f"{SKU_DRAWER} .btn"  # “完成”按钮
    SKU_CLOSE_BTN = ".popup .mask:visible"  # 遮罩（点击关闭）
    SKU_PRICE = f"{SKU_DRAWER} .right .price"  # 弹窗内当前SKU价格

    # -- 操作栏（底部固定：nth=0 立即购买，nth=1 加入购物车） --
    SERVICE_BTN = ".service-btn"  # "客服"
    SHOP_BTN = ".shop-btn"  # "进店"
    ADD_CART_BTN = ".action-btn-group .action-btn >> nth=1"  # "加入购物车"
    BUY_NOW_BTN = ".action-btn-group .action-btn >> nth=0"  # "立即购买"

    # -- 促销/优惠券 --
    PROMOTION_TAG = ".promotion-tag"
    COUPON_LIST = ".coupon-list"
    COUPON_ITEM = ".coupon-item"
    COUPON_RECEIVE_BTN = ".receive-btn"  # "领取"

    # -- 详情/参数/评价 tab --
    DETAIL_TAB = "text=详情"
    PARAM_TAB = "text=参数"
    COMMENT_TAB = "text=评价"

    # -- 通用 --
    TOAST = ".uni-simple-toast__text"
    MODAL = ".uni-modal"
    MODAL_CONFIRM = ".uni-modal .uni-modal__btn_primary"
    MODAL_CANCEL = ".uni-modal .uni-modal__btn_default"

    def __init__(self, page, base_url: str = "", timeout_ms: int = 10000):
        super().__init__(page, base_url, timeout_ms)
        self._product_id: int | None = None

    def open(self, product_id: int) -> "ProductDetailPage":
        """打开指定商品详情页。

        同路由 hash 跳转不会重新渲染（如商品A→商品B），故 goto 后 reload
        强制按当前 hash 重载，保证内容与 product_id 一致。
        """
        self._product_id = product_id
        self.goto(f"{self.PATH}?id={product_id}")
        self.reload()
        return self

    def wait_for_load(self) -> "ProductDetailPage":
        """等待页面加载完成（价格出现即视为加载完成）。"""
        self.wait_for(self.PRICE)
        return self

    def get_product_id(self) -> int | None:
        return self._product_id

    def get_title(self) -> str:
        return self.get_text(self.TITLE).strip()

    def get_price(self) -> str:
        return self.get_text(self.PRICE).strip()

    def price_amount(self) -> float:
        """当前展示价格（数值），用于 SKU 切换价格联动断言。"""
        import re

        m = re.search(r"[0-9]+(?:\.[0-9]+)?", self.get_price() or "")
        return float(m.group()) if m else -1.0

    # -- SKU 选择 --
    def open_sku_drawer(self) -> "ProductDetailPage":
        """点规格行打开 SKU 弹窗。"""
        self.click(self.SKU_ROW)
        self.wait_for(self.SKU_DRAWER)
        return self

    def close_sku_drawer(self) -> "ProductDetailPage":
        """关闭 SKU 弹窗。"""
        if self.is_visible(self.SKU_DRAWER):
            self.click(self.SKU_CLOSE_BTN)
        return self

    def select_sku_spec(self, spec_index: int, value_index: int) -> "ProductDetailPage":
        """选择第 spec_index 个规格的第 value_index 个值（0 起算）。"""
        self.click(f"{self.SKU_SPEC_ITEM} >> nth={spec_index} >> {self.SKU_SPEC_VALUE} >> nth={value_index}")
        return self

    def confirm_sku(self) -> "ProductDetailPage":
        """点击 SKU 弹窗的确定按钮。"""
        self.click(self.SKU_CONFIRM_BTN)
        return self

    def sku_drawer_price_amount(self) -> float:
        """SKU 弹窗内当前价格（数值），用于规格切换价格联动断言。"""
        import re

        m = re.search(r"[0-9]+(?:\.[0-9]+)?", self.get_text(self.SKU_PRICE) or "")
        return float(m.group()) if m else -1.0

    # -- 加入购物车 --
    def add_to_cart(self, specs: list[tuple[int, int]] | None = None) -> "ProductDetailPage":
        """加购（本应用加购成功无 toast，以购物车页校验为准）。

        :param specs: 传 [(规格序号, 值序号)] 则先在规格弹窗选好后点“完成”，
            再点“加入购物车”；不传则按默认规格直接加购。
        """
        if specs:
            self.open_sku_drawer()
            for spec_idx, val_idx in specs:
                self.select_sku_spec(spec_idx, val_idx)
            self.confirm_sku()
            self.sleep(800)
        self.click(self.ADD_CART_BTN)
        self.sleep(1000)
        return self

    def get_toast_text(self) -> str:
        return self.get_text(self.TOAST).strip()

    # -- 立即购买 --
    def buy_now(self, specs: list[tuple[int, int]] | None = None) -> "ProductDetailPage":
        """点立即购买。注意：当前前端仅支持从购物车下单，会 toast 提示并不跳转。"""
        self.click(self.BUY_NOW_BTN)
        return self

    def wait_for_order_page(self) -> "ProductDetailPage":
        """等待跳转到创建订单页。"""
        self.wait_for_url("**/order/createOrder*")
        return self

    # -- 收藏/取消收藏 --
    def toggle_collect(self) -> "ProductDetailPage":
        """点击收藏（未登录弹登录引导）。"""
        self.click(self.COLLECT_BTN)
        return self

    def is_collected(self) -> bool:
        return self.is_visible(self.COLLECTED)

    def wait_for_collect_toast(self) -> str:
        """等待收藏/取消收藏 toast 并返回文本。"""
        self.wait_for(self.TOAST)
        return self.get_text(self.TOAST).strip()

    # -- 关注品牌 --
    def toggle_brand_attention(self) -> "ProductDetailPage":
        """点击关注品牌按钮（通常在品牌区域）。"""
        # 视实际 UI 而定，这里占位
        return self

    # -- 优惠券领取 --
    def receive_coupon_nth(self, n: int = 0) -> "ProductDetailPage":
        """领取第 n 张优惠券。"""
        self.click(f"{self.COUPON_ITEM} >> nth={n} {self.COUPON_RECEIVE_BTN}")
        self.wait_for(self.TOAST)
        return self

    # -- 导航 --
    def go_cart(self) -> "ProductDetailPage":
        """点击购物车图标跳购物车页。"""
        # 视实际 UI 而定，通常在底部 tabBar 或右上角
        return self

    def go_shop(self) -> "ProductDetailPage":
        """点击进店跳店铺页。"""
        self.click(self.SHOP_BTN)
        return self

    def go_service(self) -> "ProductDetailPage":
        """点击客服。"""
        self.click(self.SERVICE_BTN)
        return self

    # -- 详情/参数/评价 tab 切换 --
    def click_detail_tab(self) -> "ProductDetailPage":
        self.click(self.DETAIL_TAB)
        return self

    def click_param_tab(self) -> "ProductDetailPage":
        self.click(self.PARAM_TAB)
        return self

    def click_comment_tab(self) -> "ProductDetailPage":
        self.click(self.COMMENT_TAB)
        return self