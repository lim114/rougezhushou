# 380完整本机验收候选：仅缓存准备

本目录没有创建attempt、source-freeze、activation或公开full380回执，没有运行任何正式检查、Qt窗口或全量。所有将来的退出码、统计、380源码哈希和截图数均未知。准备者是 `/root/full380_prepare`；执行与真实看图的人须按实际记录。正式源码、HEAD和私人状态未改。

## 已保留的范围与真实风险

- 真实完整365是范围底线：598个有序选择器、80个P3原生窗口；102份旧legacy/current模板逐字节复制且对应原365冻结。旧52状态、4283完整typed核对、862断言、552主体SHA、42投影、156正文请求均保留。原30与独立29分别真实执行，不把29替代原30。
- 声明阶段从正式树重新取得完整selectors/source maps，并从366–380动态发现所有新native脚本和各自实际 `bound_files()`。缺一节拒绝冻结；不会把只有准备候选的380说成已安装。过去598/80不冒充380的实际计数；如每节正好一个新增native，预计95个P3与100个总位置，但这仅为预计。
- 304、305显式 `--source-freeze <本轮真正freeze>`；312保留原120秒默认；311已有300秒、334已有180秒 profile。新增脚本读取各自真正 `--visible-ms` 默认，不统一缩短。每个P3 supervisor仍1200秒。没有“识别更快”之类推断。
- 上次完整365从根启动到全部终止约2小时16分；本次新增15个native，实际耗时不预先承诺。冻结至真实归档期间不能改源码/HEAD，也不能并行重叠运行正式窗口验证。
- WinError1314只有原30真实出现旧符号链接操作且独立29通过时，才可明确记为不可用；任何其它失败必须修复/重新独立全量，不能放宽为“环境问题”。原Linux/Wine/历史原Windows私样本、游戏和聊天未取得仍不计通过。
- 原365失败首轮与成功第二轮保持历史原件。本次sealer不强制复制旧313修复流程；若本次确有失败，必须原样归档，后续明确新attempt，不覆盖、自动重跑或拼合PASS。
- 静态准备不是实际验收。原源map/实际receipt schema若拒绝，保留原失败、查明原因再做有据适配。不能删断言、少执行组件或把图片外观当交互证明。

## 根代理在真正380功能完成后逐步执行

以下均为将来命令。不要一口气执行；先核上一阶段真实结果。先完成380实际必要/原生功能验证，三份路径必须填实际成功回执，不猜attempt1。`functional-receipts.actual.json`应放cache，结构如下（占位文本不是事实）：

```json
{"section":380,"references":{"necessary":"真实必要process.json","native":"真实原生actual/window.json","native_process":"真实原生process.json"}}
```

```powershell
# 1. 正式源码已定稿、当前380功能三回执确实匹配字节，且没有既有全量正在运行。
& .venv/Scripts/python.exe -B -X utf8 .cache/full380-prepared/materialize_full380.py --prepare-only --attempt 1
$full380Capsule = Join-Path (Get-Location) '.cache/full380-prepared/attempt-1'
$full380Parent = git rev-parse HEAD

# 2. 从此阶段开始正式源码及HEAD保持不变，直到真实终态归档完成。
& .venv/Scripts/python.exe -B -X utf8 "$full380Capsule/declare_current380.py" --source-finalized --expected-parent-commit $full380Parent --functional-receipts .cache/full380-functional-receipts.actual.json
$full380Freeze = (Get-FileHash verification/full-380/source-freeze-attempt1.json -Algorithm SHA256).Hash.ToLowerInvariant()

# 3. 绑定仅改fixture的来源字面量，旧主体/断言完整保留。
& .venv/Scripts/python.exe -B -X utf8 "$full380Capsule/activate_full380.py" --activate --expected-parent-commit $full380Parent --freeze-sha256 $full380Freeze
$full380Activation = (Get-FileHash "$full380Capsule/activation380.json" -Algorithm SHA256).Hash.ToLowerInvariant()

# 4. 唯一一次明确执行。工具返回仍运行时保留原handle继续观察，不另起全量。
& .venv/Scripts/python.exe -B -X utf8 "$full380Capsule/run_owned_full380.py" --execute --expected-parent-commit $full380Parent --freeze-sha256 $full380Freeze --activation-sha256 $full380Activation

# 仅状态读取，不能代替原retained handle的真实结束观察：
& .venv/Scripts/python.exe -B -X utf8 .cache/full380-prepared/inspect_execution380.py --attempt 1

# 5. 所有原任务和assigned jobs真实终止后才归档，失败原件也必须保留。
& .venv/Scripts/python.exe -B -X utf8 "$full380Capsule/archive_full380.py" --archive --expected-parent-commit $full380Parent --freeze-sha256 $full380Freeze --activation-sha256 $full380Activation
$full380Archive = (Get-FileHash verification/full-380/execution-attempt1/archive-manifest.json -Algorithm SHA256).Hash.ToLowerInvariant()
```

根 `run_owned_full380.py` 自己保留Popen并将实际退出写入原件；观测超时不等于进程终止。只读状态工具不会重启、杀PID或判通过。若根handle中断仍先查真实job/process，不凭锁文件认定已停。

## 真实终止后的图片处理

