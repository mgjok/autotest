"""date/ 测试数据目录（命名沿用历史目录名，作用等同常规 data/testdata）。

内容：
- search_testdata.xlsx：唯一数据源，20 个 sheet：
  搜索/登录注册/地址/下单/优惠券/订单/商品/权限/地址管理/资产联动/
  购物车联动/商品详情/我的页/SKU基准/页面UI基准/多商品业务流。
  用例一律读本目录副本。

用例取值示例：
    from date import SEARCH_DATA_XLSX, load_product_base
    import openpyxl
    wb = openpyxl.load_workbook(SEARCH_DATA_XLSX, data_only=True)
    rows = list(wb["搜索关键词"].iter_rows(min_row=2, values_only=True))
"""
from __future__ import annotations

import os
from typing import Any

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# 全量数据簿（含20个sheet：搜索关键词/…/SKU基准/页面UI基准/多商品业务流）
SEARCH_DATA_XLSX = os.path.join(DATA_DIR, "search_testdata.xlsx")

# 各sheet名常量，避免用例里散落硬编码中文串
SHEET_SEARCH_KW = "搜索关键词"
SHEET_SEARCH_HIST = "搜索历史状态"
SHEET_PRODUCT_BASE = "商品基准"
SHEET_ADMIN_LOGIN = "后台登录"
SHEET_FRONT_LOGIN = "前台登录注册"
SHEET_ADDRESS = "收货地址"
SHEET_CART_ORDER = "加购下单组合"
SHEET_COUPON = "优惠券"
SHEET_ORDER_STATUS = "订单状态"
SHEET_PRODUCT_MGMT = "后台商品管理"
SHEET_PERMISSION = "权限隔离"
# -- 新增：会员中心/商品详情/购物车联动 --
SHEET_ADDRESS_MGMT = "收货地址管理"
SHEET_ASSET_LINK = "会员资产联动"
SHEET_CART_LINK = "购物车联动"
SHEET_PRODUCT_DETAIL = "商品详情页"
SHEET_USER_FEATURES = "我的页功能"
# -- v2补全：SKU基准/页面UI基准（覆盖pages/web硬编码断言） --
SHEET_SKU_BASE = "SKU基准"
SHEET_PAGE_UI = "页面UI基准"
# -- v3补全：多商品业务流（加购/收藏/足迹/结算/SKU联动） --
SHEET_MIX_FLOW = "多商品业务流"


# ========== 通用读取工具 ==========
def _load_sheet(sheet_name: str) -> list[dict[str, Any]]:
    """读取指定 sheet 所有行（跳过表头），返回字典列表。"""
    import openpyxl
    wb = openpyxl.load_workbook(SEARCH_DATA_XLSX, data_only=True)
    ws = wb[sheet_name]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or all(v is None for v in r):
            continue
        rows.append(dict(zip(headers, r)))
    return rows


# ========== 各模块数据加载器 ==========
def load_address_cases() -> list[dict[str, Any]]:
    """收货地址 sheet：case_id, 操作, 备注, HTTP, code, 需求ID, 备注。"""
    return _load_sheet(SHEET_ADDRESS)


def load_cart_order_cases() -> list[dict[str, Any]]:
    """加购下单组合 sheet：case_id, productId, productSkuId, quantity, add, confirm, 需求ID, 备注。"""
    return _load_sheet(SHEET_CART_ORDER)


def load_coupon_cases() -> list[dict[str, Any]]:
    """优惠券 sheet：case_id, 操作, couponId, HTTP, code, 需求ID, 备注。"""
    return _load_sheet(SHEET_COUPON)


def load_order_status_cases() -> list[dict[str, Any]]:
    """订单状态 sheet：case_id, status, 说明, HTTP, code, total(test), 需求ID。"""
    return _load_sheet(SHEET_ORDER_STATUS)


def load_product_mgmt_cases() -> list[dict[str, Any]]:
    """后台商品管理 sheet：case_id, 操作, 条件, HTTP, code, 预期结果, 需求ID, 备注。"""
    return _load_sheet(SHEET_PRODUCT_MGMT)


def load_permission_cases() -> list[dict[str, Any]]:
    """权限隔离 sheet：case_id, 角色, 操作, product/list, order/list, 需求ID, 备注。"""
    return _load_sheet(SHEET_PERMISSION)


