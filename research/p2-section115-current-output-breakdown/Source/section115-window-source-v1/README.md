本包只准备第115节的新分项表实际窗口观察源码；没有执行项目、Qt、Wine、测试、native helper/codec 或 Git，没有修改仓库文件。Root 必须先通读并校验 SOURCE_MANIFEST.json 全部叶文件，然后在第115节功能已经实际应用的真实完整源码与 CORE guard 上执行。未来真实 guard、源文件数量和运行结果均为空。

一个真实 MainWindow，共四个快照：术师阿米娅 S1（E1/L1/R7）和医疗阿米娅 S2（E2/L1/R10），分别用真实观察窗口控件设置2秒和10秒。账号、本局均为本包显式公共 JSON fixture，信赖0、潜能1、无模组、无藏品、手动敌防法抗0、实际逐帧控件、持续攻击声明、手动 windup_frames/recovery_frames=0 参考。只读取选定技能等级，没有声称额外已读技能。没有 base_attack GUI 控件，因此不伪装 API 的1000攻击算例，也不使用 game/OCR/chat/private state。

实际 calculate_damage 原函数包裹只记录调用并核对完整 caller 与本局/账号/所有临时文件字节不变。新伤害、潜在治疗、独立回复分组的每个 count/per_hit/total/actual_total 都逐项与实际返回 components 原字段做原生类型和 float-bit 比较，不重新乘算总量，不把 None 变成数值。医阿米娅 S2 的整体伤害、整体治疗、实际结束时钟与独立回复实际总量保留未知。四个快照记录 complete result、caller、所有三份完整文本及 state/disk 图；跨2/10秒只核对相同 caller 除窗口和相同 state/disk，不把有意不同的窗口输出错当全施放或周期承诺。

三个真正 formatter 调用（estimate/default/technical）作为一个只读调用组比较整个 result + state/disk 原生图；普通输出与 estimate 相同，实际普通界面与普通全文相同（仅 Qt NBSP 正规化）。再实际切技术资料 checkbox，核对完整技术文本，恢复普通文本，并核对 result 与 state/disk 都未改变。本包不声称每个 formatter 独立纯度、原件 GUI Gold、游戏公式准确性或原生 Windows 验证。

保存两张真正 window.grab PNG：术师10秒的新伤害分项完整 metrics 区块；医阿米娅10秒的新独立回复完整 metrics 区块（含 actual_total 未知行）。以当前结构化 block 的 title/最后一行 label 取实际文档锚点，记录从标题到最后 metric 的每行两端 cursorRect 并断言都在可见 viewport 内，实际截图后 hash。Root 必须另行 view_image 实际两图；潜在治疗等其他区块有完整文本与 native 数据，不声称在这两图可见。

真实关闭一次后直接重新加载 RunState 和 AccountCache；核对原始合法加载图及临时文件字节。不是第二次 MainWindow 启动，JSON 不证明 live alias。450秒 watchdog、每个快照 fsync checkpoint、最终 receipt 原生文件 hash 与完整源码+CORE 前后守卫。CLI 必需 --root、--guard、--out（全新仓库外目录）、--source-count（Root 实际 guard 数量）。Root 用现有 Wine 包装器及 CJK 字体环境，不能再叠加 Xvfb。

SOURCE_MANIFEST.json 已封存。本包发生问题时保留原件，写 fresh 修正版，不覆盖已封存源码或原运行记录。仅 Root 实际执行、完整回执+原生复读+图像审查后才可给此窗口限定范围的通过结论；它本身不完成第115节全量或网上算例。
