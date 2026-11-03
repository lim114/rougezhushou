# 087 官方读取器与古米 Back 来源断点

状态：官方 fixed 3.8 来源/许可/自包含 core/factory/parent runner 静态合同通过；保存的两次 reader 结果独立复核通过。本代理没有执行 bundle、compile、reader、应用 API、production helper、formatter、tests、Qt、Wine 或 tracked 改动。

官方 runtime 固定到 `8b4844bd4b193ba9e54487ed397a777993cbad56`。两实际 skeleton 的 header 为 `3.8.99`，来源资源固定到 `d0b5af0b004b044d322397ce5ae79632b6d9fcdd`。没有重建不存在的旧缓存或批抓 64 skeleton；父只重新取得两份真实资源。本子目录只下载 12 份必要官方文件，13 个固定 raw GET 尝试中唯一失败是错误猜测 AttachmentLoader 根路径的 404；另 API metadata 403 和 acquisition patch hunk 格式错误各一次，都是准备问题，0 parser。失败诊断和当时原脚本/日志保留。

父 source-operation 恰两次完整 reader，Front/Back 各一次，均返回，零新 reader 异常。Front 47 bones/49 slots/9 animations，与已有 9 条原始 duration/version/event name+seconds/resource 身份精确一致；保存 control 先于 Back 开始。Back 34 bones/28 slots/5 animations，Attack/Default/Idle/Skill/Start，没有从 Front 补 Die 或 Skill2。独立复核同时核当前资源文件 SHA/Git blob 和保存 before/after byte invariance。

Back Attack 与 literal Skill 是两个源资料候选；它们不是两个已验证 UI 技能选项。现 choices 的编号正则不接受 literal Skill，Attack prefix 则是 ordinary 条件且还需已发布 selectable gate/显式选择。没有调用 choices/descriptor 或实际 UI。Native normal/skill/skin 绑定、真实时钟、EOF、atlas/texture/视觉几何与渲染有效性都未验证。旧 Back 错误 reader 身份、实际历史总尝试次数和根因仍未知，仅可见失败下界 1。

许可原全文保留（root LICENSE 2019-05-01，reader 头 2020-01-01）；这是自定义 Spine Runtimes License，不是 MIT。本轮没有产品集成或用户许可资格推断。

续作：由 root 决定是否将真实 Back 资料纳入现有离线来源流程。先保留现有 923 动画/160 selectable/unknown binding 合同，不把源读取成功变成游戏机制证明。已经通过的两 reader、Front control 和本静态/saved 审查均不得重复运行；后续只能在新的外部目录审查 root 冻结的具体改动。
