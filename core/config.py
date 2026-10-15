from __future__ import annotations
import os
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load_config() -> dict:
    env_name = os.getenv("TEST_ENV", "test")
    path = ROOT / "config" / "environments.yaml"
    if not path.exists():
        path = ROOT / "config" / "environments.example.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    config = dict(data.get("default", {}))
    config.update(data.get(env_name, {}))
    config["base_url"] = os.getenv("BASE_URL", config.get("base_url", "http://127.0.0.1:8000"))
    config["headless"] = os.getenv("PW_HEADED", "0") != "1"
    config["timeout_ms"] = int(os.getenv("PW_TIMEOUT_MS", config.get("timeout_ms", 10000)))
    config["navigation_timeout_ms"] = int(os.getenv("PW_NAVIGATION_TIMEOUT_MS", config.get("navigation_timeout_ms", 20000)))
    return config
