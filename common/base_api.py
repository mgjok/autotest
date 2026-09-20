"""API Base类：base_url/timeout 全部由 config['api'] 注入。"""
from __future__ import annotations

from typing import Any


class BaseApi:
    """API Page 父类：封装 url 拼接 + 超时，业务断言由子类与用例负责。

    用法（和 Web 侧保持一致）::

        api = PostApi(api_client, base_url=config["api"]["base_url"],
                      timeout_s=config["api"].get("timeout_s", 10))
    """

    def __init__(
        self,
        api_client: Any = None,
        base_url: str = "",
        timeout_s: int = 10,
        headers: dict | None = None,
    ):
        self.api_client = api_client
        self.base_url = (base_url or "").rstrip("/")
        self.timeout_s = timeout_s
        self.headers = {
            "Content-Type": "application/json",
        }
        if headers:
            self.headers.update(headers)
        # 如果传入的是 requests.Session，顺手把公共 header 挂上去
        try:
            if api_client is not None and hasattr(api_client, "headers"):
                api_client.headers.update(self.headers)
        except Exception:
            pass

    # -- URL 拼接 --
    def _url(self, path: str) -> str:
        """相对路径自动拼接 base_url，完整 URL 直接返回。"""
        if path.startswith("http"):
            return path
        return f"{self.base_url}{path}"

    # -- 请求封装（api_client 为 requests.Session 时直接可用）--
    def get(self, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout_s)
        return self.api_client.get(url, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout_s)
        return self.api_client.post(url, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout_s)
        return self.api_client.put(url, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout_s)
        return self.api_client.delete(url, **kwargs)