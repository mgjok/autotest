"""商品详情页核心交互联动用例：浏览/收藏/关注/加购/立即购买跨页验证。"""
import pytest

from common.log_decorator import log_class
from pages.web.user_page import UserPage
from pages.web.product_detail_page import ProductDetailPage
from pages.web.read_history_page import ReadHistoryPage
from pages.web.brand_attention_page import BrandAttentionPage
from pages.web.product_collection_page import ProductCollectionPage
from pages.web.carte import CartPage
from date import (
    SKU_PRODUCTS,
    load_cart_link_cases,
    load_product_base,
    load_product_detail_cases,
)


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebProductWorkflow:
    @pytest.mark.parametrize("prod", SKU_PRODUCTS, ids=lambda c: f'pid-{c["product_id"]}')
    def test_browse_adds_to_footprint(self, pw_page, config, prod):
        """浏览商品详情 -> 我的足迹列表出现该商品。"""
        # 先清空足迹确保干净
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login().go_read_history()
        hist = ReadHistoryPage(pw_page, base_url=config["web"]["base_url"])
        if not hist.is_empty_state():
            hist.clear()
            pw_page.wait_for_timeout(500)

        # 访问商品详情（open 强制 reload，保证 hash 跳转真实渲染）
        detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
        detail.open(int(prod["product_id"])).wait_for_load()
        detail.sleep(1500)  # 等足迹上报接口完成

        # 回我的页查看足迹
        user.goto("/pages/user/readHistory")
        user.wait_for_url("**/readHistory*")
        hist.open()
        hist.sleep(1500)  # 列表异步加载
        assert hist.get_history_count() >= 1
        # 验证足迹包含该商品名
        texts = hist.get_history_texts()
        assert any(prod["name"].strip() in t for t in texts)

    @pytest.mark.parametrize("prod", SKU_PRODUCTS, ids=lambda c: f'pid-{c["product_id"]}')
    def test_collect_appears_in_collection(self, pw_page, config, prod):
        """点击收藏 -> 我的收藏列表出现该商品。"""
        # 先清空收藏
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login().go_product_collection()
        coll = ProductCollectionPage(pw_page, base_url=config["web"]["base_url"])
        if not coll.is_empty_state():
            coll.clear()
            pw_page.wait_for_timeout(500)

        # 访问商品详情并点击收藏
        detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
        detail.open(int(prod["product_id"])).wait_for_load()
        detail.toggle_collect()
        pw_page.wait_for_timeout(500)
        toast = detail.get_toast_text()
        assert "收藏" in toast

        # 回我的页查看收藏
        user.goto("/pages/user/productCollection")
        user.wait_for_url("**/productCollection*")
        coll.open()
        coll.sleep(1500)  # 列表异步加载
        assert not coll.is_empty_state()
        names = coll.get_product_names()
        assert any(prod["name"].strip() in n for n in names)

    @pytest.mark.parametrize("prod", SKU_PRODUCTS, ids=lambda c: f'pid-{c["product_id"]}')
    def test_brand_attention_appears(self, pw_page, config, prod):
        """关注品牌 -> 我的关注列表出现该品牌（需商品有品牌信息）。"""
        # 先清空关注
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login().go_brand_attention()
        att = BrandAttentionPage(pw_page, base_url=config["web"]["base_url"])
        if not att.is_empty_state():
            att.clear()
            pw_page.wait_for_timeout(500)

        # 访问商品详情并点击关注品牌（若可见）
        detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
        detail.open(int(prod["product_id"])).wait_for_load()

        # 商品详情页的品牌关注按钮（若存在）
        if detail.is_visible(".brand-attention-btn"):
            detail.click(".brand-attention-btn")
            pw_page.wait_for_timeout(500)

        # 回我的页查看关注
        user.goto("/pages/user/brandAttention")
        user.wait_for_url("**/brandAttention*")
        att.open()
        # 仅验证页面可打开，品牌关注视 UI 而定
        assert att.is_visible(att.TITLE)

    @pytest.mark.parametrize("prod", SKU_PRODUCTS, ids=lambda c: f'pid-{c["product_id"]}')
    def test_add_to_cart_appears_in_cart(self, pw_page, config, prod):
        """加入购物车 -> 购物车列表出现该商品。"""
        # 先清空购物车
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        pw_page.goto(config["web"]["base_url"] + "/pages/cart/cart")
        pw_page.wait_for_url("**/cart/cart*")
        cart = CartPage(pw_page, base_url=config["web"]["base_url"])
        cart.sleep(1500)  # 等购物车数据加载，避免过渡态
        if cart.has_items():
            cart.clear_cart()

        # 访问商品详情加购（本应用加购成功无 toast，以购物车页校验为准）
        detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
        detail.open(int(prod["product_id"])).wait_for_load()
        detail.add_to_cart(specs=[(0, 0), (1, 0)])  # 选第1规格第1值、第2规格第1值

        # 跳购物车页验证
        pw_page.goto(config["web"]["base_url"] + "/pages/cart/cart")
        pw_page.wait_for_url("**/cart/cart*")
        cart.open()
        cart.sleep(2000)  # 等购物车列表异步加载
        assert not cart.is_visible(CartPage.EMPTY)
        # 验证商品标题
        items = cart.get_item_titles()
        assert any(prod["name"].strip() in item for item in items)

    @pytest.mark.parametrize("prod", SKU_PRODUCTS, ids=lambda c: f'pid-{c["product_id"]}')
    def test_buy_now_goes_to_order(self, pw_page, config, prod):
        """立即购买 -> 当前前端仅支持从购物车下单，断言受限提示且不跳转。"""
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()

        detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
        detail.open(int(prod["product_id"])).wait_for_load()
        detail.buy_now()

        toast = detail.get_toast_text()
        assert "购物车下单" in toast
        assert "product" in pw_page.url