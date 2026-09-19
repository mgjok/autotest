"""Web BasePage：基于 Playwright sync API 的常用操作封装。"""
from __future__ import annotations

import re
from typing import Any

# 元素快照默认选择器：只收敛“可交互 + 可定位”元素，过滤 div/span 噪音。
DEFAULT_SNAPSHOT_SELECTOR = (
    "a, button, input, select, textarea, "
    "[role=button], [role=link], [role=textbox], "
    "[onclick], [data-testid], [data-test-id], [data-test], "
    "[id], [name], [placeholder]"
)

_SNAPSHOT_JS = """(opts) => {
  const selector = opts.selector;
  const visibleOnly = opts.visible_only;
  const limit = opts.limit;
  const nodes = Array.from(document.querySelectorAll(selector)).slice(0, limit * 3);
  function isVisible(el) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return false;
    const s = window.getComputedStyle(el);
    if (s.display === "none" || s.visibility === "hidden" || s.opacity === "0") return false;
    return true;
  }
  function esc(s) {
    if (window.CSS && CSS.escape) return CSS.escape(s);
    return String(s).replace(/[^a-zA-Z0-9_-]/g, "\\\\$&");
  }
  function suggest(el) {
    if (el.id) return "#" + esc(el.id);
    const tid = el.getAttribute("data-testid") || el.getAttribute("data-test-id") || el.getAttribute("data-test");
    if (tid) return '[data-testid="' + tid + '"]';
    const tag = el.tagName.toLowerCase();
    const name = el.getAttribute("name");
    if (name && ["input", "select", "textarea", "button"].includes(tag)) return tag + '[name="' + name + '"]';
    const ph = el.getAttribute("placeholder");
    if (ph && ["input", "textarea"].includes(tag)) return tag + '[placeholder="' + ph + '"]';
    const txt = (el.innerText || el.textContent || "").trim().replace(/\\s+/g, " ").slice(0, 20);
    if (txt && (tag === "button" || tag === "a") && txt.length < 20) return "text=" + txt;
    const parts = [];
    let cur = el;
    while (cur && cur.nodeType === 1 && parts.length < 4) {
      let sel = cur.tagName.toLowerCase();
      if (cur.id) { sel += "#" + esc(cur.id); parts.unshift(sel); break; }
      const parent = cur.parentElement;
      if (parent) {
        const same = Array.from(parent.children).filter((c) => c.tagName === cur.tagName);
        if (same.length > 1) sel += ":nth-of-type(" + (same.indexOf(cur) + 1) + ")";
      }
      const cls = (cur.getAttribute("class") || "").trim().split(/\\s+/).filter(Boolean).slice(0, 2).map((c) => "." + esc(c)).join("");
      if (cls) sel += cls;
      parts.unshift(sel);
      cur = cur.parentElement;
      if (cur === document.body) { parts.unshift("body"); break; }
    }
    return parts.join(" > ");
  }
  const out = [];
  for (const el of nodes) {
    const vis = isVisible(el);
    if (visibleOnly && !vis) continue;
    const tag = el.tagName.toLowerCase();
    const txt = (el.innerText || el.textContent || "").trim().replace(/\\s+/g, " ").slice(0, 80);
    out.push({
      tag: tag,
      type: el.getAttribute("type") || "",
      text: txt,
      value: (el.value !== undefined && typeof el.value === "string") ? el.value.slice(0, 80) : "",
      placeholder: el.getAttribute("placeholder") || "",
      name: el.getAttribute("name") || "",
      id: el.id || "",
      classes: (el.getAttribute("class") || "").slice(0, 120),
      testid: el.getAttribute("data-testid") || el.getAttribute("data-test-id") || el.getAttribute("data-test") || "",
      role: el.getAttribute("role") || "",
      aria_label: el.getAttribute("aria-label") || "",
      href: el.getAttribute("href") || "",
      selector: suggest(el),
      visible: vis,
      enabled: !el.disabled,
    });
    if (out.length >= limit) break;
  }
  return out;
}"""


