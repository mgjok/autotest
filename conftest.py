"""pytest 全局 fixture 入口：config / Web / App / API。"""
from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from common.logger import get_logger
from config.settings import load_config


log = get_logger("conftest")


@pytest.fixture(scope="session")
def config() -> dict:
    return load_config()


@pytest.fixture
def sample_data():
    # 兼容老用例
    return {"hello": "world"}



@pytest.fixture
def pw_page(config: dict):
    """真实 Playwright Page，仅 E2E 时启用：PLAYWRIGHT_E2E=1."""
    if os.getenv("PLAYWRIGHT_E2E") != "1":
        pytest.skip("非E2E模式，设置 PLAYWRIGHT_E2E=1 才跑真实浏览器")
    from playwright.sync_api import sync_playwright

    web_cfg = config.get("web", {})
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=web_cfg.get("headless", True))
        context = browser.new_context(base_url=web_cfg.get("base_url", ""))
        page = context.new_page()
        yield page
        context.close()
        browser.close()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败自动截图：只处理真实浏览器用例（pw_page）。

    截图存一份到 reports/shots/，同时 base64 内嵌进 HTML，
    --self-contained-html 单文件报告也能正常显示图片。
    """
    import base64

    report = yield
    if report.when == "call" and report.failed:
        page = item.funcargs.get("pw_page")
        if page is None:
            return report
        try:
            safe = re.sub(r'[<>:"/\\|?*\s]+', "_", item.name)
            shot = Path("reports") / "shots" / f"{safe}.png"
            shot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(shot))
            log.error("用例失败截图: %s", shot)
            try:
                from pytest_html import extras

                raw = base64.b64encode(shot.read_bytes()).decode("ascii")
                html = f'<a href="{shot.as_posix()}"><img src="data:image/png;base64,{raw}" style="max-width:800px"/></a>'
                report.extras = [*getattr(report, "extras", []), extras.html(html)]
            except Exception:
                pass
        except Exception as exc:  # 截图本身不能搞挂报告
            log.warning("失败截图失败: %s", exc)
    return report


@pytest.fixture
def app_driver(config: dict):
    """真实 Appium driver，仅 E2E 时启用：APPIUM_E2E=1."""
    if os.getenv("APPIUM_E2E") != "1":
        pytest.skip("非E2E模式，设置 APPIUM_E2E=1 才连真机/模拟器")
    try:
        from appium import webdriver
        from appium.options.common import AppiumOptions
    except ImportError:
        pytest.skip("未安装 Appium-Python-Client")
    app_cfg = config.get("app", {})
    options = AppiumOptions().load_capabilities(app_cfg.get("caps", {}))
    driver = webdriver.Remote(app_cfg.get("appium_server"), options=options)
    yield driver
    driver.quit()
