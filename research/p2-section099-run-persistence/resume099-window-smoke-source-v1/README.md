# 99 实际窗口 smoke：未执行 Source

本包只准备 Source；作者没有导入或执行项目、测试、helper、fixture codec、Qt、Wine 或 Git，也没改仓库。已经使用 `compile(source, path, 'exec')` 编译 Source 而不执行模块，确认 nonlocal 的 main 外层绑定存在；不能只用 ast.parse 就声称编译合格。Root 负责最后非作者审阅与真正应用/运行。

CLI：`window.py --root <actual repo> --source-guard <actual applied099 JSON> --out <fresh external output>`。guard 必须 `section=99`、含完整 `source_sha256` map，而且核心 `rouge/run_state.py` 必须 SHA256 `1b6f66e7f864238880c5214f431da042e94c7fd7def8103352439609bbfd35d9`。全 Source 检查发生在项目 import 前；Root 真正完成 96、97、98 并应用 99 前不能运行，也不拿旧 future Source guard 替代。

`native_evidence.py` 是原 97/96 小型标准库 helper 全字节复制：6468 B / `f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a`。本作者没有调用 freeze/write_record 等 codec。Root 实际运行时保留完整 native state、调用方、结果和三篇全文的类型、码点、float bits、字典顺序、容器 aliases；JSON 只是人可读 metadata。QImage 只记录公开零图的尺寸，Path 参数有明确路径描述，二者不送进只接受 exact builtin 的 codec。

全部账户、本局、settings 和真实 DesktopBackend runtime 路径独立临时；保留真正 MainWindow、GameCapture、Reader 的构造，自动采样关闭、计时器停止、capture collecting=False、target=None，桌面后台未启动。没有操作游戏、采样、OCR、发送聊天或替换 GUI 成功结果。run 通过明确标注的公开手工 delivery 进入真实 sample_received、RunState.apply、app 刷新路径；图像是手工零图，不称为游戏截图或 OCR。

计划四个真实窗口、五个步骤记录：

1. 健康同事实窗口：公开固定局 ID，初始 lv1、正常接受 lv3/lv4 保存；实际原计算按钮调用原 calculate_damage，保存完整 damage_result、estimate/default/technical 三文本。健康保存 decoded state 精确等于接受内存。
2. 同初始事实的真实 IO 失败窗口：不同 run.json/run.tmp，非空 run.tmp 目录和公开 sentinel 触发实际原 write_text/open OSError。透传监控确认只有 mkdir 成功和 write_text 失败、replace 没有执行；apply 实际返回 True、save 返回 False。完整接受内存精确等于健康 lv3，再读 lv4 无任何目录/写入/replace 重试，原 run/account bytes 和 sentinel 不变。摘要实际显示保存失败与重启旧盘风险，完整数学和三篇全文与健康对应事实精确相等。
3. 在同失败窗口真实点击开始新局按钮：此前通过原 FrameBuffer.offer 放入明确的合成亮色小图作为队列前提，非真实采样/OCR；确认队列 pending 从 1 到 0、generation 改变、采样 epoch 递增、局 ID 换新、成员/持有/地图/历史清空、待显示观测/图像及预览清理继续，保存失败会话仍不 IO 重试、不回滚旧局，原盘及 sentinel 不变。空总览没有 profile，所以 snapshot 明确标记培养/技能 getter 未调用，不把测试 getter 错误当产品错误；数学只在接着实际接受新局 lv5 成员后进行。随后给真实 sample_received 一个旧 epoch/generation、故意更新的 timestamp 和 lv9 的延迟公开结果，必须未调用 run.apply、未改已接受新局及文件。失败警示仍可见，新事实保留新 ID。
4. 关闭旧窗口，将其实际已接受新局事实仅复制到另一个公开健康 fixture，真正构造独立健康窗口：同 ID、历史、时间、培养等事实让完整数学与三全文可精确对照；不修改失败对象、不向其回放旧局或覆盖其文件。这里只比较相同有效事实，不承认旧版本执行 gold。
5. 最后真正重开 IO 文件夹的新窗口：读到原磁盘较早的固定局 ID/lv1，save_issue 空、读取保护空，原 bytes/sentinel 仍未变、读取本身没有额外 IO。完整数学与原健康 lv1 控制相同。这实际证明警示所述重启边界，不解除旧失败对象保护。

四张 PNG 是真实 IO 失败与手动新局后各自摘要页/计算页。Root 必须实际查看四张图；runner 只留下 `root_visual_inspection_completed=False`，不会声称已看图。窗口真实按钮会调用原数值入口；原格式化函数不被替换，计算前后完整内存/所有自有文件保持。

只有原 RunState.apply/save、原 calculate_damage 和自有目录/临时路径的 Path.mkdir/write_text/replace 被透传观察，每个 wrapper 必调用原方法并返回原值；不安装 profile/trace。Path 参数及 Path 返回值只作路径描述，原调用对象和参数不改变。失败也保存已完成前缀、原异常、Qt hook 与调用原件。300 秒 watchdog 实际退出 124，不创建无界回归。

范围：本 smoke 只检验真正临时文件 open 的一种 OSError，不替代 99 的 mkdir/replace/部分写入/序列化/Unicode/link 单元与相关回归；这些仍由 Root 执行。Root 21994b 的旧实现实际 Linux 复现属于单独原件，不能拿当前 smoke 替换或倒填旧 UI gold。Wine 只是兼容验证，未认证原生 Windows、游戏或聊天；退出 0 不等于全量 PASS 或第 99 节自动完成。全部 public fixture cleanup 只发生在完整 native 文件证据保存后，不清理产品原件或私人状态。
