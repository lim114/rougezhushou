# 一个后续 P2 RunState 可靠性工作组的设计边界

这只是 Root 当前095公开实际 leads 之后的 Source 设计，不是 098 candidate/test 实施，不是 098 baseline/validation。PROJECT_PROGRESS 的优先级1“本局强化状态与计算完整性”不能解释成恢复暂停的开发阶段 P1。本组仅改善已存在离线状态与直接输入的证据资格，不推进原持续采样链、真实招募/进阶事件规则、旧局恢复、多页库存合并或识别优化。已确认数值与未知数值边界不变。

**现有处理与反证。** 当前 run_state.py 42446B / SHA256 `20c6a00a72744017ebbc0fcb3b1009dddf8a6702aa01bf273b4b51c344692fd9` 与公开 archived author089 draft 字节完全相同；相对 archived pre089 42402B / SHA256 `6d36bc955af40aff99ac9079706342b67e6df0bc8d1f93e55e2cc580cabcbdac` 唯一变化是 crew bool→None。旧研究已经处理 crew bool、保留非 bool 旧兼容，不包含这次五种深层缓存结构和 relic count bool 的修复。当前构造器 18–29 行只校验 top/operators/relics dict，再 shallow state.update；仅捕获 FileNotFoundError/OSError/ValueError。旧 full-bar memory migration 159–181 行已有 type(count) is int；reconcile 210 行已有严格 int complete_bar，但 apply 336–371 行的 equality、count assignment 和 removals 不含局部 bool 防护。这些局部已有资格判断不能闭合整个 apply。上述反证不等于断言所有历史研究从未涉及任何类似问题；范围是精确 pinned 089 与当前维护代码，以及这次已读取 Source。

**A：离线加载前资格判定。** 在 parsed saved dict 安装到 state、同局旧数据 migration 或 repair 前，校验此次确切已复现的 consumed shapes：若 maps 存在则必须是 dict，其 graph 值必须是 dict；operators/relics 当前必须是 dict 且各 record 必须是 dict；若 history 存在则必须是 list 且各 event 必须是 dict。不存在的可选旧字段沿用原 defaults，保留 valid old snapshot 的既有同局 migration。资格失败进入已有 ValueError/unreadable 处理，用现有保存阻断与 notice，完整保留原磁盘字节。不能 broad-catch 运行期 AttributeError 或在已经 shallow-install 后直接吞异常，因为这会保留部分不合格状态，并掩盖 unrelated programmer failures。

现有构造器的 reset(save=False) bootstrap 保持原序与行为；设计不新增 reset/save、不自动删除或清空缓存、不修补/union 坏记录、不恢复历史另一局，也不替用户点击手动 reset。磁盘原文件不变；已有合法本局状态、自然 id/time/history 及正证据不变。不要把这个有限 structural gate 扩写成数值清洗、完整递归 schema、自动修复 saved bool 或账户 IO/Unicode repair。map.nodes/history 的其它嵌套字段、unknown IDs、tactical_tools/config/resources/relic_icon_memory 等其它深层形状，这次并未复现，不能宣称已覆盖；若未来选择扩大 gate，先固定当前 Source 的实际消费合同并用独立公开案例复现边界，再定资格，而非猜测 schema。

**B：直接 observed relic count 的局部 bool 资格。** 保留 apply 的 stale/cross-run early return、char_buffs 原异常及 restore_origin_discovery_buffs 的原调用顺序。在已有 `relics=dict(observed.get(...)); count=relics.get('count')` 本地副本处，仅把 bool count 视为 unread（本地 count 与本地 relics['count'] 同步为 None），且要在 reconcile 和 count/completeness/removal 消费前完成。调用者 observed 中的 False/True 不能被改写。不能只改本地 count、而把 bool 留给 reconcile，也不能把 bool 转成 int0/int1。

这次的 bool inputs 应与同一 seed/同一 icon observation 的 None 控制组的产品结果配对：保留既有三件正证据与 prior int3；完整性只能来自原有效证据，不能把坏数量当作当前零/一件的移除证明。真正 int0/int1 的合法对应移除、None/missing、其它 nonbool legacy count、正卡片/道具、partial/duplicate bars 和 grade correction 维持原路径。crew float0.0/string0 的测试合同尤其保持不变。不新增计数上限、不扩展负数/float/string规则、不修改游戏事件叠加/丢失/重获含义，也不追溯重写已保存的 bool 状态。

**Producer 闭合仅限 Source。** near_number 68–97 行从 int(text) 构建候选，唯一候选返回 int、确认零返回字面 int0、其它返回 None；verified_zero 的 bool 仅作 predicate。read_run 122 行取得该值，138 行遇非空 icons 把零改 None，185 行输出 count；ScreenReader 267 行传递 run，275 行 event fallback 明写 count=None。exact-frame reuse 76 行复制之前的 produced result，不合成 bool；visual fallback 137–140 行明写 count=None。这些当前常规 Source 路径没有 bool producer，且未实际运行 producer/OCR/图像。这次确认的是 RunState 的公开直接输入防护需求。

**选择与后续真实验证。** 完成并封存实际095、096、097后，Root 再取真实后续 baseline Source guards；本次 current735 lead receipt 永远不改名为098 baseline。当前所有这些未来 gates/results 为 NULL。选择本组后，先用相同原始 public fixtures/实际 shared seed 做维护 baseline 与 candidate 的 paired 实际运行，逐 case 记录调用/异常、本局 id/自然时间、native types/完整图和 caller immutability、whole raw before/after/temp、history 与可见消费者。计数来自实际 logs；异常不能作为产品通过，进程0仍只是采集完成。

加载边界至少验证这次五个 malformed shapes 都可安全使用 fallback 消费者、保留完整原文件且保存阻断有效；有效省略 defaults、正常完整状态以及旧 full-bar/map/origin evidence migrations 保持兼容。还需实际复核 malformed JSON/顶层现有 ValueError guard、后续正常 apply 与保存阻断的组合，及用户手动 reset 原行为；任何新增 nested shape/ID/schema 承诺要先完成独立公开复现。原 startup 当前保护旗标全为 False，不可把 raw 保留误作已测过 gate。

库存边界验证 False/None/int0、True/None/int1 和 missing 的 paired distinction，保持 int0/int1 的正常移除、None 的正证据留存、正 owned card/tool、新身份及当前难度 tier 修正、duplicate/partial bars、stale/cross-run、bad char_buffs 原异常顺序和 caller/alias合同。现有 crew float/string compatibility、empty inventory、inventory tool/snapshot/catalog、origin discovery、run config/recipient/counter 相关回归按最终范围实际运行；不重跑无关大范围检查来冒充新证据。旧保存 bool 重启是尚未实际观察的独立边界，不在此设计中自动修复。

最后需要完整 paired damage/API/三份报告的产品消费与临时状态 MainWindow 真实验收，记录合理 Source guard、调用数量与原 raw/exception evidence；当前这次只测 summary/inventory_status/held_relic_ids/held_tool_ids，未运行这些更广产品消费者、真实窗口或 native Windows。无需也未安排私人截图、游戏采样或聊天。所有未知 native event/clock/stacking、账户真实激活和当前热更新对面板的依据继续延期。
