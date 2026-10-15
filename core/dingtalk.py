"""钉钉自定义机器人通知（通过环境变量配置 webhook/secret）。"""
from __future__ import annotations
import hashlib
import hmac
import base64
import time
import urllib.parse
import os
import xml.etree.ElementTree as ET
import requests

def send_summary(exit_code: int, junit_path) -> None:
    webhook = os.getenv("DINGTALK_WEBHOOK", "").strip()
    if not webhook:
        print("[INFO] 未配置 DINGTALK_WEBHOOK，跳过通知")
        return
    passed = failed = errors = skipped = 0
    try:
        root = ET.parse(junit_path).getroot()
        suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
        for suite in suites:
            passed += int(suite.attrib.get("tests", 0))
            failed += int(suite.attrib.get("failures", 0))
            errors += int(suite.attrib.get("errors", 0))
            skipped += int(suite.attrib.get("skipped", 0))
        # tests 包含失败/跳过，调整为通过数
        passed = max(0, passed - failed - errors - skipped)
    except Exception:
        pass
    status = "通过" if exit_code == 0 else "失败"
    message = f"UI 回归测试{status}\n环境：{os.getenv('TEST_ENV', 'test')}\n通过：{passed}\n失败：{failed}\n错误：{errors}\n跳过：{skipped}\n退出码：{exit_code}"
    secret = os.getenv("DINGTALK_SECRET", "").strip()
    url = webhook
    if secret:
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{secret}"
        sign = base64.b64encode(hmac.new(secret.encode(), string_to_sign.encode(), digestmod=hashlib.sha256).digest()).decode()
        separator = "&" if "?" in url else "?"
        url += separator + urllib.parse.urlencode({"timestamp": timestamp, "sign": sign})
    response = requests.post(url, json={"msgtype": "text", "text": {"content": message}}, timeout=10)
    response.raise_for_status()
    payload = response.json()
    if payload.get("errcode", 0) != 0:
        raise RuntimeError(f"DingTalk API error: {payload}")
