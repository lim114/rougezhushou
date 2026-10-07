# Linux 上的 Windows 兼容验证

用户已授权使用 Wine。2026-10-07 已在 `/workspace/.compat` 建立独立环境：Debian Wine 10、官方 Windows CPython 3.12.10、PySide6 6.9.3、NumPy 2.2.6，以及官方 Microsoft SDK x64 UCRT。真实 Windows 依赖均可导入；`pip check` 通过。Qt/NumPy 版本在项目允许范围内；Qt 6.11 缺少 Wine 系统 ICU 的失败及内置 UCRT 缺少 `crealf` 的失败保留在环境缓存中。

Debian 包核对签名索引 SHA256，Windows wheels 核对官方 PyPI HTTPS 元数据，Python/SDK 从官方 NuGet 使用验证 TLS 下载并保存哈希。没有替代模块或关闭证书验证。来源、版本及环境摘要已保存到 `verification/wine-environment/`；二进制包留在 `.compat`，不进入仓库。

每五节后在仓库目录执行，输出目录必须使用新的编号：

```bash
.venv/bin/python scripts/verify_full_available.py --output .cache/continuous-010/linux-full.json
/workspace/.compat/run-wine-python.sh 'Z:\workspace\rougezhushou\scripts\verify_full_available.py' --wine --output 'Z:\workspace\.compat\wine-full-010.json'
/workspace/.compat/run-wine-python.sh 'Z:\workspace\rougezhushou\scripts\verify_cloud.py'
/workspace/.compat/run-wine-python.sh 'Z:\workspace\.compat\wine-ui-smoke.py'
/workspace/.compat/run-wine-python.sh -m pip check
```

全量可用选择器取历史 CORE 维护集及新增云端模块；缺少迁入的 `.cache`/`samples/native-client` 资料和明确的平台依赖列为不可验证，绝不计通过。产品资源缺失、数值断言或其他异常仍使验收失败。`--require-complete` 在存在不可验证项时返回非零。

Wine 界面检查打开真实 MainWindow，使用真实 Win32 窗口枚举，逐个操作 87 技能控件及计算按钮，核对报告、保存截图，再关闭测试窗口。本局、培养、设置及聊天目录全部在临时目录；采样关闭。第5节结果见 `verification/full-005/`。

复现脚本存于 `scripts/compat/`，当前脚本使用 `/workspace/.compat`。已保留下载包时，先把这些脚本复制到 `.compat`，运行 `verify-cached-inputs.py` 核对，再运行 `rebuild-wine-local.sh` 重建。新机器需按来源回执重新取得缺少的官方包；脚本不会假装包已存在。

Wine 结果证明 Windows 二进制在此兼容环境的行为。原生 Windows Graphics Capture、真实游戏帧、原生桌面聊天客户端、多机器安装与 Windows 性能仍未验证。
