"""配置加载：config/config.yaml，支持环境变量覆盖。"""
from __future__ import annotations

from pathlib import Path
import os

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

_CONFIG_PATH = Path(__file__).with_name("config.yaml")


def load_config(path: str | Path | None = None) -> dict:
    cfg_path = Path(path) if path else _CONFIG_PATH
    if yaml is None:
        raise RuntimeError("缺少 PyYAML，请 pip install pyyaml")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # 环境变量覆盖常用项
    if os.getenv("WEB_BASE_URL"):
        cfg.setdefault("web", {})["base_url"] = os.environ["WEB_BASE_URL"]
    if os.getenv("API_BASE_URL"):
        cfg.setdefault("api", {})["base_url"] = os.environ["API_BASE_URL"]
    if os.getenv("APPIUM_SERVER"):
        cfg.setdefault("app", {})["appium_server"] = os.environ["APPIUM_SERVER"]
    return cfg
