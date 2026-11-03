# 陈原版阶段资料：候选功能与来源交接

这是一节可直接在实际产品中使用的原版动作资料查看功能，尚未应用或实际运行。

用户在陈的 S1 / S2 / S3 测算界面选择“陈原版阶段资料”的正面、背面或正背面对照，即可在普通报告、技术报告和结构化报告中查看相关原版动作条目、原始资源长度、全部命名事件偏移和各自来源。默认关闭；关闭后报告与原有计算完全一致。连续和逐帧模式均可查看，选择只存在当前界面的局部预览，按干员/技能记忆，不写培养、账户缓存或当前本局记忆。新增公共输入 `chen_motion_orientation` 仅接受 `Front` / `Back` / `both`，None 或省略关闭。

原资料过去只允许“普通攻击”成为逐击数值参考；循环、多事件、开始和结束条目均被封闭在原版资源 JSON 中，实际界面无法看到它们。新功能使陈的完整相关动作条目可见，同时保留该数值选择限制。**没有打开多事件数值 selector，没有把原版资源事件放进实际伤害、SP、回转或周期，没有改默认计算。**

可见范围（两面各自保留）：

| 技能 | 条目 | 归一化 30 帧/秒资源帧 |
| --- | --- | --- |
| S1 | Begin / Loop / End | 6 / 37 / 6；Loop 命名事件偏移 13、20 |
| S2 | Begin / Disappear / Attack | 17 / 5 / 37；前两个没有命名事件，Attack 原始 OnAttack 偏移 13 |
| S3 | Begin / Loop / End | 13 / 37 / 8；Loop 命名事件偏移 16、18、20 |

这里的“Begin / Loop / End”等为资源动作原名，展示次序只为便于查看，不代表真实执行顺序和循环次数。S2 普攻条目不证明它被用于斩击后强化，Disappear 的长度不等于斩击时长。S3 的三个命名事件不补齐剑气碰撞。每个动作事件以该资源自身起点为 0，不是技能开启时刻。所有技能实际命中和实际结束保持未知；S2 实际斩击结束和强化起点、S3 实际剑气碰撞亦保持未知。原有条件数值、本体小计和既有时钟均不变。

## 已读已有资料与公开原件

- `research/p2-chen-phase-reference/{NOTE.md,source-receipt.json}`：原有 S2 条件斩击、6 秒强化参数和 S3 单次剑气条件量，及明确未知的实际相位；沿用原证据，不把表参数推演为隐藏脚本。
- `rouge/data/original-animation-references.json`：现维护 Source 目录文件 SHA-256 `390deaa49bb353cface07b555c65a970b15a7ff1b58002008664e7872793ef53`，固定资源 commit `d0b5af0b004b044d322397ce5ae79632b6d9fcdd`。保留原始秒、原始浮点帧、严格 ceil、表示误差归一化帧和全部命名事件。记录仍标 `runtime_binding_verified=false`。
- 本次公开重新获取 Front / Back 固定版本 skel：`acquisition.json` 保留实际 HTTP 200、URL、读取时刻、原字节长度、SHA-256 与 Git blob 的独立核对。原件 `Front.skel` / `Back.skel`。没有关闭 TLS 证书验证，没有导入或执行项目、二进制 reader、native/helper 或 gzip；既有事件提取内容来自已编入的钉版原记录。
- Front 759966 字节，SHA-256 `ffb1cf1cad8b55780efe4d900f551da75d811dd7a8f101ffc53c118000732e9a`，Git blob `3697f6c6550659bf01258b9f0cf7575ef835e8cd`。
- Back 669821 字节，SHA-256 `590c3558a156d4556dc9b6261b3055ad1d7337b8a873d62c4fcacfd9a7627ca6`，Git blob `eceacbd2224429d418c07f69fd76550174a003fa`。
- 例如 S1 Loop 的资源时长浮点 `1.2333333492279053` → 原始 30 帧/秒浮点 `37.00000047683716`，严格 ceil=38、已有表示误差归一化参考=37；事件 13 帧也有同类表示误差。新界面保留这些不同口径，不把归一化当作实机帧法则。

## 候选与应用边界

`candidate/` 有完整 Source 候选，`baseline/` 保存实际原文件并哈希核对。`transport.json` 为 6 个局部 anchor 替换及 2 个新文件；全部是 Source，Root 自己审核和应用。原 `reporting.py` / `app.py` / `verify_cloud.py` 的完整基线 SHA 已记录，候选的逆 anchor 可恢复对应原字节。不能把旧整文件覆盖到已推进的其它小节：如原件已变更，Root 需逐个核对唯一局部 anchor 并重新生成候选及 Source guard。

涉及生产文件：新增 `rouge/chen_motion_reference.py`；`rouge/reporting.py` 一个纯展示 helper、一个调用；`rouge/app.py` 新独立资料选择器、计算输入接入、局部预览与可见性三块；`scripts/verify_cloud.py` 保留原顺序并新增 `tests.test_chen_motion_reference`；新测试 15 方法。没有改 `operator_engine.py`、`timing.py`、`damage.py`、公共 data 或原版 choices/descriptor。

唯一 Source 准备失败：第一次写 tests Source 时 offrepo candidate/tests 目录尚不存在，未写任何文件；创建该目录后重新保存成功，记录在 `source_review.json`。没有 runtime 失败或检查 PASS。

## Root 实际验证建议（本代理没有执行）

1. `public-original-candidate-inputs.json` 的 43 个公开调用输入，原件与候选各 1 次数值 + 3 个完整格式器。包含 3 技能 × 2 模式 × 四种显示选择、零窗口/零生命周期、高攻速专七、空供靶和显式本体弹道。完整返回图去掉恰好新 `chen_motion_front` / `chen_motion_back` 两类报告 section 后须与原件相同；caller 与每次 formatter 前后状态须保持；原件未知字段不代表原件已有资料功能。
2. 15 方法测试 Source 同时覆盖全部资源字段精确保持、独立深复制、事件顺序、严格 ceil 与表示误差口径、其它干员不消费该选项、不接受大小写/布尔/容器强制转换、原循环数值 selector 仍拒绝，以及完整图和三个格式器保持。不把 tests 或 Source 编译本身算作产品推进。
3. 实际 MainWindow：以公开暂存 RunState/AccountCache 放置陈，原先普通数值参考保持默认 None；S1 Front、S2 Back、S3 both 逐一切换，连续/逐帧都实际查看。检查下拉仅陈可见；切换到其它干员隐藏，回到原技能恢复该技能局部资料选择；关闭恢复原报告。记录每状态完整 caller/result/三文本、选择值、界面文字及状态读回；账户和局部本局公共替身结构前后保持。
4. 实际窗口图片至少显示一个完整可见资料小段与一个未知边界小段；全部 2 面长列表需 scroll，多图覆盖才可声称完整可见。不要因图片截断而声称未入图的所有行可见；源参考行与原报告数字要分别证明。
5. Linux 与 Wine 相关回归、实际 GUI 与读回复核全部由 Root 串行执行。Wine 为兼容验证，原生 Windows、实际游戏、当前热更新/皮肤、聊天仍未验收。本包并未证明这些完成。

## 待办销项边界

只可记录“陈 S1/S2/S3 正背面原版阶段动作资料可在产品中选择查看”完成。`PROJECT_PROGRESS.md` 的陈 S2 斩击结束/强化相位、S3 剑气碰撞仍保留；S1 开启/循环/结束的真实客户端绑定和原始资源到伤害事件的绑定亦未闭合。严禁以动作资源相加、循环命名事件数或新报告代替实际时序证据。
