# Fresh 100 Wine full／selected／probe（Source-only candidate）

本包提供 4 个 executable Source 文件；作者仅用 stdlib 读文件、SHA、AST、JSON 和写仓库外候选，未导入目标、执行项目、测试、helper、codec、Wine 或 Git。当前不能当运行通过或小节完成。需另一位独审和 Root 的真实完成100 guard 后执行；封存后不得原地修改。

## Root 顺序与 CLI

1. 通过实际 Wine wrapper 执行 wine_capability_probe100.py --wine --out <fresh probe JSON Windows path>，记录真实 argv/cwd、Source、launch/completion、stdout/stderr 和实际 primary；probe0 只说明能力控制已识别，不是产品 PASS。
2. Root 在真正完成100后建立新 guard JSON（不是本包提供假值）：整数 section=100；source_sha256 是 rouge/tests/scripts 全部 .py/.json 精确路径→SHA 集合；source_additional_sha256 至少含 CORE_0.70_VERIFICATION.json；adapter_source_sha256 是本包全部7文件（含manifest）的名字→SHA；wine_capability_probe 和 wine_capability_probe_primary_exit 各为 path/bytes/sha256，后者须真实 b'0\n'。
3. 各自 fresh output：wine_full100.py / wine_selected100.py --wine --root <actual Root Windows path> --guard <actual guard Windows path> --probe <bound independent probe Windows path> --out <fresh suite JSON Windows path>。仅 full 可加 --require-complete。须在项目 cwd，经同一实际 Windows Python／Wine wrapper 运行；Root 的监督器和时限另行绑定。

--root/guard/out/probe 仅接受公共 workspace（Wine Z:\workspace），guard里 probe ref 可用 /workspace/... 或实际 Windows 路径。所有 Source/ref 是 regular nonsymlink；输出 JSON/log exclusive。额外根登记只允许 CORE_0.70_VERIFICATION.json、AGENTS.md、CLOUD_HANDOFF.md、CLOUD_SOURCE_MANIFEST.json、DEVELOPMENT_CHECKPOINT.json、README.md、PROJECT_PROGRESS.md、PROJECT_COMPLETED.md、WORK_IN_PROGRESS.md、BATCH_CONTINUOUS_P2.md。Root 选择需要冻结的公开文档，运行期间不更新它们。

## 原分类与动态登记

full 动态导入当前 guard 所指 verify_full_available 和 verify_cloud，采用当前历史登记＋当前 NEW_MODULES＋当前 MODULES 的有序去重 union；selected 直接采用当前 MODULES。未冻结109/197，未读旧failed342作为当前门禁。模块物理路径和 ROOT 必须等于 --root。full 直接用当前维护的 AvailableResult；其 class 和 unmigrated_path 的 AST 校验必须与已审原版一致。若将来 classifier 原方法改变，要新 Source 审阅，不可放宽门禁。

selected 保留 result.wasSuccessful() 的原零／一判断，并加 guard/Source drift 条件。没有编造 individual passed 字段。source_sha256 主图是全部 rouge/tests/scripts .py/.json；source_additional_sha256 绑定 CORE selector登记；adapter/probe/guard 自身也保留前后绑定。

## 严格 Wine 能力边界

要求显式 --wine、真实 Windows Python3.12.10、实际 wine_get_version 导出和精确已查证 kernelbase／ntdll active module SHA；原生 Windows 永不适配。独立新 probe 与每项 suite内 fresh probe 需相同 runtime/default Temp、Source，时间有序。只用新 public TemporaryDirectory，读取/写入自己的两对控制文件，无项目或私有状态调用。

两对控制若真实创建链接，则运行原 body；若重现原始允许 creation exception，则仍运行原 body，它原有 OSError／NotImplementedError skip 保留。只有 absent/existing-malformed 两对都精确出现 nonraising None、无 is_symlink/exists、lstat/readlink/read_bytes WinError2、physical entries 与目标原字节不变，才可在产品调用前替换那两个 exact leaf ID 成 declared skip。未知、混合、二进制变更均拒绝，不改 API/测试/产品。

两项能力 skip 的 actually_executed、fixture_body_run、product_assertions_passed 都 false，capability_skips_counted_passed=0。它们也是同两次普通 skipped，不能加两遍。run 数父测试；unavailable/failure/error/skip可记录subtest；不可加减算成功。full使用真正passed_count；complete字段仅覆盖maintained union，能力skip或unavailable存在即false，普通历史skip仍保留原判定。selected complete始终false。native Windows、游戏、聊天均未认证。

历史095的源码诊断只支持当前精确binary能力归因；旧失败／NULL／Root143和窗口搁置继续保留，适配器不写、不重试它们，也不声称已核验历史归档。Root出版闭环另查原件。Source basis 当前读取哈希是审阅依据，未来100的实际guard/selector/count/runtime依然未知。

本包不替代 fresh Linux full/selected/pip、Wine pip、bounded项目完整窗口、Saved/PNG原生证据检查或commit/push。需各项真正完成才可接受100 full checkpoint。
