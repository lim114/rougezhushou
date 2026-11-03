# 首审工具路径错误的证据范围

首次只读复审工具运行在补充来源读取处抛出 `FileNotFoundError: GameAssembly.dll`，未生成最终复审回执。公开来源记录中的 basename 被工具当成本地路径；后续工具改为明确要求 `--dll-path` 与 `--metadata-path`。这是复审工具路径错误，没有生产数值断言失败。

- `first-readonly-review-tool.py` 是首次运行之后、路径修复之前封存的工具源码原字节副本；未重写或重新执行旧失败。
- `first-readonly-review-path-error-summary.log` 是当时随后写入缓存的简要说明原字节副本，**不是实际 stdout/stderr 全文捕获文件**。它记录错误类别、原因和修复范围，不作为完整原始日志。
- 实际首次工具结果的完整 traceback 曾出现在当前会话工具输出中，但没有在首次执行时封存为文件。其完整原始机器输出文件未封存；本次不重演失败，也不把摘要或重建文本冒充原件。

本次只复制上述两个已封缓存文件并补充本说明，没有修改最终 `276-readonly-source-review.json`、核心、manifest 或测试，也没有再次运行复审。最终通过范围由原最终回执独立记载。
