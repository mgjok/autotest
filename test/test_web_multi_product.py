"""多商品业务流用例（数据驱动，读 Excel“多商品业务流”sheet）。

覆盖：多商品加购/同SKU合并/删单条/数量增减/勾选重算/清空/去结算，
多商品收藏与取消、收藏跳详情、多商品足迹与清空、SKU 价格联动。
设计方法（ST/BS/BVA/EG/RL）与优先级见 Excel。
"""
from __future__ import annotations

import json
import re

import pytest

from common.log_decorator import log_class
from date import load_mix_cases, load_product_base
from pages.web.carte import CartPage
from pages.web.product_collection_page import ProductCollectionPage
from pages.web.product_detail_page import ProductDetailPage
from pages.web.read_history_page import ReadHistoryPage
from pages.web.user_page import UserPage


def _product(pid) -> dict:
    for r in load_product_base():
        if int(r["product_id"]) == int(pid):
            return r
    return {}


def _name(pid) -> str:
    return str(_product(pid).get("name") or "").strip()


def _price(pid) -> float:
    try:
        return float(_product(pid).get("price") or 0)
    except Exception:
        return 0.0


def _row_of(titles: list[str], pid) -> int:
    """按商品名找到购物车行号（列表顺序不稳定，动态定位）。"""
    for i, t in enumerate(titles):
        if _name(pid) in t:
            return i
    raise AssertionError(f"购物车未找到商品{pid} {_name(pid)}，实际条目:{titles}")


