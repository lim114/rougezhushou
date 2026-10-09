# 第100节 Source v2：界面培养消费资格与本局独立证据保留

这是可应用、可运行测试的完整 Source 候选，尚未由作者导入或执行。Root 尚须在实际完成98/99的源上运输、独审、运行29个 unittest 方法、相关回归和真实项目窗口，才能完成小节。本文不把 Source 审阅、独立 Qt probe 或 Linux catalog 原有 ValueError 当作项目窗口 PASS。

范围严格限定 UI 消费：已知干员的有效账号/本局培养混合进入阶段/技能索引、QSpinBox、时间格式化和原始 summary 之前使用安全只读投影；不会新增完整 RunState schema、改变99持久化、重置当前本局或改任何游戏机制。本局原始成员、账号记录、文件与 caller 保持原样。

产品是 `candidate/rouge/training_view.py` 与 `candidate/tests/test_training_view_100.py`，包含真正可运行的29个 unittest 方法。`app-current-operator-state-increment.txt` 给三个方法的 Source，`exact-app-local-transports.json` 给五个明确限定所属方法、原文、替换文和唯一次数的增量，不整份覆盖 app/run_state。缺省 fields 修复已由98负责，本节只是运输时继续沿用，不重复计成果。

正常有效记录保留旧语义：本局有效字段优先，账号仅补字段，本局技能不填账号技能；被 invalid mask 屏蔽的旧值不检验，锁定技能的 formatter-safe 原类型、无技能档案等级、falsy 模组身份的未使用阶段、非选项 selected_skill 和未知额外键保持原安全行为。先检查实际混合，再检查去掉账号补足的本局上下文；不能先按本局默认精二拒绝原来由账号精零约束的锁定 rank=99 安全混合。

资格副本用可信当前选项 op 查询既有 `_record_issue` 培养政策，去掉其账户专属 scope/时间和等级范围政策；不把成员 id 的缺省或 opaque 元数据变成新 RunState schema。未实现干员及原始 run summary 的 formatter 使用当前选项身份的读投影，原 id 元数据不改。原始 summary 只使用实际 formatter 的异常门，旧 formatter 可显示的原始字段文本仍原样显示，不套计算培养 schema。

Root 已执行并保存真实 Wine Qt6.9.3 的边界原件：

- `section100-qt-probe-actual-wine-v1.json`：153770 B，SHA256 `093c89213681671f0f390cc4c4ff1d1878251c2b1bc650c1d2ae26419864a078`。Root01aaef/session48441启动、e8af6c primary0、raw0；222等级及13时间观察。
- `section100-qt-probe-fraction-actual-wine-v1.json`：67369 B，SHA256 `2206388cfe1154da0117735cc955b0538ce8de4b0bcdd73e9ac17edf17d74c12`。Root7ccdd2 primary0、raw0；102等级观察。

原件证明 bool、普通整数及有限小数由实际 setter 截整数并夹取；int32闭区间两端安全。`-2147483648.9/.5/.1`、`2147483647.1/.5/.9` 在截整数仍落int32时也安全，所以新门不能直接对原float作int32范围拒绝；先 `int(value)` 再检验int32。None、文本、容器类型实际TypeError；越界int/float、巨型值、inf/nan实际OverflowError。这里的int32是已测实际UI binding转换边界，不是干员等级schema。原值与类型不规范化、不写回；QSpinBox仍拥有原截整和夹取。

`preserve_level` 分支没有 setter，Root两次probe全部该分支无异常。因此保存等级即使None/字符串/数组/巨int，在用户等级override而未使用时都不拒绝其它有效字段。新 `current_operator_state` 明确接收 preserve_level，`update_operator` 必须通过精确单行传其当前实参；其它读取按现有 level_override 使用。

时间只按原UI `time.localtime/strftime` 的实际平台调用资格：None、bool、0、100.5在Wine都安全；Wine -1实际OSError，Linux可能可用。没有新全局时间规则、字符串解析、时间裁切或时钟修改，原生Windows仍未验证。

v1 Source 独审指出培养fallback会丢独立招募/个人强化，v2已将数据流分开：培养当前不可用时继续安全账号/明确预览与原来源label；`current_run_operator_state` 只沿原 enabled/present/scope run 门读取原成员不透明metadata，calculate的五项招募/强化scenario与sync_target_buffs使用该独立来源，其余培养state/确认labels不变。本节不扩充强化叶子schema，不替代现有来源与生命周期资格。新增四个纯函数方法只证明保留/gate，public占位字符串不代表数值机制验证；Root窗口必须用已有真实公开SNACK `rogue_6_from_relic_13` 等固定合法fixture确认有效强化+培养fallback及开关/离队的数值和三报告。

Root推荐实际验证顺序：

1. 重新绑定已完成96–99的开发分支、Source清单与app方法AST。运输两个新文件、三个app方法和五个局部增量；保持其它Source完全不变，不将old snapshot整份覆盖新维护。
2. 执行29方法文件及account093、training input、98运行记录可靠性、99文件IO、recipient063、emergency recruitment、observation workflow相关回归；记录真实失败与退出码。正常输入与masked/unused边界保持原native类型、caller/files和已实现输出。
3. 运行实际可见MainWindow：非法精英/活动rank/时间/Qt溢出、缺少账号时明确预览、有效混合与补足冲突、float/int/bool夹取、等级override、未实现干员身份读投影、raw summary，逐一点击选择输入并核对响应。已有原 Linux catalog接口对elite=[]返回ValueError的21994b回执，仅证明已有数值接口保护，不能当作此前Qt崩溃。
4. 用固定公开有效招募/个人强化记录＋培养fallback核对实际数值、强化显示、伤害/治疗三报告。开关off、离队与非run scope不得供本局metadata；没有新增激活/叠加/概率假设。
5. 保存Root实际runner/source hashes、日志/raw/receipt、真实窗口图像和checkpoint，再提交推送。完成第100节后按用户五节节奏运行全量可用Linux/Wine/窗口并总结；full95历史搁置和原生Windows未验证不能改成PASS。

原盘保护边界：此UI门不调用reset/save，也不声称任意持久培养叶子已在构造迁移保存前保护。若Root另决定扩展保护，请先按v1 `OPTIONAL_ORIGINAL_PROTECTION_SOURCE_NOTE.md` 的真实公开配对观察必要性；本v2产品不修改99 IO或序列化，不把正常账号/本局混合不兼容当作原文件损坏。实际用户损坏频率、游戏采样是否产生这些类型和所有既有未知机制继续未知。
