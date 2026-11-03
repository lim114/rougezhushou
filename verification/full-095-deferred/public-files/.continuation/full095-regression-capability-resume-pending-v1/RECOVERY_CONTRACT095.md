# Full095 原实际 epoch 的最小恢复合同

此封包仅为 SOURCE。没有执行 context / adapter / project / tests / codec / Wine，也没有完成全量、commit、push 或新增编号小节。所有 future runner / review / actual observation / spec binding 保持 null，直到 root 用实际文件填写新控制 spec，并由独立 SOURCE 审阅绑定其精确 SHA。

`binding_validation095.py` 和 `historical-classifications090.json` 从实际 FINAL 原件按整文件原样复制。新的 `recovery_binding095.py` 先用原模块、原 `OUTPUT_NAMES` 和原 `root_spec` 验证原 actual_inputs、93–95 物理归档与 index、HEAD、735 实际源集合、original full/selected selectors、8 原合同、UI/saved exact source bindings。随后才投影两项 Wine 合同；不修改原 validator 常量或调用其目标脚本。

允许的差异只有：wine_full / wine_selected 的 argv 与 runner，wine_full 的 raw exit sink，新 full receipt / runner log / console，以及新恢复 context sink。selected 的既有未占用 console / raw sink 保持原路径；另外六项合同、UI/native/PNG/saved 全路径、原分类器 bytes、源码集合、full/selected selectors、所有严格 finish 断言均保留。新增 immutable inputs 包含原 context、原失败、真实已通过 observation 和所需 receipt，以及适配器/来源/SOURCE审批封包；它们不是新测试。

原 context 的 14 个函数中 12 个整函数 bytes 保持：只改 `load_actual_binding` 和 `require_primary_executions`；原 `full_receipt` 整函数及其 Linux 完整度判断保持原样。新 `wine_full_receipt` 复制同一原 full receipt gates，仅使用新 planned sink，并用真实 capability schema 严格核对两条 unrun/declared skip、真实理由、原 unittest skips、零 PASS credit、完整度 false、真实 Wine export/active module hash、两个原件确认的 phantom probe、同一 source refs/adapter source map/argv。selected 原整函数不变，main 读实际结果后追加同一 capability 核验。`actually_executed: false` 的真实 producer 含义是原 fixture 和 AccountCache 保存断言未运行；替身 skipTest 本身由 unittest 执行并计作 skip。

`root-recovery-input-template095.json` 不能直接执行：状态为 pending、真实引用为 null。Root 实际 spec 必须使用 `ROOT_BOUND_ACTUAL_FULL095_RECOVERY_SOURCE_INPUTS`，逐项填入实际 fullref `{path, bytes, sha256}`。至少提供已真实通过的 Linux full 和 Linux pip observation；可加入已实际完成的 Linux selected / Wine pip / Wine UI，其余在运行或未运行的 jobs 不得填入 future pass。full 的 receipt 为实际 JSON fullref，pip/selected receipt 显式 null，UI receipt 为原计划 UI JSON fullref。每个 observation 使用原 actual contract、原实际开始/完成时间、root tool session/completion chunk、实际 primary 0、同一物理 stdout/raw。

原 Wine full 的失败单独保留：真实 root session 37864、completion chunk 6e35c0、primary 1、原 receipt/runner log/stdout/raw、原实际时间和两条原失败 case。不把它改成通过或把 selected 未启动改成失败。Root 若需失败 observation，另写新实际 metadata；不运行只接受 0 的旧 observation helper，不覆盖任何原文件。

Root 实际 spec 中 `adapters` 包含 `manifest`, `source_contract`, `source_evidence`, `executions`；每个 adapter 执行条目须有 `runner`, `argv`, `source_review`, `review_pointers`；pointers 的 keys 是原 `exact_source_review` 使用的 `source_pass`, `runtime_pass`, `runner_sha256`, `argv`。真实正式 review 必须 source pass true / runtime false，绑定对应 runner SHA 和精确 CLI；来源证据与 manifest 必须实际存在且严格哈希验证。实际 adapter manifest 的 `name` 仅作成员元数据；它的 path/bytes/SHA 投影须与合同/runner/shared refs相等，不把额外 name 字段误当ref不等。context 不执行 adapter 来决定能否接纳 SOURCE。

