# 既有低概率防御逐项确认

依据用户最新要求：既有低概率防御也先取得同意；不得以“必要”自行豁免。以下按潜在低概率项送审，没有实际发生频率统计。未决项暂不改动，不计整改通过；正常的缺失输入、未知状态和用户输入校验不自动归为低概率防御。

## 本轮已确认决定

| 编号 | 现有位置 | 触发与作用 | 建议及取舍 | 状态 |
| --- | --- | --- | --- | --- |
| D01 | offline_tools_view._QueryWorker.run；route_constraints_view、route_resident_review_view、route_resource_ledger_view、route_scenarios_view、route_continuation_view 的 _Worker.run（共6处） | 计算发生未预期异常时也发送结束信号和错误文字，使界面退出运行状态；同一捕获还处理正常输入错误 | 保留任务出口的这6处统一回传，界面内的重复捕获继续收窄。删除未预期异常捕获后，线程异常可能不回传，按钮保持运行态。 | 已同意保留，代码不变 |
| D02 | route_scenarios_view._finished；offline_tools_view._finished（共2处） | 已有内部结果在渲染或序列化时失败，改成错误提示；前者保留旧结果，后者清空结果 | 建议删除这两层兜底，让内部结果格式/渲染缺陷显露；发生此类错误时不再提供该处定制提示。也可决定保留。 | 已同意删除，已移除 |

用户已明确回复：D01保留6处任务出口，D02删除两层显示兜底。决定只覆盖表中8处，不授权全程序的其它防御代码。

## D03：编辑入口中剩余的未预期异常兜底（已批准收窄）

以下16处原先把所有Exception都转换成输入提示。正常JSON缺字段、类型错误、空选择等保留现有处理；建议删除对其它内部异常的兜底，按各函数实际读取字段收窄异常类型。不增加检查或恢复策略。代价是内部代码缺陷不再只显示“未设置/未运行”，会交给应用原有异常输出。

- route_constraints_view：_run。
- route_resident_review_view：_run。
- route_continuation_view：_set_progress、_set_current_after、_import_graph、_run。
- route_resource_ledger_view：_set_activation、_set_after_battle、_set_terminal、_run。
- route_scenarios_view：_set_scenario_ap、_set_snapshot_uses、_run。
- offline_tools_view：_import_scenario、_import_graph、_fill_node。

用户已明确批准收窄这16处，已按各入口正常输入错误类型落实。该范围与D01任务出口不同，D01仍保留。

## D04：同帧识别失败后重试一次（已决定删除）

原代码 `app.py: MainWindow.sample_now.work` 对 reader.read 的任意异常等待0.25秒后重试同一已捕获帧一次；第二次失败由采样任务出口上报。本轮没有统计其真实触发率，不声称它能提高多少成功率。建议保留这一次有界重试，供已离开的短暂页面遇到临时识别错误时使用；代价是程序性错误也会再执行一次，失败处理增加等待和一次识别开销。替代是删除重试，首次失败直接上报；缓存和其它页面处理不变。

用户明确选择“删除重试，首次失败直接上报”。已删除重试循环和0.25秒等待；保留现有采样错误上报，成功记录的recognition_attempts固定为1。一次任务只识别一次，后续任务仍按原调度运行。并未修改缓存、页面优先级、地图新鲜度或其它线程出口。

## 已有明确同意，不重复征求

叠加设置的原子保存、mkdir/open统一失败出口、write/commit失败处理，以及损坏设置不覆盖/不默认开启，已由用户在第473节明确同意，见[原决定](2026-11-03-overlay-video-controls.md)。本轮只登记授权，不改代码，不将授权扩展到其它配置文件。

## 本轮可独立继续

继续处理普通编辑输入的重复解析、初始化顺序及重复方法；用户可编辑的不完整JSON属于正常输入路径。待决定的防御与其余未审代码继续列在未完成事项中。
