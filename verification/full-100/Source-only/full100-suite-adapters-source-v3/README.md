# Fresh 100 Wine full／selected／probe v3（Source-only candidate）

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

两对控制若真实创建链接，则运行原 body；若重现原始允许 creation exception，则仍运行原 body，它原有 OSError／NotImplementedError skip 保留。只有 absent/existing-malformed 两对都精确出现 nonraising None、无 is_symlink/exists、lstat/readlink 的 int errno2 + int WinError2，read_bytes 的 int errno2 + 显式 winerror null、physical entries 与目标原字节不变，才可在产品调用前替换那三个 exact leaf ID 成 declared skip。未知、混合、二进制变更均拒绝，不改 API/测试/产品。

三项能力 skip 的 actually_executed、fixture_body_run、product_assertions_passed 都 false，capability_skips_counted_passed=0。它们也是同三次普通 skipped，不能加两遍。run 数父测试；unavailable/failure/error/skip可记录subtest；不可加减算成功。full使用真正passed_count；complete字段仅覆盖maintained union，能力skip或unavailable存在即false，普通历史skip仍保留原判定。selected complete始终false。native Windows、游戏、聊天均未认证。

历史095的源码诊断只支持当前精确binary能力归因；旧失败／NULL／Root143和窗口搁置继续保留，适配器不写、不重试它们，也不声称已核验历史归档。Root出版闭环另查原件。Source basis 当前读取哈希是审阅依据，未来100的实际guard/selector/count/runtime依然未知。

本包不替代 fresh Linux full/selected/pip、Wine pip、bounded项目完整窗口、Saved/PNG原生证据检查或commit/push。需各项真正完成才可接受100 full checkpoint。

## v2 精确错误合同修正（未实际运行）

v1 Root 实际独立 probe primary1（525825），两 pair 的创建/无实体/原目标字节/physical entries/同 pinned binaries 均保留，mode 未识别是 observe/missing 错误合同：`read_bytes` 记录 FileNotFoundError、显示 Errno2、winerror null；`lstat/readlink` 保留 WinError2。旧记录未采集 errno 字段，不能给它补造字段或重写 passed。

精确 CPython v3.12.10 官方 Source 已查：Path.read_bytes 经 io.open；FileIO 的 `_wopen` 失败用 errno 三参数构造，Windows 路径查询经 WindowsErr 构造，PC/errmap.h 将 ERROR_FILE_NOT_FOUND2 映射 ENOENT。完整下载/hash/行依据在 `/workspace/.continuation/full100-cpython-fileio-source-diagnosis-v1/source-diagnosis.json`。

只有 `observe_operation` 新收实际 `exc.errno`，`missing_operation` 对三个已明确 operation 精确区分：均需 FileNotFoundError、真正 int errno2；read_bytes 需显式 winerror null，lstat/readlink 需真正 int winerror2；其它 operation 不准。所有其它函数 AST、三 entrypoint 原 bytes、两 pair 不存在实体/目标字节/目录/同 binary/双实际 probe/全部 Source 与 primary 门保留。没有修改产品、AccountCache/test methods、AvailableResult、capability admit logic 或判断 successful 的方式。

v2 packet-map 改为本新目录7个实际文件，Root 需新独立 v2 probe 与真实 raw0 引用；v1 probe/Source map 会拒绝作为 v2 证据。实际100 production Source map 不应因为这个仓库外 Source 修正而变化，GUI 另行进行。仅1b3a75实际 Source 语义编译0，未调用 classification/helper/probe/project/tests/Wine/Git，也未执行原控制的“重分类”。待独审后由 Root 第二次实际采集字段和识别，仍遵守同一问题最多3次。


## v3 精确第三个符号链接夹具（未实际运行）

Root 的真实 Wine full v2 JSON/log 原件保留：运行2100，failures1/errors0；唯一 failure 为 tests.test_run_persistence_099.RunPersistenceTests.test_actual_dangling_symlink_is_not_missing_until_explicit_manual_reset，在原测试480行 self.assertTrue(path.is_symlink()) 失败，483行 RunState(path) 尚未到达。这不是 RunState 产品行为已被测失败或通过。Root 另报告同一原测试 Linux 实测通过；本作者没有执行它。

v3 仅将上述第三个精确 leaf ID 加入 TEST_IDS，将 admit_suite 的 found==2 和消息改为3，并将对应 validate_skips 文本改为Three。统一 SKIP_REASON 明确称 AccountCache or RunState 的原产品保留断言没有运行；全部 skip 不计 PASS。三 entrypoint 的 bytes 与封存v2逐字相同。

只有双 fresh absent/existing-malformed 控制、同 pinned binary/default Temp、精确 errno/operation、原 Source/primary/双 probe 门已满足的 diagnosed_phantom_success 可替换这三个加载的原 leaf；真实链接与原允许创建异常仍进入各原测试体。两对控制、全部其它函数／class AST、AvailableResult gate、主Source／附加Source guard 不变。未修改产品、原测试、旧packet或失败记录；没有宽泛符号链接／平台 skip。

Root 必须用新v3七文件 map，重新真实执行独立probe、保留physical primary0和新probe引用，建立实际fresh guard，再执行fresh full/selected；v2 packet/probe旧map不能当v3证据。本作者只compile四份源码为codeobject并未执行，当前仍是 Source-only pending review/runtime。小exactdiff、原failure引用和各不变合同在 source-contract.json 的 exact_leaf_admission_expansion_v3。封存 STOPWRITE，后续修正只能新packet。
