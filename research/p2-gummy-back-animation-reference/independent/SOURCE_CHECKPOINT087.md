# 087 数据追加独立审查断点

来源准备通过；作者最终产品冻结、保存公有结果及新测试尚未交接。本文件记录准备阶段，不是正式产品或 UI 验证通过声明。

固定 baseline 为 `9ef5a469673502754db3be320a8eece9a7fd18d4`。baseline 原 JSON 1283952B、SHA `28d9be1dd6fe6f91dc5773b1c685ea78fb0bb403d25c4f26d933adcfcbad3f9e` 已 gzip 保存并逐字节还原。原 923 条 record 的字面对象字节与严格 JSON 类型/值 digest 建立索引，供最终冻结稿比较；没有重建旧 cache。

已核对应追加的五个 Back 动画：Attack/Default/Idle/Skill/Start。仅 Attack 与 literal Skill 满足原 builder 的保守资料筛选；duration/event 秒数来自封存的实际官方读取结果，30Hz 与 1e-5-frame 归一化完全沿用旧表示规则。两 eligible preview 分别为 16/24/40 与 13/27/40。Default/Idle/Start 按旧理由保持非 selectable，OnStart 保留。

预期 counts 为 32 operators、64 source_skeletons、928 animations、162 selectable_references、766 unverified_or_transition_references、0 missing_skeletons。原 source_skeletons=64 是声明库存，当前实际具有 record 的 operator/face 组合为 63，恢复此 Back 后为 64，不能改成 65。所有旧记录及新记录 runtime_binding_verified 均应为 false。

只允许保留原 923 条对象及顺序、追加五条当前已知 Back 资料、清除古米当前 missing entry、修改四个计数字段。原 selection_derivation 是历史来源记录，其不存在的 cache 不能重建或改称本轮的新来源；旧 Back 错误及旧 reader/次数/root cause 未知事实仍保存在已封外部来源证据。

资料筛选与选择逻辑是两个边界：literal Skill 没有编号，既有 choices 不接受它；Attack 前缀满足 ordinary，但还需已发布 selectable gate 与显式 reference_id。现 ordinary 条件可在 normal 或 skill 分支使用，不证明 actual normal、native skill 时钟或 UI 选项数量。

本准备阶段应用 API、production helper、formatter、tests、Spine/source runtime parser、network、Qt、Wine 与 tracked 改动全部为 0；只读取固定 git blobs、少量已封 saved 数据/合同，并计算字节 digest 和表示规则字段。没有重新检查全部 source102 材料、下载新资源或重复已有 Front/Back 解析。

下一步等作者最终 freeze，再精核 source-only delta、原 923 byte/type/value 保留、新五条完整字段、source provenance 和 saved 公有输出。任何必要 fresh≤12pairs 或新测试由父协调明确预算后执行；不得自行重跑作者大矩阵或既有来源读取。
