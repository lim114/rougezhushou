# 第115节最终归档与报告核对清单

v2纠正清单编写期间的状态变化：19:37:44 UTC快照中精选及两端依赖退出已是0，故从待齐项移至已有证据；v1原写作时间线保留。

本清单是只读源码及 Root 普通 JSON/原始退出文本的磁盘快照复核。未运行项目、API、tests、Qt、Wine、helper、native、gzip 或 Git；未改仓库文件。具体观察时间、文件存在性、原始退出值及 SHA 见同目录 `OBSERVED_ROOT_RECEIPTS.json`。该快照可能早于 Root 后续完成的执行，不替代最新收据。

## 已有实际证据

| 项目 | 原始退出文件 | 对应收据/记录 | 本次观察 |
| --- | --- | --- | --- |
| 115原件公开API | `section115-original-api-actual-v1.exit-code` | `section115-original-api-actual-v1/observations.json` | 原始退出0；属于原件观察，完整候选结论另由配对审计证明 |
| 115候选公开API | `section115-candidate-api-actual-v1.exit-code` | `section115-candidate-api-actual-v1/observations.json` | 原始退出0 |
| API完整配对与网上算例 | `root-section115-api-accuracy-actual-v1.exit-code` | `root-section115-api-accuracy-actual-v1/receipt.json` | 原始退出0；Root收据为完整通过，19原件/19候选，190原生记录、152实际调用、66公开来源叶文件；4个名义算例相符 |
| 115定向Linux/Wine | `resume115-related-linux-v1.exit-code`、`resume115-related-wine-v1.exit-code` | 同名 `.json` | 两者原始退出0，各72运行/72通过/0失败/0错误 |
| 115功能专项真实窗口 | `section115-window-actual-v1.exit-code` | `section115-window-actual-v1/receipt.json` | 原始退出0，当前Source758 |
| 功能专项窗口Saved读回 | `root-section115-window-saved-actual-v1.exit-code` | `root-section115-window-saved-actual-v1/receipt.json` | 原始退出0；66记录、4完整状态、4三文本组/12完整字符串、2独立SP配对、关闭重载；不重复执行产品 |
| 功能专项两图实际像素检查 | 无另造退出码 | `root-window115-specialized-visual-actual-v1.json` | Root记录确已查看两图。术师伤害表及医疗独立生命回复表完整可见；医疗其他表有裁剪，不称两图完整覆盖所有表 |
| 当前Wine能力诊断 | `full115-capability-actual-v1.exit-code` | `full115-capability-actual-v1.json` | 原始退出0；只证明环境能力观察，不等于产品通过 |
| Linux可用全量 | `full115-linux-actual-v1.exit-code` | `full115-linux-actual-v1.json` | 原始退出0；2394运行、2171通过、84历史/声明skip、192 unavailable/151父项、0失败/0错误 |
| Wine可用全量 | `full115-wine-actual-v1.exit-code` | `full115-wine-actual-v1.json` | 原始退出0；2464运行、2251通过、87历史/声明skip、186 unavailable/145父项、3环境能力skip、0失败/0错误，Source/CORE/adapter漂移均空 |
| Wine精选 | `full115-selected-actual-v1.exit-code` | `full115-selected-actual-v1.json` | 原始退出0；1459运行、4skip、0失败/0错误，Source/CORE/adapter漂移均空；未从run减skip推导PASS数 |
| Linux/Wine依赖检查 | `full115-linux-pip-actual-v1.exit-code`、`full115-wine-pip-actual-v1.exit-code` | 两者同名 `.log` | 原始退出均0；归档保留实际命令及日志 |

以上相对路径均位于 `/workspace/.continuation`。计数照实际收据字段分别报告；unavailable记录/父项和test运行数不是可直接相加的分区，不能据此反推通过数。Wine三个能力skip与普通skip行重叠，不能再加到87上或计为通过。

冻结产品依据为 `resume115-final-source-v1.json`，实际维护Source为758，guard SHA256为 `9ee50ae4aed69d3bd901f5925b24af00fea6ac60a2dc79fa9aed2b50d2625ba4`。Linux/Wine后已有 `root-full115-after-linux-Source-continuity-v1.json`、`root-full115-after-wine-Source-continuity-v1.json`；最终所有运行后的完整Source/CORE守恒仍需 Root 单独闭合。

## 当前仍待闭合的原始证据

下列路径是本次快照中的待检查项。存在原始退出0、对应完整收据且正确Source绑定后才能改状态；仅有log、Source草案、激活清单或部分进度不能算通过。具体最终路径由 Root 实际执行绑定；若名称变化，保留原始名字并更新归档清单，不生成伪退出码。

