# Python + Playwright UI 回归测试框架

## 特性
- 统一文件入口：`python run.py`
- Python + Playwright + pytest
- Page Object + Service 业务封装
- `data-testid` 定位、自动等待与显式断言
- 环境配置与账号密钥分离
- 截图、视频、Playwright Trace、Allure 原始结果
- xdist 并发、失败重试、JUnit XML
- GitHub Actions 示例与钉钉通知
- 过期诊断产物清理脚本

## 本地安装
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
playwright install chromium
copy .env.example .env
copy config\environments.example.yaml config\environments.yaml
```
macOS/Linux 请使用 `source .venv/bin/activate` 和 `cp`。

在 `.env` 中设置 `BASE_URL`、`E2E_USERNAME`、`E2E_PASSWORD`。不要提交真实 `.env`。
配置 `config/environments.yaml` 中的环境地址和超时。该文件已加入 `.gitignore`。

## 执行入口
```bash
python run.py
python run.py --env test
python run.py --env staging --headed
python run.py --grep login
python run.py --workers 4
python run.py --no-retry
python run.py --tests tests/test_login.py
```
本地和 CI 都通过 `python run.py` 执行，不要求直接调用 pytest。

## 适配已有项目
请先阅读 `docs/ADAPT_EXISTING_APP.md`。目前 `pages/login_page.py` 中的 `/login`、`login-username`、`login-password`、`login-submit`、`user-menu` 均为示例值，必须替换为真实系统路径和 `data-testid`。测试系统需提供可自动化的独立账号，若登录有验证码/MFA，应与系统负责人协商安全的测试方案，不要尝试绕过生产安全控制。

## GitHub Actions
工作流位于 `.github/workflows/ui-regression.yml`，支持：
- push / pull request 到 main/master
- Actions 页面手动触发并选择 `test` 或 `staging`
- 运行后归档 `reports/` 和 `artifacts/`，保留 14 天
- 测试失败时 job 失败，阻断依赖该 job 的合并检查

GitHub 仓库 `Settings → Secrets and variables → Actions`：
- Variable：`BASE_URL`
- Secrets：`E2E_USERNAME`、`E2E_PASSWORD`
- 可选 Secrets：`DINGTALK_WEBHOOK`、`DINGTALK_SECRET`

如果测试环境只允许内网访问，需要配置 self-hosted runner 或安全的网络连通方案。不要把凭据写入 YAML。

## Allure 报告
框架会生成 `reports/allure-results/`，并生成 `reports/junit.xml`。需要本地查看 HTML 报告时，安装 Allure Commandline 后执行：
```bash
allure generate reports/allure-results -o reports/allure-html --clean
allure open reports/allure-html
```
CI 已归档原始结果和诊断文件。若需托管 Allure HTML，可再配置专用报告发布步骤。

## 失败诊断与安全
- 失败时保存截图和 trace zip；视频由 Playwright context 录制，CI 归档 `artifacts/`。
- Trace、截图、视频可能含用户信息或敏感数据，应限制 artifact 访问并设置保留期。
- 重试成功仍应视为 Flaky 候选，定期分析与治理；不要无限增加重试次数。
- xdist 并发时不仅账号要隔离，订单、用户、审批等测试数据也要隔离。
- 建议使用专用最小权限测试账号，不要使用生产账号。

## 清理
```bash
python scripts/cleanup_artifacts.py --days 14 --dry-run
python scripts/cleanup_artifacts.py --days 14
```
