# 第 61 节最终草稿独立审核

最终 patch SHA256 `b12e5ca02ca6587661e82651a2b586b0c563a78a18480250a9bbde490c44e27c` 独立审核通过，无 blocker。冻结基线仍为 HEAD58 `4543b9b91ac7b61fc019bb96a3d6d5ac2593a6bc`。121 个 runtime 文件重新校验无基线漂移，草稿仅 `rouge/operator_engine.py` 改动，除 `Combat.option` 方法之外整棵 AST 完全一致。patch 另含 8 个新测试方法以及第 54 节四个活跃整数参数 bool 预期的迁移；两个旧 inactive legacy 字段和原 capability guard 仍有验证。

原始只读来源审计建议显式余下字段集合；最终草稿采用现有 `integer=True` 查询契约，仅对 `healing_targets` 例外。独立核过当前所有 27 字段：`stolen_enemy_count`、`amiya_hit_targets` 与 `enemy_weight` 原来已经在公开入口拒绝 bool，未造成新增公开变化；余下 23 个有缺陷字段按实际调用点拒绝。`healing_targets` 在所有 plan 中查询，但拒绝必须仍经第 54 节 `has_healing` capability seam，否则会改变非治疗干员 inactive 行为。当前实现保留了这一例外，也没有全局预验证 scenario、改变真实 checkbox 或无调用字段。

独立小 probe 在 baseline 与最终 draft 各执行 95 次公开调用：94 组配对案例加一项 comparator 诊断，合计 190 次。22 组活跃原始 bool 变为预期整数错误，72 组完整公开输出或已有错误严格保持。案例包含默认、整数/浮点整数/字符串、原始 bool、其它 owner/skill inactive、ghost_count=0 时 ghost_casts 不查询、healing capability、非 integer 参数、真实 checkbox、已有 enemy_weight 拒绝、旧 summon_count 字符串 TypeError 以及显式零窗口/零敌人。caller input、catalog 和 mechanics 均保持不变。

独立加载新 8 测试方法与第 54/57 节相邻契约共 **26 方法全过**，无 failure/error/skip。没有将主审计的 51 方法冒充为独立重跑数量。

对已经完成的主矩阵 JSON 作独立严格全字段比较，未重跑 1,354 个计算：192 个被实际查询且原先接受的原始 bool 变为精确 ValueError；其余 1,162 个完整 public JSON outcome 一致。其中 828 属 active integer 控制，144 属其它 owner inactive，6 属 ghost 查询 gate，184 属真实 checkbox。比较不删除 report、数字、时序、None 或 scope 字段，也不把 bool 与数字等同。

作者最初 comparator 的 374 个失败 receipt/log 已保留。独立从其中 index 62 重新执行一个 baseline/draft 公开输入，确认运行时 `unbound_cast_reference.parameter_rows` 及 `window_reference.parameter_rows` 有十处 tuple，对应已保存 JSON 的 list；Python 直接 equality 为假，而完整严格 JSON 序列化与原保存结果一致。所有 374 个历史失败 index 均属于已保存完整 JSON 保持集。这支持作者的比较器准备问题诊断，不能把那次失败计为通过，也未通过修改生产代码或删除字段消除差异。

两个固定 commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 的 character/skill 原缓存实际重新哈希并匹配。独立复核 25 控件记录、510 个 rank blackboard 与固定原表一致，绑定到实际技能 ID；战术阿米娅映射只用已提交 char_patch exact-selector 历史回执，不声称当前原始 char_patch 文件已重新验证。UI 上限仍是既有输入契约，不推断 native 上限。首次附着、独立事件时钟、叠层、随机性、生命周期、热更新等未知未被补猜。

本审核只针对冻结 HEAD58 的外部最终草稿。Root 必须在 full60 完成归档后集成并进行 fresh 相关/精选验证及后续每五节的全量检查；此处没有声称 Wine、实际 GUI 或原生 Windows 通过。没有改 root tracked、作者 draft 或 58/59 冻结文件。原 `NOTE.md`、`receipt.json`、`source_audit.py` 保持原只读候选审计内容；本轮新增 `final-receipt.json`、`final-baseline-probes.json`、`final-draft-probes.json`、`final-tests.json` 与独立脚本/log。
