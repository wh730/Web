from __future__ import annotations
import os
from pathlib import Path
import pytest
import allure
from dotenv import load_dotenv
from core.config import load_config

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

@pytest.fixture(scope="session")
def app_config():
    return load_config()

@pytest.fixture(scope="session", autouse=True)
def prepare_artifact_dirs():
    for path in (
        ROOT / "artifacts",
        ROOT / "artifacts" / "videos",
        ROOT / "artifacts" / "traces",
        ROOT / "reports" / "allure-results",
    ):
        path.mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, app_config):
    args = dict(browser_type_launch_args)
    args["headless"] = app_config.get("headless", True)
    return args

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    args = dict(browser_context_args)
    args.setdefault("viewport", {"width": 1440, "height": 900})
    # pytest-playwright 会为测试创建独立 context；关闭 context 时写入视频文件。
    args["record_video_dir"] = str(ROOT / "artifacts" / "videos")
    args["record_video_size"] = {"width": 1440, "height": 900}
    return args

@pytest.fixture(autouse=True)
def configure_page_timeouts(page, app_config):
    page.set_default_timeout(app_config["timeout_ms"])
    page.set_default_navigation_timeout(app_config["navigation_timeout_ms"])
    return page

@pytest.fixture
def test_credentials():
    worker = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    username = os.getenv(f"E2E_USERNAME_{worker}") or os.getenv("E2E_USERNAME", "")
    password = os.getenv(f"E2E_PASSWORD_{worker}") or os.getenv("E2E_PASSWORD", "")
    if not username or not password:
        pytest.skip("未配置 E2E_USERNAME/E2E_PASSWORD；跳过需要真实账号的用例")
    return username, password

@pytest.fixture(autouse=True)
def capture_diagnostics(page, request):
    """每条测试记录 Trace；失败时附加截图与 trace 到 Allure。"""
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in request.node.nodeid)[:120]
    trace_path = ROOT / "artifacts" / "traces" / f"{safe_name}.zip"
    page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield
    report = getattr(request.node, "rep_call", None)
    failed = bool(report and report.failed)
    if failed:
        screenshot_path = ROOT / "artifacts" / f"{safe_name}.png"
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
            allure.attach.file(str(screenshot_path), name="failure-screenshot",
                               attachment_type=allure.attachment_type.PNG)
        except Exception as exc:
            print(f"[WARN] screenshot capture failed: {exc}")
    try:
        page.context.tracing.stop(path=str(trace_path) if failed else None)
        if failed and trace_path.exists():
            allure.attach.file(str(trace_path), name="playwright-trace",
                               attachment_type="application/zip")
        # pytest-playwright 关闭 context 后会生成 webm，这里尝试挂载最近视频
        if failed:
            video_dir = ROOT / "artifacts" / "videos"
            videos = list(video_dir.glob("*.webm"))
            if videos:
                latest_video = max(videos, key=lambda x: x.stat().st_mtime)
                allure.attach.file(str(latest_video), name="failure-video",
                                   attachment_type="video/webm")
    except Exception as exc:
        print(f"[WARN] trace capture failed: {exc}")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
