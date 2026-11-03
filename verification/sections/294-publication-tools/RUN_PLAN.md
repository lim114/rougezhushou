# 第294节发布工具准备

仅从第293节实际工具适配；准备阶段不执行这些工具、不暂存、提交、推送或修改产品/公开文档。根代理先完成294严格closeout及索引更新，审查本目录后再按次序调用。工具不会提交Git；提交由根代理明确执行。

## 执行次序

在项目根目录使用 .venv\Scripts\python.exe -B -X utf8，以下脚本均位于 .cache/p3-294-publication-prep/：

1. 根代理先运行既有 scripts/update_cloud_index.py，确保功能294、next295、full290历史/next305、无数字终点。
2. stage_section_294.py：只允许8份当前文档、既有 rouge/data/fixed-landmark-references.json，promotion17路径和本节294公开原件。核最终section、实测来源、索引，读取真实index blob逐字节对比磁盘。须当前HEAD为48eeb454e23fffee084fe7b6c7f9667b9216131d、index为空。使用promotion作为路径集合，最终SHA取实际section/necessary/native，不能要求旧native promotionSHA等于修后源码。
3. 根代理实际提交功能与要求/索引；push_section_294.py functional 执行唯一普通push。核父提交和stage精确路径，不含force/main，失败或超时记录实际结果，不能据push单独宣称远端核实。
4. verify_publication_294.py：要求干净worktree、实际功能push0、实际ls-remote相符、功能提交父为指定293 metadata、changed集合等于stage readback。逐字节核提交/磁盘与最终necessary/native来源之并集。通过后才写294-publication及原push副本，更新真实publication CP和当前文档。功能SHA来自当前实际HEAD和stage父/精确路径验证，不预填或预测。
5. 根代理再次运行既有 scripts/update_cloud_index.py。finish_publication_294.py stage：归档本目录精确工具原件、只暂存7份发布文档、实际proof/push和工具档案，逐字节读取stage。此阶段不变更功能数据或待办。
6. 根代理实际提交发布元数据；push_section_294.py metadata 普通push；finish_publication_294.py final 再次ls-remote并读取metadata commit blob，输出仅缓存current294-checkpoint.json。metadata父必须为已核实功能提交，未实际push不输出完成。

## 输出与边界

脚本由根代理实际调用后，缓存回执为 .cache/section294-stage-readback.json、.cache/section294-functional-push.json、.cache/section294-metadata-stage.json、.cache/section294-metadata-push.json、.cache/current294-checkpoint.json。均要求原路径不存在；失败不自动覆盖或重发。推送结果不明确时先只读核远端，另行处置，不自动重复。

最终必要检查数/原生unique及重复断言取真实回执；不预填本次工具的PASS或新增实测检查数。保留首原生失败，18新增点/2原图/4关与合计10图18关58点只是部分直接参考；81关59图完整校准未知、regular12/24不变。未跑294全量，历史290原SHA沿用、下次305；next295、无终点、P3/P2未完成。发布工具不操作窗口、游戏、聊天或私人状态，不重复执行必要测试/原生窗口。

旧293四工具只读用于适配，BASELINE.json记录其原SHA；本目录READY只说明语法/静态准备，不是运行验收或发布证明。根代理确认实际closeout输入后再执行本流程。
