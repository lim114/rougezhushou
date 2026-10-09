# 第108节最终报告/逐叶保存 Source 包

本包由 Source 作者只读公开源码和已完成 JSON、使用标准库 AST/hash/compile 制备。作者没有执行 builder、saver、publisher、项目、测试、API、Qt、Wine、helper 或 decoder，没有改 tracked 文件。只有 Root 可以执行下述入口。

`INACTIVE_FINAL_INPUTS_TEMPLATE.json` 保持 readyFalse、Source_onlyTrue、35 个 pin 和未来结果 NULL。Root 在另一个新 JSON 中提供实际公开 regular leaf 的绝对路径、bytes、SHA；真实 inputs 必须 readyTrue/Source_onlyFalse，不能把这个模板直接作为完成证明。原 Saved binder 是 Root 实际一次 stdlib heredoc，未落 `.py`；归档实际 bindings、log、raw0，不补造脚本或重跑。

Root CLI：

```sh
python /workspace/.continuation/section108-final-save-spec-source-v2/root-section108-spec-builder-v1.py \
  --inputs /workspace/.continuation/ROOT_CHOOSES_FRESH_ACTUAL108_INPUTS.json \
  --inputs-sha256 ROOT_READS_ACTUAL_INPUTS_SHA256 \
  --spec /workspace/.continuation/root-section108-save-spec-v1.json \
  --report /workspace/.continuation/section108-actual-report-v1.md
python /workspace/.continuation/section108-final-save-spec-source-v2/root-section108-save-v1.py \
  /workspace/.continuation/root-section108-save-spec-v1.json
python /workspace/.continuation/root-section-publish-v3.py \
  /workspace/.continuation/root-section108-save-spec-v1.json
```

builder 的首次写入前要求：真实 raw0，当前751+CORE与750局部变化，原107 publication3964/CP107/full105/旧95deferred；两个平台的相关原 AvailableResult、精选真实末尾 JSON；原/候选 API observation-only 原件；同c440第三 Gold/候选各43快照2窗口；主 Saved f46 的全部绑定与1043实际原件；Root 实际四PNG查看；额外 e37 API配对 Saved 的真实 `workflow_checks_passed`、450解码178配对及所有 refs/CORE。20个明确ValueError和两个preview pending是合法错误观察/变化，不能强求0异常或把观察raw0称产品PASS。缺失、非终态、失败或Source漂移都拒绝，不生成成功spec/report。

前两次 Gold raw1、两个 Root 纯Saved诊断、三次真实结果都保留。Qt官方v6.9.3 QRect.center公开取证和reader v1→v2单处精确逆向保留；本次没有报告实际负坐标故障，没有产品修复或额外Gold运行。精选 JSON 自身没有完整 Source map，报告明确只有实际pipeline后/最终检查前后完整Source守恒。主Saved `preview_checks` 桶为空；完整原preview的真实遍历和snapshot域与空统计桶区分。

主Saved1043与独立APIpair450合计1493次解码，原API225重复读取，唯一公开native1268；代码从实际完整ledgers/counters计算，不把1493说成独立原件。逐formatter独立prepost、跨freeze live alias、JSON alias、第二MainWindow、自然OCR、非法Saved准入、原生Windows/游戏/聊天和未知portal动态机制都未验证。

`public-files-source-plan.json` 是233个已明确公开的逐leaf清单（含 prepared-unapplied-next 的109/110既有50个Source叶文件）。运行时没有BASE目录扫描，只从已绑定四套实际native ledger和前两失败ledger扩展精确文件名，再加四PNG。原Source/draft/独审按历史保留，不计109/110完成，未来guard/原probe结果均NULL。不会复制temporary-caches、用户profile、私有状态或活跃Rootlive检查点。Root最终不可变publication-ready snapshot和整体进度材料可通过 `additional_public_files` 逐leaf提供：只允许明确108前缀/公开后缀及 `additional-public-108/` 相对目的地，不接目录。

saver 从真实 `root-section-save-v3.py` 做四处精确局部运输：完整751和每leaf pin在首次tracked写入前验证；copy前再验pin；真实APIpair exactkind用 `workflow_checks_passed`；归档脚本名为108当前文件。所有原archive/checkpoint/progress逻辑保留，旧脚本不改。publisher仍使用原v3，真实commit/push/remote equality/clean由Root执行，作者不构造future commit。

本节实际检验/归档/commitpush结束后按用户要求收束。CPnext109、nextfull110、lastfull105和95deferred是恢复断点，不自动启动109/110，也不将Source准备登记成完成小节。

Root只读独审发现v1报告将历史v1模板的引用误用于封存v2模板；v2只修正这句话与负坐标故障措辞，所有validator/gates、saver、233叶清单及35pin模板全字节保留。原v1是不可变Source历史，从未执行builder/saver。
