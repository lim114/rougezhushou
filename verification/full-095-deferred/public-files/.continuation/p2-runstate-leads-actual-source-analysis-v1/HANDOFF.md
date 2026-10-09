# Root 过去实际 lead 观测的只读 Source 分析

这是一个独立 sidecar；原 audit 与 sealed probe Source 包保持 STOPWRITE。此次分析未执行或导入项目、测试、codec/helper、Wine、Git，也未操作进程、游戏、聊天、私人缓存或计划任务。分析自身 `runtime_executed=false`、`completed_section_increment=0`、`Product_PASS=NULL`。Root 过去实际执行是另一层事实，不能混写成未执行，也不能把采集进程 0 写成产品通过。

Root 的原始 receipt 是 908064B，SHA256 `16dd55c6295a1c2894d3c80f7d58ee9b4746ca5bbe67dc8bf4a6fb38b8ce8630`。原字节及 Root observation/console/exit 文件完整复制到 `actual-proof/`。Root observation 记录 launch chunk `f394a6` / session `99700`、completion chunk `48172e`、实际 primary exit `0`、launch 2026-10-09T02:03:50Z / completion 02:04:27Z；进程开始时间没有独立捕获。这里是读取过去证据，并未重复运行。

14 个实际 cases / 551 个 `run_state.py` 源码 body entry。551 包含 module 1、class body 1、generator/lambda entries，不能写成 551 次显式产品方法请求。实际 case records 记录构造请求 14、apply 请求 8、已返回构造后的显式四消费者请求 44；内部 reset/save 与消费者嵌套调用的计数另见 `actual-counters.json`。receipt 过去的 whole735 Source before/after 精确相等；guard 是 84227B / SHA256 `41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab`。这只证明此次公开 lead 采集的 maintained Source 未变。

已复现的 syntax-valid 离线结构边界是 maps=[]、maps graph=null、member=null 构造抛 AttributeError；history=[null] 构造返回但 summary 抛 AttributeError；relic=null 构造返回但 summary、inventory_status、held_relic_ids 抛 AttributeError。详细真实 type/message/frames、未调用消费者的原因、原始 native 与 whole raw 见原 receipt 和 `startup-observation-index.json`。全部 6 个 startup fixture 的 original raw、raw before、raw after 精确相等，`.tmp` 前后不存在，但实际 `preserve_unreadable=False`：文件保留是因为未发生 save，不能证明这 5 个结构已有防覆盖保护。没有私人损坏缓存、真实游戏出现频率或真实窗口启动复现。

bool 库存是 direct observed input 边界。False empty 将两藏品和一道具的 `held` 设为 False；True one 只保留 cargo_1 held=True，fight_26 和 tool_5 held=False。相应消费者返回 complete=True，total_badge_count 的 native 类型仍是 bool，summary 分别显示 `0 / False`、`1 / True`。这里的库存状态字段是 held；relic 记录的 present 字段实际不存在，不可套用 crew 的 present 语义。真正 int0/int1 对照有对应合法移除结果；None 与 missing count 对照保留原 int3 与三件 held=True。7 个 subjects 都由同一实际 seed 的完整 raw bytes 开始、caller before/after native 精确相等、apply 返回 native bool True。全部 raw after 改变，包括 None/missing 控制组，不能仅凭文件改变判定缺陷；正常 last_read/notice/正证据与 save 也会改变文件。

当前 `near_number` → `read_run` → `ScreenReader` 的已检查 Source 分支及 visual/event fallback 闭合为 int/None。没有 Source 或实际证据说明当前 producer 输出 bool，也没有运行 OCR 或图像识别。这支持局部 RunState 输入边界防护，不支持声称识别引擎曾读出 bool。

可进入后续设计审查的是一个 coherent P2 RunState 离线/输入证据可靠性工作组；未创建实现或测试候选。它不恢复开发阶段 P1、不改变任何未确认事件/叠加/时钟数值、不重复 097 account save 修复、不新增 Source collection milestone。具体资格判定和验证边界见 `DESIGN_AND_VALIDATION.md`。future full095 saved-batch、096、097、098 baseline guards/results 均 NULL；Root 最新报告的 full095 UI 仍运行，不由本包更新为完成。

旧 contract 的 “never recognition APIs” 过宽，已在 `SCOPE_ERRATUM.md` 明确撤回。实际 import log 包含 relic_recognition/map_recognition 等普通依赖，普通 apply 可以调用 resolve_* 纯资料函数；helper 调用计数没有被 profile 全面测量，不作 whole-project 零 API 声明。

所有原始 encoded graph 的 object_id/ref、native types、float.hex、自然 UUID/时间、caller/state、raw before/after 均在原 receipt 原字节复制中保留；没有解码 raw_hex 或重建项目 native 对象。选择索引只在 JSON 编码节点中按已记录 string key 选取子节点。跨不同 capture/returned value 的相同 object_id 不能证明实时别名，因为原对象可能释放并复用 id。实际 MainWindow/Wine/native Windows、damage API、三份报告与后续完整回归仍未验证。
