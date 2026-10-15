"""统一文件执行入口：python run.py --env test"""
from __future__ import annotations
import argparse
import os
import sys
import shutil
import subprocess
from pathlib import Path
import pytest
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent

def main() -> int:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description="Python + Playwright UI 回归测试")
    parser.add_argument("--env", default=os.getenv("TEST_ENV", "test"), help="环境名：test/staging 等")
    parser.add_argument("--headed", action="store_true", help="显示浏览器窗口")
    parser.add_argument("--grep", default=None, help="按用例名称关键字筛选")
    parser.add_argument("--workers", default="1", help="xdist worker 数量，例如 4 或 auto")
    parser.add_argument("--no-retry", action="store_true", help="关闭失败重试")
    parser.add_argument("--tests", default="tests", help="测试目录或文件")
    parser.add_argument("--allure-results", default="reports/allure-results", help="Allure 原始结果目录")
    args = parser.parse_args()

    os.environ["TEST_ENV"] = args.env
    os.environ["PW_HEADED"] = "1" if args.headed else "0"
    results_dir = ROOT / args.allure_results
    report_dir = ROOT / "reports" / "allure-report"

    # 每次执行前清理旧的 Allure 数据和旧 HTML 报告，避免打开历史报告
    for old_dir in [results_dir, report_dir]:
        if old_dir.exists():
            shutil.rmtree(old_dir)

    results_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "reports").mkdir(parents=True, exist_ok=True)
    (ROOT / "artifacts").mkdir(parents=True, exist_ok=True)

    argv = [
        args.tests,
        "-ra",
        "--strict-markers",
        "--alluredir", str(results_dir),
        "--clean-alluredir",
        "--junitxml", str(ROOT / "reports" / "junit.xml"),
        "-n", args.workers,
    ]
    if args.grep:
        argv += ["-k", args.grep]
    if args.no_retry:
        argv += ["--reruns", "0"]
    else:
        argv += ["--reruns", os.getenv("E2E_RETRIES", "1"), "--reruns-delay", "1"]

    exit_code = int(pytest.main(argv))

    # 自动生成最新 Allure HTML 报告
    try:
        allure_cmd = shutil.which("allure")
        if not allure_cmd:
            raise FileNotFoundError("未找到 allure 命令，请检查 Allure 环境变量")

        subprocess.run(
            [allure_cmd, "generate", str(results_dir), "-o", str(report_dir), "--clean"],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"[INFO] Allure 报告已生成: {report_dir}")
    except Exception as exc:
        print(f"[WARN] Allure HTML生成失败：{exc}", file=sys.stderr)

    try:
        from core.dingtalk import send_summary
        send_summary(exit_code, ROOT / "reports" / "junit.xml")
    except Exception as exc:
        print(f"[WARN] 钉钉通知发送异常：{exc}", file=sys.stderr)
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
