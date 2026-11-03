第90节根端归档草稿，尚未执行，也未改仓库。脚本不启动测试、计算API、Qt或Wine。

`archive-full-090.spec-template.json` 中 UI 的 `null` 必须替换为最终冻结包及根端实际记录；模板本身不能用于完成归档。最终UI字段、检查总数、文件名由正式包给出，不能猜。`ui_contract` 可补最终副节计数和范围字段。

根端正式运行顺序：完成 `full_context.py finish 90`，独立查看四张实际窗口PNG并写 inspection，再以新文件另存填好的spec。脚本默认仅静态读取检验，只有 `--execute` 才写入新 `verification/full-090`、更新四份进度元数据、提交和创建 `p2-validation-090`。

固定实际产品提交为 `5e2ff697402d06e78b239e01f0b4307b50dd5633`，并以 finished context 再断言730份维护源码与Git原字节。必纳Linux/Wine全量JSON和两种console/log、精选和Linux复用证明、依赖检查、UI运行器/结果/process、四PNG/inspection、整个UI公开V1包及原manifest。额外54份未来源候选资料不是已完成小节。

`additional_public_files` 是明确的 `{source_path, archive_path, bytes, sha256}` 列表，根端可加入 `full090-pre-window-source.json`、`wine-version-post-restart090.log`、`root-finish-090.log`、正式root-preflight脚本/spec与独立静审附件。这些文件待最后字节稳定后核SHA，不能通配复制任何runtime/private文件。

所有输入先核后写，失败保留部分归档供诊断，禁止覆盖重试。全部归档件（包括忽略的build/log叶子）逐件 `git add -f`，核索引原字节后写payload closure与最终V1清单，再核全部索引，commit后核全部Git blob，最后tag。最终提交SHA不能嵌入该提交自身；真实postcommit闭合证明存入新的外部 `full090-committed-closure.json`，stdout另报告tag验证，已归档payload closure准确标明排除自身与最终清单。

原full085和4217检查的历史JSON/图片保持原样，新UI明确保留4217；Wine只代表兼容验证，缺失记录不计通过，原生Windows/game/desktop与未知时钟边界不改。
