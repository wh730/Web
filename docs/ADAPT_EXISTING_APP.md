# 适配已有 Web 项目：实施清单

本仓库是通用框架，不假设任何真实页面的 URL、文案或 `data-testid`。请在测试环境完成以下适配后再启用 CI 门禁。

## 1. 收集被测系统信息
- 测试环境 URL、登录 URL、登录后稳定页面 URL/元素。
- 登录页用户名、密码、提交按钮、错误提示的 `data-testid`。
- 登录成功后可稳定验证的元素，例如导航栏用户菜单。
- 是否有验证码、MFA、SSO 跳转或 IP 白名单。
- 测试数据创建/清理方式，是否可通过 API 准备数据。
- 哪些操作有副作用，哪些账号可以用于自动化。

## 2. 统一选择器契约
建议前端给自动化测试提供稳定属性：
```html
<input data-testid="login-username" />
<input data-testid="login-password" />
<button data-testid="login-submit">Sign in</button>
<div data-testid="user-menu"></div>
```
`data-testid` 是示例命名，需按真实 DOM 调整。不要用易变化的 CSS class、层级 XPath 或纯视觉坐标。

## 3. 修改页面对象
修改 `pages/login_page.py` 中：
- 登录路径（`open()`）
- 用户名、密码、提交按钮、错误提示的 test id
- 登录成功判定元素（`expect_logged_in()`）

页面对象只封装单页操作；跨页面流程放到 `services/`；测试用例负责场景、断言和测试数据。

## 4. 配置账号
在 GitHub 仓库 `Settings → Secrets and variables → Actions` 中配置：
- Repository variable：`BASE_URL`
- Repository secrets：`E2E_USERNAME`、`E2E_PASSWORD`
- 可选 secrets：`DINGTALK_WEBHOOK`、`DINGTALK_SECRET`

请使用专门的、最小权限的测试账号。不要把密码、Cookie、token 或 `.env` 提交到 Git。
如启用并发，推荐配置独立账号，例如 `E2E_USERNAME_gw0` / `E2E_PASSWORD_gw0`。测试数据也必须隔离。

## 5. 验证 CI
先在 `workflow_dispatch` 手动运行，确认：
- 测试环境可从 GitHub-hosted runner 访问
- 登录流程成功
- `reports/junit.xml` 与 `reports/allure-results/` 生成
- 失败时 `artifacts/` 中有截图、trace 和视频
- GitHub Actions 的 artifact 可下载，且访问权限与保留期符合要求

## 6. 质量门禁建议
- 冒烟/关键路径失败：阻断合并。
- 重试成功仍标记为 Flaky，统计趋势并分配治理负责人。
- 不允许通过增加重试次数长期掩盖失败。
- 按团队要求设置覆盖率、成功率和 Flaky 阈值；先收集基线再设硬门槛。
