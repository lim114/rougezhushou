# 第105节终验与归档规格 Source v2

这是仓库外的 Source-only 准备包。作者只读取、哈希、AST解析和 compile-only，未运行 builder、产品、helper/codec、测试、Qt、Wine 或 Git；未修改 tracked 文件。实际窗口 retry2 仍由 Root 执行，包的存在不是检验或105完成证明。

`root-section105-spec-builder-v2.py` 沿 Root 原 v1 builder（11803 bytes / SHA `77d12a76f636ce9934d5746c175cfaedd353fe8c95e5cffc65dab5e079fda764`）作 fresh Source 运输。实际执行入口必须是此包内该脚本，Root 可先独立读取；它的执行会在 `.continuation` 生成 `root-section105-save-spec-v2.json`、`full105-actual-closure-v2.json` 和 `full105-progress-report-v2.md`，通过 open('x') 避免覆盖既有原件。全部 terminal gates 先于这三项写入；本包不提前生成或执行这些输出。

终验严格绑定 `full105-window-actual-v2/wine-ui-100.json`、`full105-window-primary-v2.exit-code`、`full105-window-supervisor-v2.json` 和真实新 runner/supervisor Source `full105-progress-bounded-window-source-v2/window.py` / `supervisor105.py`（各 SHA `0004f90b316ec6bc576ac893ce67f52e09e9db4508edd8708f431676b36695a1` / `477cf622f56e77a87850790f99c37dbdef3d6466b74697e9783417e83cf3efc3`）。精确 argv 指向 retry2 输出及 suite guard；child/supervisor/primary 必须0、实际预算1200、attempt2、无timeout且无仍执行owned进程。progress 文件必须仍是 passed/workflow false 的简短已追加检查下界，不能替代4283条checks与52状态完整终稿。任何 progress IO 异常不能回退为通过或借第一次/旧full100 PASS。

最终 Saved 与视觉证明沿 Root 约定仍命名 `root-full105-saved-audit-v1.json` / `full105-visual-audit-v1.json`。Saved 必须绑定 retry2 的 saved archive SHA 和四张 `screenshots100` 元数据；visual 必须是 Root 实际四图查看通过的最终 receipt。脚本不代替 Root 打开 PNG，也不重新调用计算或 formatter。原legacy native090 无alias；52个旧Gold比较只覆盖原显式public projection，不扩写为整个旧Gold/full095向量通过。89原五组×双显示模式仍是10个内存消费者回放，非10次真实constructor/apply/OCR。101–104专项窗口/观察/saved证据仍单独归档。当前Wine二进制验证不冒称原生Windows、游戏或聊天验收。

第一次失败原件仍完整保留：supervisor v1 SHA `b49a2771bea0121cc2a84c6c4e0c6a113d7fb020ffc5b2aed9db81de8103cbb6`，primary124、child-9、600秒deadline、真实600.1465337909904秒、三张实际已查看PNG、没有完整终稿。closure/gui_attempts 和报告明确两次尝试；只有 retry2 实际通过后写第2次PASS。第95节三次未完成继续 deferred，原失败不删除/覆盖、不作第四次无诊断重放。

Linux现成 receipt 自身 Source 为355子集；完整748+CORE另由 Root 的 `full105-linux-root-source-audit-v1.json` 与当前 guard/产品字节全量匹配证明。不能把355说成Linux receipt内748。已存在实际 Linux2240/2018PASS/84skip/U191records150parents、Wine2307/2094PASS/87skip/U186records145parents，均0F0E；Wine三项实际能力skip计入87跳过，不计PASS。当前221物理测试模块/239 full union selectors与不完整仓库范围声明均沿真实v1材料保留，不猜未来执行counts。

`checkpoint-closure-plan.json` 是 Root 实际成功后、通用 section saver 后、105 commit前的明确更新建议，不是 tracked 修改器：completed105、next106、dueFalse、last_full_validation/current_full105_checkpoint完整复制actual closure-v2，顶层及policy的 next_full_validation_after 同为110。原095/100、deferred/problems与旧pending_batch_save历史原样保留。106 applier 可据这些实际字段加强前置gate；不会依据 Source-only 计划放行未完成105。

本包公开entries沿原root builder扫描 `section105-*` / `full105-*`，自然包括两套Source、首次raw124、retry2完整终稿和partialprogress；另外实际执行的builder-v2字节通过 `Path(__file__).resolve()` 入档。原builder-v1仍作为原Source依据归档。只存在于本 Source 包的编译成功不等于未来 builder实际成功。
