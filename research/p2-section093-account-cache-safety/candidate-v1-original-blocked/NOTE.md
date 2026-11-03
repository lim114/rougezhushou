# 第93节账户观察缓存候选（尚未执行）

本包只准备外部候选与测试草稿。没有导入或执行项目、候选 helper、formatter、测试、Qt 或 Wine，没有读取私态或修改 tracked 文件；不计第93节完成。原 source 包22例仍是 STATIC 预测。

候选基底是 root-integration-plan092.json 指定的第92节 prospective `rouge/app.py`，SHA256 `32818adf259dbb124ae86178e0ef82dcb1a316d0f7bf373e5c4b99aa5d25f9f6`。第92节真实提交前不能称为其 commit 上的验证；root 需核对实际 app bytes 后运输。`rouge/reporting.py` 不在本候选中。app 保留 CRLF，只改初始化、账户 state 入口、账户观察合并入口、账户 sample summary 与训练状态显示；calculate、培养参数、等级/rank 显示逻辑、真实 RunState、浏览行为及92窗口条件逻辑保留原 AST。

`AccountCache` 只依赖标准库；规则由 app 已有合并档案及已实现干员集合注入。加载先筛全表，保留 raw map，未知 catalog id 保持 opaque。可消费记录要求 key/id 一致、现有必需 mapping 安全、显式时间能被本运行平台 `localtime/strftime` 转换、实际 GUI/计算消费的培养与技能叶安全。absent container/time 保持原缺省；信赖 bool、falsy module identity/ignored stage、低于模组 unlock 的合法 identity/stage、无效但不起作用的技能偏好、未知额外字段和来源值不统一规范化。

formatter metadata 按实际消费检查：invalid_fields 必须能建 set；invalid_skill_ranks 必须可迭代，安全的 nested 值保留；missing_fields 必须可迭代且每个 entry 能执行原字符串操作。锁定的技能等级只要求其未被屏蔽的 formatter 消费安全；解锁技能依现有 UI index 和计算 type/range/unlock 守卫检查。未实现计算档案不引入仅已实现 damage API 才施加的精英专精限制。

账户 `scope=run` 整记录隔离。其余账户 raw metadata 不改；safe view 删除已知 recruitment/advanced/char-buff/run-confirmed 的本局操作 metadata，防止账号数据经真实 member merge 冒充本局来源。原真实 RunState 合并和 sample summary 路径保持。训练状态在总览和正常状态赋值后追加同一 notice；单条坏账号参考与全局原文件保存保护分开，真实本局成员继续显示已确认培养。

正常好记录仍按原 timestamp `<` 拒绝、更晚或相等接受、fields union、rank string-key、sources/time map merge、changed decision 保存。坏旧记录不参与 union；新的合法 observation 只能恢复内存，清除对应隔离 issue，原文件永久保护保持。bad original 的普通 save 在 mkdir、tmp write、replace 之前返回。FileNotFoundError 需配实际 lstat 不存在才算 missing；dangling symlink 或不确定 OSError 保持原路径。没有 repair、migration 或新的用户流程。

新增单个纯 helper 验证模块及 selected registry entry 是为了长期覆盖全表预筛、消费边界、正常 merge 和受保护文件无保存副作用。测试草稿尚未运行；真实 MainWindow/Wine、RunState precedence/snapshot、原public API before/after输出及timing/relic兼容验收仍由 root 执行。根代理完成独审、真实运输、测试、实际窗口和报告后才能归档第93节。
