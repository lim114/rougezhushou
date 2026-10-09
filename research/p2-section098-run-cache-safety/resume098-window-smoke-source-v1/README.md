# 第 98 节真实窗口有界 smoke：未执行 Source

作者只读取源码、写本隔离目录并对 window.py/native_evidence.py 做 AST 与内存 compile；没有执行 code object、导入项目或 helper、运行项目/tests/Wine/Qt/Git。Root 实际结果、实际第 98 节 guard、工具退出码与图片验收仍未生成。不得把 Source 编译 0 当产品 PASS。

`native_evidence.py` 与已审第 97 节 runner helper 精确同字节：6468 B，SHA256 `f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a`。Native pickle 只接收内建类型，保存时拒绝 global/external references；每个 native record gzip、compressed/decoded bytes 与 SHA 都留存。作者未运行这些 codec。

## 绑定及执行边界

Root 完成、验收并保存 97，实际应用获独审的 98 v2 及 app 单行 fields 缺省后，再冻结全体 rouge/tests/scripts 的 .py/.json 为实际 guard。runner 参数 `--root`、`--source-guard`、`--out` 全必需。guard 格式为 `section: 98` 与 `source_sha256: {relative_path: sha256}`，必须与当时实际 source_map 完全相等；RunState 硬绑定 51094 B 的 SHA `ca338423cdce026293d0987365eefac7a16fe3769f6b2dff9d4e0faf1b956363`，并检视实际 app 中 fields 缺省源。先独立审阅 runner 的精确源码/MF，再在 PYTHONDONTWRITEBYTECODE=1 的真实 Wine Python 执行。输出目录必须不存在且位于 repo 外；结束再核对全体 source hash。Source 包无虚构 actual guard，也没有生成准入成功记录。

所有本局、账号和 settings 路径在 MainWindow 构造前指向独立 TemporaryDirectory；DesktopBackend 使用原构造器但目录重定向，所有 folder 的其他本局 sentinel 也核对原 bytes。运行的是真实 MainWindow、真实采样控件（disabled/off/unconnected）、原 calculator、原历史提示和原报告格式器；不替换算例返回或 UI。实际游戏枚举要求为空，不连接/读帧/OCR/聊天；QTimer 不活动，DesktopBackend 不启动、chat目录不存在。调用 actual reset_run 按钮只影响该测试临时本局。

## 代表性闭合范围

同一进程缓存公开数据、使用新真实窗口，计划 20 次真实窗口构造、19 个成功步记录、36 次显式计算按钮进入 original numeric。这些是 Source 计划，实际计数从日志/receipt 获得；任何断言/Qt异常/超时都会失败。

- 健康原缓存打开、训练优先切换、计算和真实关闭重开，原 bytes/opaque 数据不变。
- 六个代表性损坏缓存：maps 外层数组、history 非 list、成员 fields=None、记忆 icon 缺 candidates、匹配完整地图节点 content 缺 title、真实三排图 row=3。损坏拒绝前不浅安装同文件兄弟；窗口显示保护提示，可继续本局观察于内存、选干员并计算，原文件不变且 tmp 不产生。
- 第一个坏缓存通过实际“开始新局”按钮重置，再关闭/重开验证新 ID 及新空本局；账号和另一临时局原件保持。
- 合法旧成员缺 fields 的实际展示、训练账号参考标记、计算和关闭/重开，直接证明 app 新一行的真实消费资格。
- 用真实窗口 apply 正常 int3 原库存生成单一原 raw seed。之后每次窗口启动都复制完全相同 seed：None empty/one 对照，False empty、True one、missing count unknown，int0 explicit empty、int1 explicit one。bool/missing 的完整 state、实际 raw、库存结果和完整两套数学/报告都与对应 None 结果精确比较；int0/1 保留正常明确信息与移除行为。bool 并不抹去 prior int3 的可信同局缓存；新局原 count=None 的 True partial 另证明仍然未知且不虚构完整清单。
- 每个 reports 操作用真正计算按钮；仅针对显式按钮记录完整原 native scenario/result，再使用原 calculator + 原 history notice 对相同 scenario 做完整结果比较。账号与本局训练分开验证实际 level 和界面值；一般/estimate/技术三个原格式器、实际技术/结构化可见切换精确比对，durable state不变。未声称旧版本完整数学配对或全缓存数值 schema。

不装 global profile/trace，不捕捉每个 Qt/layout/JSON 调用。自动计算仍走原函数，仅计数不保存完整 native 副本，避免第 95 节采集过密问题。该 runner 是第 98 节有界验证，不是第四次 full095 UI 重试。

## 证据与收尾

watchdog 300 秒后保留当前真实进度并原退出 124；不能宣称完成。成功每步原子生成 native 记录和 progress；最终 receipt 的 actual PASS 必须有明确结果、真实窗口响应、无 Qt 异常、无 source drift。四张原 PNG 为 healthy-training、protected-cache-summary、manual-reset-summary、bool-inventory-preserved，图像哈希/尺寸被记录。runner 中 `root_visual_inspection_completed=false`，Root 必须实际查看四张，另记完整验收；本包不填“已看图”。Native Windows/game/chat 均未验证，Wine只记兼容检查。Root需保存实际 shell launch/completion、stdout/stderr/raw exit 及该 runner receipt，不把工具0或 Source-only记录当 native Windows通过。
