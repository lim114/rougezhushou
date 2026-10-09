# 97 实际窗口 smoke：未执行 Source

本包不宣称窗口打开、IO 复现、计算通过或第 97 节完成。作者未执行项目、测试、Wine、helper 或 codec；只在仓库外写 Source 并用 ast.parse 检查语法。Root 必须完成 096、应用已独审 097，并将真实 maintained source map 绑定后再审阅和执行。

runner CLI：`window.py --root <actual repo> --source-guard <actual applied097 JSON> --out <fresh external output>`。guard 必须为 `section=97` 并含全量 `source_sha256`。当前未填 actual guard / receipt / argv / exit，不能执行历史 future baseline 代替。退出 0 只表示本 smoke 自身实际 assertions 完成，不表示原生 Windows 或全量通过；Root 仍应真实打开四张截图并保留主进程/raw/log。

`native_evidence.py` 全字节复制 Root 当前 096 的小型 stdlib helper：6468 B / `f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a`。作者没有导入或调用它。实际 native graph 以限制 globals 的 protocol4 pickle/gzip 前后精确比较，保留码点、bool/int、float bits、dict order 和容器 aliases；metadata JSON 不负责证明 native surrogate pair。输出只含公开 fixture，无私人状态。

全部 MainWindow 为真实构造，账户、本局、settings、DesktopBackend runtime 路径均指向独立临时目录。GameCapture/读屏器实际构造但自动采样关闭、目标 None；没有执行采样、OCR、聊天或游戏操作。sample_received 仅使用明确标注的手动 public delivery 与零图；没有替换计算函数、报告函数或 GUI success。只包装原 AccountCache.observe、原 calculate_damage 与匹配 owned account.tmp 的原 Path.write_text，所有包装必调用原入口。

五个新实际窗口计划：

1. 健康公开 Unicode 保存为同事实控制：lvl2 初值、lvl3 成功保存、lvl4 成功保存；记录实际 run/account 培养开关与真实按钮的完整 damage_result、estimate、default、technical。
2. 真正 account.tmp 非空目录导致原 write_text/open OSError；记录原异常，不 mock 权限。observe 仍接收 lvl3、run 不变、原 account bytes 与 sentinel 不变，两处原消费路径显示保存失败。将作者拥有的 barrier 显式移到 evidence role 后接受 changed lvl4，验证保护门不再 IO；原目标不变、数学与三全文等于真实健康同事实控制。
3. ASCII JSON 载入 lone/separated surrogate，实际 observe/save 精确保留 decoded codepoints，普通中文/emoji/字面 backslash-u 仍保持；计算全文仍与相同有效事实控制相等。
4. native 两码点 high→low pair 经 apply_operator_observation 实际接收；在任何 temp write 前拒绝，原 target 与既有 .tmp sentinel 全字节不变。随后普通 delivery 保留旧 opaque leaf 并到达摘要消费者，避免把 raw surrogate units 投进 Qt 的 observed_text。拒写提示与健康同事实计算对照均保留，之后 changed lvl4 永久拒写。
5. 关闭旧窗口、以 IO 故障保留的健康原 target 建立真正新窗口，读取原 lvl2、save_issue 空、保护空、完整计算三全文等于原 lvl2 健康控制；不解除旧失败对象保护。

每步完整 native、调用方、账户/本局/文件 before-after 原件独立保存，失败也保留已完成前缀。300 秒 watchdog 有真实 124 出口，不会制造无限检验或 PASS。四张 PNG 是 IO 与 pair 场景的培养页/摘要页；Root 必须实际 view 才能把 screenshot inspection 记为完成。

范围：这是当前源中的真实健康与失败功能对照，不含旧 096 产品整树执行 gold；旧异常行为仍需 Root 的相关回归或另行明确 baseline 对照。IO smoke 只认证一个真实写临时文件 OSError，不替代 mkdir/replace/部分写入注入方法和其它 OS 实际验证。这里只测特定公开 Unicode fixture，不声称通用 Python JSON 值无损持久化。
