# 第245节全量失败修复候选（只在 work）

根代理在260功能完成后串行应用。此目录未修改生产源码、golden、来源读数或历史失败回执；维护不增加功能节数。

## 可直接应用的两项修复

1. `tests/test_base_settlement_planning.py` 的旧20个查询断言改为第236节已发布的21，并显式要求 `relic-panels` 实际存在。没有去掉数量断言或减少运行的八个公开情景。既有 `tests/test_offline_tools_view.py` 已使用21。
2. 原地图构建器逐位比较重算 OpenCV 浮点与封存 fit，当前环境产生极小差异而失败。新增 `scripts/map_fit_replay.py` 明示允许范围，只有 `/matrix/*`、`/checks/*/projected_pixel/*`、`/checks/*/error_px` 可用有限浮点 policy。其余类型、键、长度、原 observed pixels、单元格、身份和 accepted 布尔严格相同。重算与封存两份各自重新用原 `max(error_px)<=4` 判定；即使差值在数值 policy 内，只要资格跨4px也拒绝。

数值 policy 为 `float32 epsilon * max(1, abs(current), abs(frozen))`。OpenCV 上游源码显示 findHomography 将输入转为 CV_32F，再执行 method0 kernel/迭代 refinement。这个政策以已用输入类型为明确尺度，是工程重放政策，**不是** OpenCV 的已证误差上界、图像测量精度、4px 门调整或原生准确性保证。来源文件为 `opencv-fundam-4x.cpp`，URL https://raw.githubusercontent.com/opencv/opencv/4.x/modules/calib3d/src/fundam.cpp ，SHA256 `4fd0cf0abec358bc3b40761e0f2ebfa0ca8b9fad0efa907e3ab9b2d4ec942ae0`，对应输入转换约391行及LM refinement约433行。4.x快照用于算法依据，不宣称逐字对应已安装4.14.0二进制。

重算只作独立复验。输出矩阵/投影/误差用原 hash-sealed initial fit；逆矩阵复验后用原封存 canonical inverse，绝不更新 golden 为本机结果。canonical 为已在后续原件收据封存的 `research/p3-direct-ground-current/prior-regular-projections.json`，SHA256 `b36710dbc381de0ded802d6edc4ef4eafe192432818180bf608a5fded3cf843c`，也精确等于原 ground build 的 output SHA。源文件 SHA 检查、独立读数、接受/拒绝及4px门均原样保留。

Linux最大绝对漂移为 `6.193262436227087e-08`，最大单叶占允许数值预算 `0.3778206112328917`；Wine最大占比 `0.3778207669965923`。逐叶原/今值、允许差值、两份独立资格/最大error及保护来源哈希在 `fit-replay-candidate-{linux,wine}.json`。二者canonical输出和原direct收据精确不变，242合法扩展的 source-bound entries 与运行数据严格相等。未把整个旧baseline误当作全部当前覆盖范围。

`candidate/tests/test_map_fit_replay.py` 包含超过预算、原件像素/身份/单元格/类型/形状改变、非有限计算和预算内跨4px资格的拒绝反例。49个必要相关检查在Linux/Wine各49 PASS，正常进程exit0，日志 `candidate-linux.log` 与 `candidate-wine-bash.log`。这些检查包含原地图/Qt流程和原source guard；未替换完整全量范围。

## Qt139：证据与后续验收

245历史Linux receipt写完后进程exit139，但没有栈。最小两个Qt用例原样跑exit1（只失败旧数量），全选择器仅导入exit0；原245 selector中206个Qt命名类用例跑exit1，只有旧数量失败，没有139。不可声称已重现或确定Qt是根因。

同样206用例结束有157个有效top-level QWidget wrapper、全局线程池0。显式正常销毁探针确认 QApplication.instance()为None、157个wrapper全部失效，仍正常exit1并保留原失败（`qt-runtime-explicit-shutdown.log`）。`candidate/scripts/qt_verification_cleanup.py` 为可选真实清理候选，等线程完成后关闭窗口、处理DeferredDelete、调用PySide实际shutdown并严格检查已销毁；无os._exit，也不吞异常。

该可选helper另在Linux/Wine真实运行确认：活动线程池任务完成、排队result先交付、3个实际QWidget与QApplication全部销毁，正常exit0，重复无app调用也正常返回；见 `qt-cleanup-candidate{,-wine}.log`。这仅证明清理动作真实有效，不证明245退出139的因果。

260完整检查必须保持原历史CORE + NEW + 当前云端selector并集和完整window范围。建议进程启动加 `PYTHONFAULTHANDLER=1`，保存真实外层exit code；先完整运行再判断139是否持续。若应用cleanup候选，应在全部测试之后、source-after/receipt之前调用并写入cleanup诊断字段；它未被证明解决245原因，必须靠完整运行验收。若仍139，保留faulthandler栈并继续定位相关native库/退出析构，不得用通过的Python断言冒充正常进程退出。

初次调用系统python缺PySide6、Wine脚本无execute权限直接调用失败也保存在对应work日志。实际验证使用 `.venv/bin/python` 与 `bash scripts/wine_python.sh`，没有改权限或环境依赖。

## 文件与应用

`repair-map-query.patch` 是可直接审阅的生产路径补丁，只含两个构建器、浮点复验helper、两份旧断言修正与新增反例测试；Qt可选候选不混入已证修复。先检查生产相关文件未被其他维护改动，再由根代理应用；需要验证时复用 `run_candidate_tests.py`、`audit_fit_replay.py` 的真实依赖和公开资产。

复现：

```
QT_QPA_PLATFORM=offscreen .venv/bin/python work/full245-repair-audit/run_candidate_tests.py
QT_QPA_PLATFORM=offscreen bash scripts/wine_python.sh work/full245-repair-audit/run_candidate_tests.py
.venv/bin/python work/full245-repair-audit/audit_fit_replay.py
bash scripts/wine_python.sh work/full245-repair-audit/audit_fit_replay.py
```