现成公共365注册表 `verification/full-365/public-prior-plus-attempt1-appearance.json` 真正包含当时最终509路径所需外观来源；只在当前完整PNG逐字节相等时可复用真实原审阅者和方法。可直接使用这份原公共注册表，或用 `extend_visual_registry.py` 将已完成366–380的真正公共 `N-visual-agent-review.json` 中逐图直接审阅记录加入新缓存注册表，再逐字节复制到公开full380目录。不能把root包装清单当root看图，也不能把contact sheet改成新direct。

```powershell
# 可选，且实际--review-file可重复；只写新cache，不新看图。
& .venv/Scripts/python.exe -B -X utf8 .cache/full380-prepared/extend_visual_registry.py --prior-registry verification/full-365/public-prior-plus-attempt1-appearance.json --prior-registry-sha256 68242af73b3a8fa04d26f6de5792dc66169e6778d8a82803e994b25bf6e51f53 --review-pair verification/sections/375-visual-agent-review.json verification/sections/375-native-attempt1/process.json verification/sections/375-native-attempt1/actual/window.json --output .cache/full380-prior-visual-registry.json
```

新注册表复制到公开 `verification/full-380/public-prior-visual-registry.json` 后，核真实SHA再传给库存工具。库存只把真实终止archive内的每个PNG路径列出，匹配不到的代表图留为未看；同SHA重复也不会自行变已看。

```powershell
& .venv/Scripts/python.exe -B -X utf8 .cache/full380-prepared/actual_png_visual_inventory.py --archive verification/full-380/execution-attempt1 --attempt 1 --archive-manifest-sha256 $full380Archive --registry verification/full-380/public-prior-visual-registry.json --registry-sha256 <实际公共注册表SHA> --actor /root --output .cache/full380-visual-inventory-attempt1.json
```

把原库存逐字节复制到公共 `verification/full-380/actual-visual-inventory.json`；真正逐张查看 `needs_actual_view` 代表PNG，独立真实审阅者的每行需file/sha/reviewed/method=direct_view/review_actor/actual_new_view_image_called/actual_pixels_visually_reviewed/visual_blocking_issue/observation。实际part放公开full380目录；不能只将库存的false改true。之后：

```powershell
& .venv/Scripts/python.exe -B -X utf8 .cache/full380-prepared/compose_final_visual.py --inventory verification/full-380/actual-visual-inventory.json --inventory-sha256 <实际公共库存SHA> --actual-direct-part <真正公共看图part路径>
```

若完全无需新看图，省略所有 `--actual-direct-part`，但仍逐字节重核原证明。组合工具不看图、不跑窗口、不创建语义PASS；strict sealer再核完整PNG路径集、registry叶证明、实际actor、真direct或无环同字节复用链。

## 实际完整结果的严格seal

先把候选 `seal_summary380.py` 原样复制到 `verification/full-380/execution-summary380.py` 并核字节；实际summary内记录公共sealer而非无法云端读取的cache路径。再取真正review helper/最终视觉哈希：

```powershell
$full380Review = (Get-FileHash "$full380Capsule/review_results380.py" -Algorithm SHA256).Hash.ToLowerInvariant()
$full380Visual = (Get-FileHash verification/full-380/root-visual-review.json -Algorithm SHA256).Hash.ToLowerInvariant()
& .venv/Scripts/python.exe -B -X utf8 verification/full-380/execution-summary380.py --seal --attempt 1 --expected-parent-commit $full380Parent --freeze-sha256 $full380Freeze --activation-sha256 $full380Activation --archive-manifest-sha256 $full380Archive --visual-sha256 $full380Visual --review-helper-sha256 $full380Review
```

只在全部当前证据严格满足时才创建 `verification/full-380/summary.json`；不会覆盖既有summary或改原archive。它核当前整个原range、所有组件实际argv/retained exit/job终态/来源closure、全部旧typed内容、完整source freeze、真实功能380三回执和全部实际PNG。`complete_repository_validation/P3/P2/P1_complete`均保留false，不把当前完整可用范围通过当工程全部完成。

完成后根代理仍需正常原项目测试窗更新可见响应、保留五私人路径、按现有流程同源码/要求/索引普通提交与push、核真实remote。380后暂停，不启动381。全量运行不能替代普通发布核对。


### 显式配对普通逐节视觉回执（缓存适配，尚未调用）

现有371–380普通视觉回执可能没有内嵌process/native gate，因此使用可重复的`--review-pair <原review> <实际成功native process.json> <同一原生actual/window.json>`。每个实际已审图的章节各给一组，按该节公开最终receipt的`native_windows_validation.receipt`和`.process.receipt`取真实成功attempt，禁止一律猜attempt1。371/372已知最终是attempt2，374是attempt3；后续以实际该节receipt为准。375的命令仅是已存在示例，不是全371–380覆盖。

配对工具严格核原review不改、同节、真实0退出与process.exit、准确window SHA及argv绑定、原生Windows成功终态、原process/native前后source map相同，以及原review与原native全部图片路径/SHA集合完全相等。历史source map不要求等于380当前源码，因为这里只复用同字节外观，不能借旧运行证明380语义。未曾真实看过、看图失败、来源不匹配或未配对的记录不能加入；无相同PNG SHA的本轮图片仍全部待看。原有内嵌gate格式仍可走`--review-file`，同样接受严格绑定检查。
