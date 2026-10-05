# 本地客户端桥接来源

`rouge/bridge/desktop-chat.cjs` 与 `conversation-hub.cjs` 由用户明确指定，从本机 EsperantaCompanion 项目复用。该项目 package.json 标注 GPL-3.0-only；随附 `Esperanta-GPL-3.0.txt`，不得将这两个本机模块误标为 Apache-2.0。

desktop-chat.cjs 文件头说明其通信方案参考 kajmahal/chatgpt-conversations-mcp，社区项目为 Apache-2.0；随附 `chatgpt-conversations-mcp-Apache-2.0.txt` 保留许可。

来源：https://github.com/kajmahal/chatgpt-conversations-mcp

2026-10-01 Rouge 修改：移除打开/切换前台窗口操作，禁止将调用上下文作为目标会话；新增 Python/Node 后台传输适配。后续发送保护改动在代码中注明。没有读取登录令牌、Cookie 或修改客户端安装文件。