def load_front_login_cases() -> list[dict[str, Any]]:
    """前台登录注册 sheet：case_id, username, password, HTTP, code, 需求ID, 备注。"""
    return _load_sheet(SHEET_FRONT_LOGIN)


def load_admin_login_cases() -> list[dict[str, Any]]:
    """后台登录 sheet：case_id, username, password, HTTP, code, 需求ID, 备注。"""
    return _load_sheet(SHEET_ADMIN_LOGIN)


def load_product_base() -> list[dict[str, Any]]:
    """商品基准 sheet：product_id, name, price, stock, 命中关键词, sku_id, brand, 用途。"""
    return _load_sheet(SHEET_PRODUCT_BASE)


# ========== 新增：会员中心 / 商品详情 / 购物车联动 ==========
def load_address_mgmt_cases() -> list[dict[str, Any]]:
    """收货地址管理 sheet：case_id, action, name, phone, zip_code, region, detail, is_default, expected_toast, desc。"""
    return _load_sheet(SHEET_ADDRESS_MGMT)


def load_asset_link_cases() -> list[dict[str, Any]]:
    """会员资产联动 sheet：case_id, feature, product_id, product_name, action, expected_state, desc。"""
    return _load_sheet(SHEET_ASSET_LINK)


def load_cart_link_cases() -> list[dict[str, Any]]:
    """购物车联动 sheet：case_id, product_id, sku_id, quantity, action, expected, expected_toast, expected_count, desc。"""
    return _load_sheet(SHEET_CART_LINK)


def load_product_detail_cases() -> list[dict[str, Any]]:
    """商品详情页 sheet：case_id, product_id, product_name, action, expected, expected_price, desc。"""
    return _load_sheet(SHEET_PRODUCT_DETAIL)


def load_user_feature_cases() -> list[dict[str, Any]]:
    """我的页功能 sheet：case_id, action, expected, expected_url, desc。"""
    return _load_sheet(SHEET_USER_FEATURES)


# ========== v2补全：SKU基准 / 页面UI基准 / 搜索 ==========
def load_sku_base() -> list[dict[str, Any]]:
    """SKU基准 sheet：product_id, product_name, sku_id, spec_desc, price, stock, 用途。"""
    return _load_sheet(SHEET_SKU_BASE)


def load_page_ui_cases() -> list[dict[str, Any]]:
    """页面UI基准 sheet：case_id, page, 用例文件, check_item, selector_or_method, expected, expected_url, 需求ID, 备注。"""
    return _load_sheet(SHEET_PAGE_UI)


def load_search_kw_cases() -> list[dict[str, Any]]:
    """搜索关键词 sheet：case_id, keyword, 需求ID, H5列表期望数(DB), ES期望数, 是否空态, 用例映射, 备注。"""
    return _load_sheet(SHEET_SEARCH_KW)


def load_search_hist_cases() -> list[dict[str, Any]]:
    """搜索历史状态 sheet：state_id, 前置条件, 期望空态文案, 需求ID, 备注。"""
    return _load_sheet(SHEET_SEARCH_HIST)


def load_mix_cases() -> list[dict[str, Any]]:
    """多商品业务流 sheet：case_id, action, params(JSON), expected, priority, design_method, desc。"""
    return _load_sheet(SHEET_MIX_FLOW)


def load_sku_products() -> list[dict[str, Any]]:
    """workflow用SKU商品：商品基准中用途含加购/联动基准的行，含product_id/name。

    供 test_web_product_workflow.py 的 SKU_PRODUCTS 参数化使用。
    """
    try:
        base = load_product_base()
    except Exception:
        return []
    out = []
    for r in base:
        use = str(r.get("用途") or "")
        if "加购" in use or "联动基准" in use or "详情默认" in use:
            # 统一成 workflow 需要的 product_id/name 结构
            out.append({"product_id": r.get("product_id"), "name": r.get("name")})
    # 兜底：至少返回26/44，避免空参数化导致用例跳过
    if not out and base:
        out = [{"product_id": r.get("product_id"), "name": r.get("name")} for r in base[:2]]
    return out


# 兼容老用例：test_web_product_workflow.py 直接 import SKU_PRODUCTS
try:
    SKU_PRODUCTS = load_sku_products()
except Exception:  # pragma: no cover
    SKU_PRODUCTS = []