| 项目 | 待齐路径/绑定 | 必须核验 |
| --- | --- | --- |
| 受控52状态完整窗口 | 实际输出目录、supervisor JSON、external primary exit、child exit/log待 Root 绑定；可采用 `full115-window-primary-v1.exit-code`、`full115-window-supervisor-v1.json`、`full115-window-actual-v1`，但本快照不把这些建议名当已有执行 | 无超时、实际child/primary/supervisor退出0、原完整4283检查/52状态闭合、Source/CORE不漂移、10唯一113准入、launcher闭合、没有live owned执行 |
| 全量窗口Saved | 实际 `root-full115-saved-audit-v1.json` 与 `.exit-code`/`.log`待 Root 绑定 | Root实际完整解码，52结果/调用者/三完整当前文本、四PNG字节、10精确准入/42原投影、对应原始退出与supervisor绑定；不是只读准备证明 |
| 全量四图像素检查 | Root实际四图视觉收据，路径待实际绑定 | 实际查看对应PNG；保留裁剪/显示范围，不由文件hash推导像素正确 |
| 最终Source连续性与本节/全量归档 | 最后Source/CORE守恒收据、`verification/sections/115.json`、`verification/full-115`及本节research manifest | 所有原始结果同一冻结Source，manifest按实际字节/SHA闭合，无私人状态、无 `public-state` 或 `__pycache__` 混入 |
| 发布与远端保存 | `section115-publication-v1.json`；实际commit/push退出与remote HEAD | 真实逐节commit/push；local HEAD=开发分支remote HEAD，工作树干净。Source清单和“READY”不证明已提交 |

全量窗口契约的4283/52来自未改原功能矩阵，不是本复核实测值。`full115-root-activated-source-v1/ROOT_SOURCE_ACTIVATION.json` 与 `root-full115-activated-Source-independent-byte-proof-v1.json` 是Source激活/字节检查，字段明确为runtime未通过；不能填入运行PASS位置。

## 全量窗口归档必须保留的解释

- 原831个Assert的AST/顺序、完整功能Try与三份原公共literal不改。52个历史投影中42个保留原Gold；10行只允许第113节原件/候选实际证明的观察窗口秒数/DPS变化。HPS不能排除。
- 每一准入都绑定当前完整调用者/当前完整类型化投影以及实际第113节pair-audit；不是把新结果写回旧Gold。行21只有两个明确的历史JSON tuple/list表示缝，按实际3项类型与顺序限定，不能全局宽松化容器类型。
- 已有完整原生090语义证明是表示出来的类型、字典顺序和浮点位。不能据此声称跨分支容器alias身份或完整旧full-result Gold相等；旧52 Saved也没有各formatter后分别独立的图快照。报告必须说明这些尚未验证的边界。
- 无live owned执行不等于进程条目完全消失。若实际supervisor记录Z条目，保留它们并说明是已终止僵尸；不能称已经reap或完全absence。
- 原第95节三次未完成全窗口及原第109节三次未完成完整候选窗口继续搁置，不由第115节另一有界流程覆盖。

## 网上准确性检验的报告范围

实际已有4个合格比较：原始攻击500/名义防御800/法抗50得到物理25和法术250；原始攻击1200/名义防御800得到物理400；阿米娅S1七级攻速100+60=160、基础间隔1.6秒得到1.0秒。源码/输入/输出及来源URL、版本、下载字节都应归档。

原Wiki原文使用近似符号，结论是给定名义输入下算例一致，不是当前客户端实际战斗精确测量，也不能将A级评级普遍等同800/50。TapTap原段落S1/S2笔误保留，并以固定Wiki/本项目catalog确认S1；不能从间隔核对扩展为首击、前后摇、命中次数、SP或完整回转准确性。

第五个IS5真实伤害图片例的条件、版本/来源与显示舍入未闭合，收据明确 `apply_ready=false`、`Root_executed=false`、`actual_result=null`；继续排除，不凑成五个通过算例。

## 最终报告必须保留的未完成范围

沿用 `final115-progress-remaining-source-v1/README_ZH.md`：P2未闭合，不能宣称转入P3；藏品/本局强化、技能真实时序、条件天赋/模组/召唤物与环境仍有证据缺口。深海色热更新与实际面板独立核对仍未完成，111尾段修复不删除这项。地图/事件/路线/出怪/敌人机制数据、聊天多客户端、安装交付仍待推进；识别优化继续最后统一处理。

Linux/Wine结果只覆盖当前可用维护范围，不能称整个仓库全部PASS、原生Windows/游戏/聊天认证或自然OCR实机测量。保留 missing migration evidence、unavailable与历史/能力skip，未知机制不填成完成。

## 文档和保存的最后一步

111–114现有Root publication JSON各自记录真实commit/push退出0、local/remote一致、clean；它们是已有Root证据，本复核未重跑Git。具体SHA见快照。115 publication本次尚缺，未来提交/remote保持null。

全量闭合后Root将完成项、当前断点与本批总结更新到115；`PROJECT_PROGRESS.md`只保留剩余事项。`DEVELOPMENT_CHECKPOINT.json`和`WORK_IN_PROGRESS.md`明确本批结束、不启动116；逐节保存规则与旧失败记录仍保留。最终报告附实际开发分支GitHub提交链接，不用草案、当前日志或“准备提交”充当远端成果。