class BaseWebPage:
    """Web Page 父类：封装常用操作，业务断言由子类/Page 与用例负责。"""

    def __init__(self, page: Any, base_url: str = "", timeout_ms: int = 10000):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.timeout_ms = timeout_ms

    # -- 导航 --
    def goto(self, path: str = "/") -> None:
        """打开页面。相对路径自动拼接 base_url，完整 URL 直接打开。"""
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        self.page.goto(url, timeout=self.timeout_ms)

    def go_back(self) -> None:
        """浏览器后退。"""
        self.page.go_back(timeout=self.timeout_ms)

    def go_forward(self) -> None:
        """浏览器前进。"""
        self.page.go_forward(timeout=self.timeout_ms)

    def reload(self) -> None:
        """刷新当前页面。"""
        self.page.reload(timeout=self.timeout_ms)

    # -- 元素查找 --
    def find(self, selector: str) -> Any:
        """返回匹配的 Locator（懒加载，操作时才真正查找并自动等待）。

        选择器示例：\"#kw\" / \".menu-item\" / \"input[name='wd']\" /
        \"xpath=//button[@type='submit']\" / \"text=登录\"。
        """
        return self.page.locator(selector)

    def find_all(self, selector: str) -> list[Any]:
        """返回所有匹配的 Locator；无匹配时返回空列表。"""
        return self.page.locator(selector).all()

    def count(self, selector: str) -> int:
        """统计匹配元素个数，常用于断言列表行数。"""
        return self.page.locator(selector).count()

    def wait_for(self, selector: str, state: str = "visible") -> None:
        """等待元素进入指定状态：visible（默认）/ hidden / attached。"""
        self.page.locator(selector).wait_for(state=state, timeout=self.timeout_ms)

    # -- 元素操作 --
    def click(self, selector: str) -> None:
        """点击元素。"""
        self.find(selector).click(timeout=self.timeout_ms)

    def move_to(self, selector: str) -> None:
        """鼠标悬停（触发 hover 菜单 / tooltip）。"""
        self.page.hover(selector, timeout=self.timeout_ms)

    def fill(self, selector: str, text: str) -> None:
        """输入框填写文本（先清空原有内容）。"""
        self.find(selector).fill(text, timeout=self.timeout_ms)

    def press_key(self, key: str, selector: str | None = None) -> None:
        """模拟按键（如 Enter / Escape）。传 selector 则先聚焦该元素。"""
        if selector:
            self.page.press(selector, key, timeout=self.timeout_ms)
        else:
            self.page.keyboard.press(key)

    # -- 信息获取 --
    def get_text(self, selector: str) -> str:
        """获取元素文本；无文本返回空字符串。"""
        return self.page.text_content(selector, timeout=self.timeout_ms) or ""

    def get_title(self) -> str:
        """获取页面标题。"""
        return self.page.title()

    def get_url(self) -> str:
        """获取当前页面 URL，常用于断言跳转。"""
        return self.page.url

    def is_visible(self, selector: str) -> bool:
        """元素是否可见；不存在或异常时返回 False（适合 if 判断）。"""
        try:
            return self.page.is_visible(selector, timeout=self.timeout_ms)
        except Exception:
            return False

    # -- 等待 --
    def wait_for_url(self, url: str) -> None:
        """等待地址栏变为指定 URL（支持 ** 通配，登录跳页最常用）。"""
        self.page.wait_for_url(url, timeout=self.timeout_ms)

    def wait_for_loaded(self, state: str = "load") -> None:
        """等待页面加载状态：load / domcontentloaded / networkidle。"""
        self.page.wait_for_load_state(state, timeout=self.timeout_ms)

    def sleep(self, ms: int) -> None:
        """固定等待（毫秒）。优先用 wait_for_* 代替，避免拖慢用例。"""
        self.page.wait_for_timeout(ms)

    # -- 调试辅助 --
    def screenshot(self, path: str, full_page: bool = False) -> str:
        """页面截图，返回保存路径。"""
        self.page.screenshot(path=path, full_page=full_page, timeout=self.timeout_ms)
        return path

    def execute_js(self, script: str, arg: Any = None) -> Any:
        """执行 JS 并原样返回结果（Playwright 搞不定时兜底用）。"""
        if arg is None:
            return self.page.evaluate(script)
        return self.page.evaluate(script, arg)

    # -- 元素快照：辅助编写 Page 定位 --
    def snapshot_elements(
        self,
        selector: str = DEFAULT_SNAPSHOT_SELECTOR,
        visible_only: bool = True,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """抓取当前页元素快照（tag/文本/推荐选择器），供编写 Page 定位使用。

        :param selector: 默认只抓可交互元素；传 "*" 全量抓取。
        :param visible_only: 默认只返回可见元素。
        :param limit: 最多返回条数，默认 200。
        """
        try:
            opts = {"selector": selector, "visible_only": visible_only, "limit": limit}
            return self.execute_js(_SNAPSHOT_JS, opts) or []
        except AttributeError:
            return []

    def dump_for_pom(
        self,
        selector: str = DEFAULT_SNAPSHOT_SELECTOR,
        visible_only: bool = True,
        limit: int = 200,
    ) -> str:
        """将元素快照转成可直接粘进 Page 类的定位常量。"""
        rows = self.snapshot_elements(selector, visible_only, limit)
        lines: list[str] = []
        used: set[str] = set()
        for i, r in enumerate(rows):
            tag = str(r.get("tag") or "el")
            base = (
                r.get("id")
                or r.get("testid")
                or r.get("name")
                or r.get("aria_label")
                or r.get("placeholder")
                or r.get("text")
                or r.get("value")
                or f"{tag}_{i}"
            )
            name = re.sub(r"[^0-9A-Za-z]+", "_", str(base)).strip("_").upper()[:30]
            if not name or not name[0].isalpha():
                name = f"{tag.upper()}_{i}"
            orig, n = name, 2
            while name in used:
                name = f"{orig}_{n}"
                n += 1
            used.add(name)
            hint = str(r.get("text") or r.get("placeholder") or r.get("aria_label") or "")[:20]
            lines.append(f'{name} = "{r.get("selector")}"  # {tag} {hint}')
        return "\n".join(lines)

    def print_elements(
        self,
        selector: str = DEFAULT_SNAPSHOT_SELECTOR,
        visible_only: bool = True,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """打印元素快照并返回，供调试定位使用。"""
        rows = self.snapshot_elements(selector, visible_only, limit)
        for i, r in enumerate(rows):
            print(
                f'[{i}] {r.get("tag")} type={r.get("type")} '
                f'text="{r.get("text")}" selector={r.get("selector")} '
                f'visible={r.get("visible")} enabled={r.get("enabled")}'
            )
        return rows