@pytest.mark.web
@pytest.mark.e2e
@log_class
class TestWebMultiProduct:
    """MIX-01~15：多商品/多SKU 业务流覆盖。"""

    # ---------- 通用步骤 ----------
    def _login(self, pw_page, config) -> UserPage:
        user = UserPage(pw_page, base_url=config["web"]["base_url"])
        user.open().ensure_login()
        return user

    def _open_cart(self, pw_page, config) -> CartPage:
        cart = CartPage(pw_page, base_url=config["web"]["base_url"])
        cart.open()
        cart.sleep(2500)  # 列表异步加载
        if cart.has_items():
            cart.wait_for(f"{CartPage.CART_ITEM} >> nth=0")
        return cart

    def _clean_cart(self, pw_page, config) -> CartPage:
        cart = self._open_cart(pw_page, config)
        if cart.has_items():
            cart.clear_cart()
            pw_page.wait_for_timeout(1500)
        return cart

    def _add_to_cart(self, pw_page, config, pid, specs=None) -> ProductDetailPage:
        detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
        detail.open(int(pid)).wait_for_load()
        detail.add_to_cart(specs)
        return detail

    def _collect(self, pw_page, config, pid, cancel: bool = False) -> ProductDetailPage:
        detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
        detail.open(int(pid)).wait_for_load()
        detail.toggle_collect()
        detail.sleep(900)
        toast = detail.get_toast_text()
        if cancel:
            assert "取消" in toast, f"期望取消收藏，实际toast[{toast}]"
        else:
            assert "收藏" in toast and "取消" not in toast, f"期望收藏成功，实际toast[{toast}]"
        return detail

    def _clean_collection(self, pw_page, config) -> ProductCollectionPage:
        coll = ProductCollectionPage(pw_page, base_url=config["web"]["base_url"])
        coll.open()
        coll.sleep(1500)
        if not coll.is_empty_state():
            coll.clear()
            pw_page.wait_for_timeout(1200)
        return coll

    def _clean_history(self, pw_page, config) -> ReadHistoryPage:
        hist = ReadHistoryPage(pw_page, base_url=config["web"]["base_url"])
        hist.open()
        hist.sleep(1500)
        if not hist.is_empty_state():
            hist.clear()
            pw_page.wait_for_timeout(1200)
        return hist

    # ---------- 数据驱动主流程 ----------
    @pytest.mark.parametrize("case", load_mix_cases(), ids=lambda c: f'{c["case_id"]}-{c["action"]}')
    def test_multi_product_flow(self, pw_page, config, case):
        action = case["action"]
        p = json.loads(case.get("params") or "{}")
        self._login(pw_page, config)

        if action == "cart_add_two":
            self._clean_cart(pw_page, config)
            for pid in p["pids"]:
                self._add_to_cart(pw_page, config, pid)
            cart = self._open_cart(pw_page, config)
            assert cart.count(CartPage.CART_ITEM) == len(p["pids"])
            titles = " | ".join(cart.get_item_titles())
            for pid in p["pids"]:
                assert _name(pid) in titles, f'购物车缺少商品{pid} {_name(pid)}'

        elif action == "cart_same_sku_merge":
            self._clean_cart(pw_page, config)
            for _ in range(int(p["times"])):
                self._add_to_cart(pw_page, config, p["pid"])
            cart = self._open_cart(pw_page, config)
            assert cart.count(CartPage.CART_ITEM) == 1
            assert cart.qty_value(0) == int(p["times"])

        elif action == "cart_delete_one":
            self._clean_cart(pw_page, config)
            for pid in p["pids"]:
                self._add_to_cart(pw_page, config, pid)
            cart = self._open_cart(pw_page, config)
            assert cart.count(CartPage.CART_ITEM) == 2
            del_nth = _row_of(cart.get_item_titles(), p["delete_pid"])
            cart.delete_item(del_nth)
            cart.sleep(1000)
            assert cart.count(CartPage.CART_ITEM) == 1
            titles = " | ".join(cart.get_item_titles())
            keep = [x for x in p["pids"] if x != p["delete_pid"]][0]
            assert _name(keep) in titles, "删除后应保留另一商品"
            assert _name(p["delete_pid"]) not in titles, "被删除商品不应还在购物车"

        elif action == "cart_qty_plus":
            self._clean_cart(pw_page, config)
            self._add_to_cart(pw_page, config, p["pid"])
            cart = self._open_cart(pw_page, config)
            assert cart.qty_value(0) == 1
            unit = cart.item_price_amount(0)
            cart.qty_plus(0)
            assert cart.qty_value(0) == 2
            assert abs(cart.get_total_amount() - unit * 2) < 0.01, "总价应=单价*数量"

        elif action == "cart_qty_minus":
            self._clean_cart(pw_page, config)
            for _ in range(int(p["merge_times"])):
                self._add_to_cart(pw_page, config, p["pid"])
            cart = self._open_cart(pw_page, config)
            assert cart.qty_value(0) == int(p["merge_times"])
            cart.qty_minus(0)
            assert cart.qty_value(0) == int(p["merge_times"]) - 1

        elif action == "cart_uncheck_total":
            self._clean_cart(pw_page, config)
            for pid in p["pids"]:
                self._add_to_cart(pw_page, config, pid)
            cart = self._open_cart(pw_page, config)
            before = cart.get_total_amount()
            assert before > 0, "未能解析购物车合计金额"
            uncheck_nth = _row_of(cart.get_item_titles(), p["uncheck_pid"])
            cart.toggle_item_check(uncheck_nth)
            after = cart.get_total_amount()
            assert abs((before - after) - _price(p["uncheck_pid"])) < 0.01, (
                f"取消勾选{p['uncheck_pid']}后总价应减少{_price(p['uncheck_pid'])}，实际减少{before - after}"
            )

        elif action == "cart_clear":
            self._clean_cart(pw_page, config)
            for pid in p["pids"]:
                self._add_to_cart(pw_page, config, pid)
            cart = self._open_cart(pw_page, config)
            assert cart.has_items()
            cart.clear_cart()
            cart.sleep(1500)
            assert cart.is_visible(CartPage.EMPTY)

        elif action == "cart_settle":
            self._clean_cart(pw_page, config)
            for pid in p["pids"]:
                self._add_to_cart(pw_page, config, pid)
            cart = self._open_cart(pw_page, config)
            assert cart.has_items(), "购物车应有商品"
            cart.wait_for(cart.SETTLE_BTN, state="visible")
            cart.go_settle()
            cart.wait_for_url("**/order/createOrder*")
            cart.sleep(2000)  # 订单页异步渲染，URL 变化早于内容
            cart.wait_for("text=提交订单")
            body = pw_page.inner_text("body") or ""
            for pid in p["pids"]:
                assert _name(pid) in body, f'创建订单页缺少商品{pid}'
            ids = re.search(r"cartIds=(\[[^\]]*\])", pw_page.url)
            assert ids and len(json.loads(ids.group(1))) == len(p["pids"])

        elif action == "sku_price_switch":
            detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
            detail.open(int(p["pid"])).wait_for_load()
            assert detail.price_amount() == float(p["p1"]), "默认SKU价格不符"
            detail.open_sku_drawer()
            for spec_idx, val_idx in p["specs2"]:
                detail.select_sku_spec(spec_idx, val_idx)
            detail.sleep(600)
            assert detail.sku_drawer_price_amount() == float(p["p2"]), "切换SKU后价格未联动"
            detail.confirm_sku()

        elif action == "sku_add_specified":
            self._clean_cart(pw_page, config)
            self._add_to_cart(pw_page, config, p["pid"], specs=[tuple(x) for x in p["specs"]])
            cart = self._open_cart(pw_page, config)
            assert cart.count(CartPage.CART_ITEM) == 1
            attrs = " | ".join(cart.get_item_attrs())
            assert "512GB" in attrs, f"购物车规格不匹配: {attrs}"
            assert abs(cart.item_price_amount(0) - 549) < 0.01, "指定SKU价格应为549"

        elif action == "collect_two":
            self._clean_collection(pw_page, config)
            for pid in p["pids"]:
                self._collect(pw_page, config, pid)
            coll = ProductCollectionPage(pw_page, base_url=config["web"]["base_url"])
            coll.open()
            coll.sleep(1500)
            assert coll.collect_count() >= 2
            names = " | ".join(coll.item_names())
            for pid in p["pids"]:
                assert _name(pid) in names, f'收藏列表缺少商品{pid}'

        elif action == "collect_cancel_one":
            self._clean_collection(pw_page, config)
            for pid in p["pids"]:
                self._collect(pw_page, config, pid)
            # 再进被取消商品的详情，点收藏=取消收藏（校验toast确为取消）
            self._collect(pw_page, config, p["cancel_pid"], cancel=True)
            coll = ProductCollectionPage(pw_page, base_url=config["web"]["base_url"])
            coll.open()
            coll.sleep(1500)
            names = " | ".join(coll.item_names())
            assert _name(p["cancel_pid"]) not in names, "取消收藏后列表仍存在该商品"
            keep = [x for x in p["pids"] if x != p["cancel_pid"]][0]
            assert _name(keep) in names, "取消一个后另一个应保留"

        elif action == "collect_tap_enter":
            self._clean_collection(pw_page, config)
            self._collect(pw_page, config, p["pid"])
            coll = ProductCollectionPage(pw_page, base_url=config["web"]["base_url"])
            coll.open()
            coll.sleep(1500)
            assert coll.collect_count() >= 1
            coll.click_item(0)
            coll.wait_for_url(f'**/product/product?id={p["pid"]}*')

        elif action == "history_two":
            self._clean_history(pw_page, config)
            for pid in p["pids"]:
                detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
                detail.open(int(pid)).wait_for_load()
                detail.sleep(1500)  # 等足迹上报
            hist = ReadHistoryPage(pw_page, base_url=config["web"]["base_url"])
            hist.open()
            hist.sleep(1500)
            texts = " | ".join(hist.get_history_texts())
            for pid in p["pids"]:
                assert _name(pid) in texts, f'足迹缺少商品{pid}'

        elif action == "history_clear":
            self._clean_history(pw_page, config)
            for pid in p["pids"]:
                detail = ProductDetailPage(pw_page, base_url=config["web"]["base_url"])
                detail.open(int(pid)).wait_for_load()
                detail.sleep(1500)
            hist = ReadHistoryPage(pw_page, base_url=config["web"]["base_url"])
            hist.open()
            hist.sleep(1500)
            assert hist.get_history_count() >= 1
            hist.clear()
            hist.sleep(1000)
            assert hist.is_empty_state()

        else:
            pytest.skip(f"动作 {action} 暂无自动化实现")
