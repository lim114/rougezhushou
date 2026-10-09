# 第 109 节：原有空供靶消费者的观察源码

这是 Source-only 作者封存包，不是产品改动或测试通过证明。作者只读取公开源码/JSON、计算哈希、解析 AST 和 compile-only 两个 Python 文件，未运行项目、helper、codec、API、测试、Git、Qt 或 Wine。

Root 必须先结束正在处理的第 107/108 节，另取真实完整源码 guard，再决定实际运行。后续源码数量和 guard 哈希保持 null。实际运行前后，整个 `rouge/tests/scripts` 的真实 `.py/.json` 映射必须逐项等于 Root `--guard` 文件；CORE 单独匹配。15 个仍未变的原消费者/数据另行固定。第 108 节可能改变的 run_modifiers/enemy_environment 不列入窄 pins，但始终在完整实际 guard 中检查。历史 pending 标签不改写，也不据其推断现状。

第一阶段 `focused` 只有 30 个真实 calculate_damage 情景，成功时另外调用 format_estimate/format_report，共最多 90 次显式接口、120 个 native 记录。覆盖本体常规、无窗口弹药覆盖、医疗弹药友方回退、机械师手填持续普通攻击、instant 获取门、友方治疗、初动/充能/单酒/部署限时攻速、独立触手与未绑定无人机/友方 SP。没有任何数值 PASS 断言或全面归零预设。

第二阶段 `extended` 是可选的 32 干员/87 技能完整观察清单：两模式各有带 10 秒窗口的默认/空列表/非空范围/0 生命周期，以及不带窗口的默认/空列表，共 1044 情景。其作用是补足范围证据，不是为了计数而必须完成的进度条件。默认每次只取 100 情景，硬上限 160；每次 120 秒独立预算，Root 可根据第一阶段实际问题选择是否运行和所需区段。

Root 调用入口为 `probe_empty_target109.py --root <实际仓库> --guard <Root 新实际 guard> --out <新仓库外目录> --stage focused`。可选的扩展区段通过 `--stage extended --start <零基索引> --limit <1..160>` 指定。作者从未执行该入口；这些是后续 Root 审阅/运行参数，不代表已经运行。

每次接口调用完整保存 before/after/result/error，保留类型、浮点位、字典顺序、容器别名；完整 formatter 文本也在 native 中。只有 calculate_damage 的真实结果可以进入 formatter，异常则显式阻断，绝不替换假输出。每个 native 文件与 append-only index 元数据立即 fsync；每完成一个 case 再原子保存小 checkpoint 和 next_case_index。完整 guard 只在热循环外前后各读取一次。checkpoint 不表示 after guard 或产品通过；`observations.json` 的实际完成、错误和前后 guard 必须由 Root 执行产生。超时保留 raw124 和原文件，后续只使用新输出目录，不覆盖或补填旧失败。

`target_windows:[]` 是该本体或独立单位的供靶声明，不是全场无敌人。独立单位不继承 owner 的供靶范围；友方治疗/技力、诱饵、无人机、范围场、投递/路径、碰撞等既有未核验来源仍保留各自范围与未知。非空 continuous 范围不按比例换算伤害，也不新增原生获取、释放、命中或技能结束时钟。False/None/0/空字符串不等同有效空列表；缺省也不同于空列表。

所有当前结果/实际返回/通过计数/未来 commit 保持未填写。native_evidence.py 与已封存第 108 节的 f040 helper 完全同字节，作者没有导入、执行或解码它。原 107 错误证据、原 108 包和独立事实报告不被覆盖。
