第 73 节只补齐梅 MAR-X 的空中目标条件资料。固定开发基线为已提交的 `552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9`，未读取滚动未提交改动作为实现基线，未修改 tracked 文件，未运行 GUI、Wine 或游戏。

原始数据固定于 ArknightsGameData `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。character_table 重新核验 SHA256；battle_equip_table 与 uniequip_table 从固定 GitHub raw URL 经原代理与默认 TLS 新下载，字节数及 SHA256 与既有固定资料一致。`source-receipt.json` 保存原始角色技能/天赋、精确所属绑定、模块 metadata 与三阶完整 parts/attributes。不是从规范资料中抽一个数值就宣称来源成立。

`uniequip_table.charEquip.char_133_mm` 与 `equipDict.uniequip_002_mm.charId` 双向绑定梅与「新手侦探礼包」MAR-X；模块门槛为精二 40 级。三阶 `battle_equip_table.uniequip_002_mm.phases[0..2].parts[0]` 均为非 token 的 TRAIT，无 map/game 限定；对应 resKey 为 `mm_equip_1_{1,2,3}_p1`。唯一候选均为精二 40 级、requiredPotentialRank 0，原描述是“攻击空中单位时攻击力提升至110%”，黑板 `atk_scale=1.1`。规范 catalog 的三阶完整 parts 与全部属性逐一等于原件，已有具名天赋值及技能资格映射也已核对。

这条记录证明条件及原参数，不能单独证明实际模组附着、与技能或其它加成的组合层、实际目标飞行条件及客户端当前热更新。保留的 199 个 native 文本/JSON/研究导出文件经重新哈希并针对梅角色、技能、模组 resKey 与 module ID 检索，均没有精确绑定。查询范围只是现存缓存，不是完整安装包。其他干员的技能 atk_scale 与卡达的单元特性不能代替本 TRAIT 的组合层证据。公共 GitHub 搜索没有补齐这条特性的精确可信机制资料；PRTS 不在当前网络允许域名内，未重试此前已诊断的受限路线。

实现只在当前选中梅 MAR-X、培养满足精二 40 级门槛、模块等级 1–3 且来自同一 catalog 的已选 TRAIT part 时新增 `mei_airborne_module_reference` 和一块公开报告。候选仍按其精英、等级、潜能条件筛选；无模组、未满足门槛或其它干员保持完整旧结果。参考保存具体原选择器、门槛、当前阶数、原描述、1.1 参数，并将目标空中条件和该特性实际伤害保留为 None。所有附着/组合层/实机标记为 False，明确未计入现有数值。没有新增 checkbox，没有解析或默认推断地面/空中，没有伤害乘数、事件、快照、获取、结束或阻回时钟。

报告用人类可读文字说明“110%参数未计入当前伤害数值”、“本次未确认目标是否为空中单位”与“组合层尚未核验”。沿用最终公共输出已有的 complete_definition，不改变 complete 或 estimate.complete 的范围。S1 既有实际总伤、相位、回转的 None 继续保持；S2 当前数字仍是既有已覆盖模型，不包装为该条件特性完整结果。

8 个必要新测试与 40 个相关旧方法共 48 个方法通过。新测试覆盖三阶、实际门槛、技能与潜能资格、逐击旧参考值、来源未知、报告明确未套倍率、其它所有者/外来 parts、空窗口/空供靶边界和公共培养旧错误。最初测试误用了不存在的 verified_phase 字段、误将 S1 条件小计当作已确认 actual total，并沿用 engine 内部而非最终公共 complete_definition；另一次用了不存在的旧测试模块名。这些测试假设按基线事实修正，错误日志保留，没有修改生产公式来迎合测试。

两个独立 Python 进程对固定 baseline/draft 执行 1,830 对完整普通 public calculate_damage 调用，共 3,660 次。1,524 个资格满足场景仅新增参考字段和报告 section；246 个成功场景完整结果保持；60 个旧错误类型/原文及先后保持。对资格满足的结果仅移除新 field/section 后，其余完整 JSON 与 baseline 严格相等，包含所有数字、None、component、timing stream、scope、complete、培养/SP、阶段/周期、旧来源与其它报告。输入及 catalog 缓存也保持。保存 gzip 全结果可独立复比，不只是计数或摘要。

外部 draft 有 706 个旧源码/数据/测试文件，其中 704 个原字节保持；只有 operator_engine 的参考接入和 reporting 的新资料块改变，另外新增专门 helper 与 8 方法测试。`draft-freeze.json` 固定 4 个最终文件及 patch SHA256。最终独立审查由 review_shu60 复用线程执行；状态与路径见 handoff.json。

最终独立审查通过，无 blocker。审阅者重新核原三文件哈希、所有者与三阶原完整 parts/attributes，并将 706 个 baseline 文件与提交的真实 git blobs 比较，核验 704 个旧 draft 文件原字节保持及 patch 恰好重建 4 文件。独立新鲜 80 对/160 次 public 调用结果为 50 个仅资料变化、20 个成功全输出保持、10 个旧错误保持；8 个新方法独立通过。保存的 1,830 对完整输出严格复比，1,524/246/60 计数吻合，没有重算原 3,660 次。独立证据全部列入可归档 public manifest。

仍须完成的实际机制是空中目标条件获取、当前客户端模组附着和与技能/其它加成的组合层。取得对应精确脚本/原生绑定或可独立复核的实际机制证据后再恢复数值实现，不能凭这个参数参考宣布 P2 条件模组已完整完成。