Root 在实际 spec 完成后独立 SOURCE 审批报告需要顶层字段：`source_gate_passed: true`, `runtime_pass: false`, `recovery_spec_sha256`, `source_manifest_sha256`, `pending_context_sha256`, `recovery_helper_sha256`, `sealer_sha256`。所有 SHA 是审批时的实际字节。Sealer argv：

```
/workspace/rougezhushou/.venv/bin/python /workspace/.continuation/full095-regression-capability-resume-pending-v1/seal_recovery095.py --spec ROOT_ACTUAL_SPEC --spec-sha256 ROOT_ACTUAL_SPEC_SHA --review ACTUAL_INDEPENDENT_SOURCE_REVIEW --review-sha256 ACTUAL_REVIEW_SHA --output-dir /workspace/.continuation/full095-regression-capability-resume-final-v1
```

Sealer 仅做绑定和 SOURCE 写入，root 必须继续独立 FINAL source 投影审批后再使用 FINAL。其 pending→FINAL 只替换 PENDING 和新 binding SHA 两处字面量；完整 15 处 recovery delta 可逆回实际原 FINAL `full095_context_final.py`。partial write 永不当作完成，任何已存在 sink 都保留。

Root 实际 `full095_context_recovery.py resume` 只要求五个 NEW retry/recovery sinks 和尚未使用的原 final context sink 不存在，不要求旧 33 outputs 全部空。它继承 immutable original context 的真实 `started_at`，同时记录当前真实 `recovery_started_at`，显式声明 original epoch recovery、已通过项列表和原失败引用。它不会再次执行 start 或任何成功前缀，也不把原 timestamp 说成新运行时间。

Finish 继续原八项 exact argv / cwd / runner / script position / timestamps / stdout / strict raw 0、full receipts、旧 skip taxonomy、dynamic counts/source scopes、selected/pip、actual fullUI、saved native exact physical set、4 PNG root view、same-source/same-receipt/execution witness 等断言。两个 adapter 运行的开始时间必须晚于真实 `recovery_started_at`；所有 spec 声明复用的 passed observation 必须与最终八 witness 对应行整对象完全相同。final context sink 保持 `/workspace/.compat/wine-validation-095-context-final.json`，并带真实 recovery、旧失败保存和原 epoch 标志。

原字段 `selected_reuse_performed: false` 继续表示没有借用历史/前一节的 selected receipts 或用 subset结果代替当前95的实际完整selected执行。恢复时当前95 original epoch的真实成功proof引用由 `preserved_passed_executions` 和 final `reused_passed_current_epoch_executions` 单独明确披露；这些是恢复使用的原本轮真实执行，不说它们在 resume 后重新运行。

现有 archive v2 的 `context_start` role 接新的恢复 context，`context_source_binding` / `context_final_runner` 接 recovery FINAL。恢复 context 保留 archive 接受的 started status / original epoch / source map，并与 final 绑定同一新 runner/binding；它显式记录恢复事实，不能把它描述成八项全部新开始。原 context、原 runner/binding、实际原 start stdout/raw、原 Wine failure全部 physical artifacts/SOURCE packets 及 actual spec/formal approval，必须额外明确归档。已有 archive v2 从 binding.actual_inputs 读取合同和 sink，能接最小投影；原/source snapshots、每项 stdout/runner/exit 和所有复用 proof 都要精确 public archive，不能只填 summary。

Root 所有实际命令使用 `PYTHONDONTWRITEBYTECODE=1`；若外部正常 Python 编译生成 cache，保存实际历史，不把它写成原 SOURCE payload 或偷偷删改 frozen 源包。Wine 仍是 Linux 上的兼容验证，不是原生 Windows/game/chat。
