"""我的页功能入口用例（真实浏览器，需登录；地址/资产联动走 Excel 数据驱动）。"""
import pytest

from common.log_decorator import log_class
from pages.web.user_page import UserPage
from pages.web.address_page import AddressPage
from pages.web.address_manage_page import AddressManagePage
from pages.web.read_history_page import ReadHistoryPage
from pages.web.brand_attention_page import BrandAttentionPage
from pages.web.product_detail_page import ProductDetailPage
from pages.web.product_collection_page import ProductCollectionPage
from date import (
    load_address_mgmt_cases,
    load_asset_link_cases,
    load_user_feature_cases,
    load_product_base,
)


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebUserFeatures:
    def test_user_page_guest(self, pw_page, config):
        """未登录我的页：用户名=游客，可见立即开通/统计/订单/菜单。"""
        page = UserPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        assert page.get_username() == "游客"
        assert page.is_visible(UserPage.VIP_OPEN)
        assert page.count(UserPage.STAT_ITEM) == 3
        assert page.order_names() == ["全部订单", "待付款", "待收货", "退款/售后"]
        assert page.menu_names() == [
            "地址管理",
            "我的足迹",
            "我的关注",
            "我的收藏",
            "我的评价",
            "设置",
        ]

    def test_user_page_logged_in(self, pw_page, config):
        """登录后我的页：显示用户名、积分/成长值、菜单可点。"""
        page = UserPage(pw_page, base_url=config["web"]["base_url"])
        page.open().ensure_login()
        assert page.get_username() != "游客"
        assert page.is_visible(UserPage.STAT_VALUE)

    def test_go_address_from_user(self, pw_page, config):
        """我的页点“地址管理”跳转。"""
        page = UserPage(pw_page, base_url=config["web"]["base_url"])
        page.open().ensure_login().go_address_nth()
        page.wait_for_url("**/address/address*")

    def test_read_history_guest_redirects_login(self, pw_page, config):
        """未登录访问足迹页，跳登录页。"""
        page = ReadHistoryPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        page.wait_for_url("**/public/login*")

    def test_read_history_logged_in_empty(self, pw_page, config):
        """登录后足迹页：先清空再验空态（用例自带清理，不依赖账号初始状态）。"""
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        page = ReadHistoryPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        if not page.is_empty_state():
            page.clear()
        assert page.is_visible(ReadHistoryPage.TITLE)
        assert page.is_empty_state()

    def test_brand_attention_logged_in_empty(self, pw_page, config):
        """登录后关注页：先清空再验空态。"""
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        page = BrandAttentionPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        page.sleep(1500)
        if not page.is_empty_state():
            page.clear()
        assert page.is_visible(BrandAttentionPage.TITLE)
        assert page.is_empty_state()

    def test_product_collection_logged_in_empty(self, pw_page, config):
        """登录后收藏页：先清空再验空态。"""
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        page = ProductCollectionPage(pw_page, base_url=config["web"]["base_url"])
        page.open()
        page.sleep(1500)
        if not page.is_empty_state():
            page.clear()
        assert page.is_visible(ProductCollectionPage.TITLE)
        assert page.is_empty_state()

    def test_address_list_and_count(self, pw_page, config):
        """登录后进入地址管理页，列表正常渲染（等异步加载后再计数）。"""
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login().go_address()

        addr = AddressPage(pw_page, base_url=config["web"]["base_url"])
        addr.wait_for_url("**/address/address*")
        addr.sleep(1500)  # 列表异步加载
        assert addr.is_visible(AddressPage.TITLE)
        assert addr.get_address_count() >= 1

    @pytest.mark.parametrize("case", load_address_mgmt_cases(), ids=lambda c: c["case_id"])
    def test_address_management_data_driven(self, pw_page, config, case):
        """基于 Excel 数据驱动测试地址管理（新增校验 / 编辑 / 删除 / 取消删除）。"""
        action = case.get("action") or ""
        expect_toast = (case.get("expected_toast") or "").strip()

        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login().go_address()

        addr = AddressPage(pw_page, base_url=config["web"]["base_url"])
        addr.wait_for_url("**/address/address*")
        addr.sleep(1500)  # 列表异步加载，避免计数/取图标时读到 0

        if action.startswith("add_"):
            before = addr.get_address_count()
            addr.go_add()
            amp = AddressManagePage(pw_page, base_url=config["web"]["base_url"])
            amp.wait_for_url("**/addressManage*")
            amp.fill_name(case.get("name") or "")
            amp.fill_mobile(case.get("phone") or "")
            amp.fill_zip(case.get("zip_code") or "")
            amp.fill_area(case.get("region") or "")
            amp.fill_detail(case.get("detail") or "")
            amp.submit()
            if expect_toast:
                toast = amp.get_toast_text()
                assert expect_toast in toast, f'{case["case_id"]} 期望toast[{expect_toast}] 实际[{toast}]'
            else:
                # 成功新增：实测无toast、自动回列表，断言条数+1
                amp.wait_for_url("**/pages/address/address")
                addr.sleep(2000)
                assert addr.get_address_count() >= before + 1, (
                    f'{case["case_id"]} 新增前{before}条，新增后应增加'
                )
            return

        if action == "edit_success":
            if addr.get_address_count() == 0:
                pytest.skip("无地址可编辑")
            addr.click(f"{AddressPage.ADDRESS_ITEM} >> nth=0 >> {AddressPage.EDIT_ICON}")
            amp = AddressManagePage(pw_page, base_url=config["web"]["base_url"])
            amp.wait_for_url("**/addressManage*")
            amp.fill_name(case.get("name") or "")
            amp.fill_mobile(case.get("phone") or "")
            amp.submit()
            if expect_toast:
                toast = amp.get_toast_text()
                assert expect_toast in toast, f'{case["case_id"]} 期望toast[{expect_toast}] 实际[{toast}]'
            else:
                # 编辑成功：实测无toast、自动回列表，断言新姓名出现
                amp.wait_for_url("**/pages/address/address")
                addr.sleep(2000)
                assert (case.get("name") or "") in addr.names()
            return

        if action in ("delete_success", "delete_cancel"):
            before = addr.get_address_count()
            if before == 0:
                pytest.skip("无地址可删除")
            addr.click(f"{AddressPage.ADDRESS_ITEM} >> nth=0 >> {AddressPage.DELETE_ICON}")
            addr.wait_for(AddressPage.MODAL)
            if action == "delete_success":
                addr.click(AddressPage.MODAL_CONFIRM)
                addr.sleep(2000)
                # 删除成功：实测无toast，断言条数-1
                assert addr.get_address_count() == before - 1
            else:
                addr.click(AddressPage.MODAL_CANCEL)
                addr.sleep(1500)
                assert addr.get_address_count() == before
            return

        pytest.skip(f"动作 {action} 暂未自动化（需默认地址状态断言）")

    @pytest.mark.parametrize("case", load_asset_link_cases(), ids=lambda c: c["case_id"])
    def test_asset_link_data_driven(self, pw_page, config, case):
        """基于 Excel 数据驱动测试会员资产联动（足迹/收藏/关注）。"""
        prod_id = int(case["product_id"])
        feature = case["feature"]
        action = case["action"]
        expected = case["expected_state"]

        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()

        if feature == "read_history":
            # 清空足迹
            user.go_read_history()
            hist = ReadHistoryPage(pw_page, base_url=config["web"]["base_url"])
            if not hist.is_empty_state():
                hist.clear()
                pw_page.wait_for_timeout(500)

            # 浏览商品（open 自带 reload，规避同路由 hash 跳转不渲染）
            detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
            detail.open(prod_id).wait_for_load()
            detail.sleep(1500)  # 等足迹上报接口完成

            # 回足迹页验证
            user.goto("/pages/user/readHistory")
            user.wait_for_url("**/readHistory*")
            hist.open()
            hist.sleep(1500)  # 列表异步加载
            assert hist.get_history_count() >= 1

        elif feature == "product_collection":
            # 清空收藏
            user.go_product_collection()
            coll = ProductCollectionPage(pw_page, base_url=config["web"]["base_url"])
            if not coll.is_empty_state():
                coll.clear()
                pw_page.wait_for_timeout(500)

            # 访问商品详情并收藏
            detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
            detail.open(prod_id).wait_for_load()
            detail.toggle_collect()
            toast = detail.get_toast_text()
            assert "收藏" in toast

            # 回收藏页验证
            user.goto("/pages/user/productCollection")
            user.wait_for_url("**/productCollection*")
            coll.open()
            coll.sleep(1500)  # 列表异步加载
            assert not coll.is_empty_state()

        elif feature == "brand_attention":
            # 清空关注
            user.go_brand_attention()
            att = BrandAttentionPage(pw_page, base_url=config["web"]["base_url"])
            if not att.is_empty_state():
                att.clear()
                pw_page.wait_for_timeout(500)

            # 访问商品详情
            detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
            detail.open(prod_id).wait_for_load()

            # 回关注页验证
            user.goto("/pages/user/brandAttention")
            user.wait_for_url("**/brandAttention*")
            att.open()
            assert att.is_visible(att.TITLE)

    @pytest.mark.parametrize("case", load_user_feature_cases(), ids=lambda c: c["case_id"])
    def test_user_feature_data_driven(self, pw_page, config, case):
        """基于 Excel 数据驱动测试我的页功能（登录/退出/订单入口/设置）。"""
        action = case["action"]
        expected = case["expected"]

        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open()

        if action == "open_guest":
            assert user.get_username() == "游客"
        elif action == "login":
            user.ensure_login()
            assert user.get_username() != "游客"
        elif action == "logout":
            user.ensure_login()
            # 退出登录（点击设置页退出；确认弹窗主按钮为 primary）
            user.go_settings_nth()
            pw_page.click("text=退出登录")
            if pw_page.is_visible(".uni-modal:visible"):
                pw_page.click(".uni-modal:visible .uni-modal__btn_primary")
            pw_page.wait_for_timeout(500)
            assert user.get_username() == "游客"
        elif action.startswith("click_order"):
            # 订单入口在订单区（.order-item），不在功能菜单区
            user.ensure_login()
            if action == "click_order_all":
                user.click(".order-item:has-text('全部订单')")
                user.wait_for_url("**/order/order*")
            elif action == "click_order_pending":
                user.click(".order-item:has-text('待付款')")
                user.wait_for_url("**/order/order*")
            elif action == "click_order_shipped":
                user.click(".order-item:has-text('待收货')")
                user.wait_for_url("**/order/order*")
            elif action == "click_order_refund":
                # 前端未实现：点击无跳转无toast（已实测），断言停留在我的页
                user.click(".order-item:has-text('退款/售后')")
                user.sleep(1000)
                assert "pages/user/user" in pw_page.url
        elif action == "click_settings":
            user.ensure_login()
            user.go_settings_nth()
            user.wait_for_url(case.get("expected_url") or "**/set/set*")