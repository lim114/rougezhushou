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

## D05—D07：悬停与页脚补读（已按用户决定落实）

本轮核对基线4dca7f553；没有实际触发率统计。用户已分别同意：D05删除两处缺属性兜底；D06保留这一处任务出口；D07删除补读静默兜底。已按原范围落实，不授权其它防御。

| 编号 | 位置与触发条件 | 当前作用 | 建议、影响与替代 |
| --- | --- | --- | --- |
| D05 | player_game_hover.GameHover.tick / accept 的两处 getattr(companion,'hidden_windows',None)；传入对象缺少 hidden_windows 属性 | 默认当作未被用户收起，继续悬停流程 | 建议直接访问。CompactAssistant.__init__ 在创建 GameHover 之前已设 hidden_windows=None；正常收起状态判断保留。构造契约破坏则暴露错误；替代为明确保留两处缺属性兜底。 |
| D06 | GameHover.tick 内 work 的 except Exception；采帧、识别或匹配抛出异常 | 发送失败结果，经 accept 清除 busy，允许后续悬停 | 建议保留这一处后台任务出口；删除后后台异常可能使 busy 一直为 True。D01只授权另6处，不能扩展到此处。 |
| D07 | recipient_recognition.reconfirm_owned_popup_footer 的 engine 调用捕获任意 Exception | 弱页脚补读抛错时静默沿用原文字 | 建议移除捕获，首次失败走既有采样错误上报；代价是本次整帧读取失败。替代为明确保留原文字回退。分数、页面归属和坐标判定不属于本次删除建议。 |

### 同批核对：不是重复就直接删除

app.sample_now 在连接前后都调用 set_collecting(True)，但 connect_game 会依据自动采样开关再次设置采集状态。因此连接后的调用负责手动采样时重新启用采集，本轮不删。GameHover 在读取后复核新鲜画面、同局、窗口及鼠标位置，是异步期间实际可变状态的判定，不是对同一不变输入重复判空。

验证：27项定向检查通过，覆盖悬停异常结束后再次悬停、隐藏时拒绝在途结果、正常卡片来源入口、正常页脚补读与歧义判定、补读异常不修改原文字并上报。既有私样本只在本机读取，不复制到回执。原测试窗口已正常关闭并更新启动，可见且响应。首次补丁脚本因换行匹配失败未写入，首次代码检查发现属性替换缺空格，均已修正；原失败日志保留本机。

## D08—D10：快捷键读取、保存和系统调用（已确认）

| 编号 | 位置、触发条件与原作用 | 用户决定与实际处理 | 影响及替代 |
| --- | --- | --- | --- |
| D08 | player_hotkey.load_preferences：文件损坏、无权限、格式错误时默认启用Ctrl+Alt+Space；shortcut非文字可导致AttributeError | 用户同意异常设置不自动启用，并在文件入口检查shortcut类型。首次运行仍启用默认快捷键，异常已有文件不改写，需用户明确应用 | 异常时少一个自动恢复入口，保留工具条；未选择“仍默认启用”。 |
| D09 | save_preferences的mkdir失败上报、QSaveFile.open/write/commit检查，以及apply_hotkey的OSError提示 | 用户同意全部保留，无新增重试。保存函数原样，界面仍告知本次可用但未保存 | 防止保存失败却误报持久化成功；替代为移除这些提示/原子保存失败处理，用户未选择。 |
| D10 | GlobalHotkey.configure/release：注销失败则拒绝切换/关闭，撤销刚注册的新键；编号超过0xBFFF拒绝注册 | 用户同意保留上述系统调用保护，原行为不变 | 注销失败仍需重新打开助手；撤销新注册本身失败的恢复不在本轮内，无实际发生率。替代为删除保护，用户未选择。 |

来源：微软[RegisterHotKey](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey)规定应用编号范围为0x0000—0xBFFF；[UnregisterHotKey](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unregisterhotkey)规定返回0表示失败。查阅日期2026-11-04。本轮保留既有Win32实现，没有引入第三方替换框架。

同批前两条整改：apply_hotkey只调用configure解析一次，复用成功后的标准名称；删除只做一次坐标转换转发的_drag_dock方法，将表达式并回dragged信号连接处，维护验收脚本改走该信号。正常输入ValueError仍在界面入口提示；复用的_move_dock、Qt生命周期回调与页面入口没有机械地按“调用次数少”删除。

24项定向通过；原工具条4个失败在改动前源码上复现，补齐模拟主窗口的map_overlay_reference/session_recorder后通过。测试使用模拟注册接口，未做原生快捷键交互验收或游戏操作。加载已保存设置和配置入口仍各有自身校验，本轮仅关闭应用按钮的重复解析，不声称整个启动链已完成单次解析整改。

## D11：内嵌笔记初始化的缺控件兜底（已确认并落实）

位置：InlineNotesPanel.refresh 的 hasattr(self,'save_state')。旧构造函数在compact_controls创建保存状态、选项区域等控件之前就设置inline_ready=True；触发早期刷新时，末尾跳过保存状态刷新，但fit_content还可能先访问不存在的options_scroll。该兜底不能保证整个刷新安全。

用户明确同意：将inline_ready=True放到全部控件构建完成之后，删除该hasattr；保留原有尚未就绪就返回，构建完成后首次计算布局。替代为保持原顺序和兜底，用户未选择。没有新增异常捕获或恢复重试。

构造期间刷新测试在修改前复现options_scroll不存在，修改后通过。最终41项定向通过（笔记与控件31项、目录与选择器10项），首次前两条整改的28项通过也保留。未改NoteStore或NoteLibrary的文件写入、锁、冲突复核、链接和异常文件处理；这些存储防御仍属待逐项审查，不能从D11推导授权。

本轮前两条：目录显示直接复用读取结果中的key；select_context的目标key只在本函数入口计算一次，不在候选循环重复计算；删除产品未调用、只有测试使用的catalogue列表包装；将单次_tick转发并回定时器连接。资料归属、草稿阻止切换、搜索及阅读保留仍按原行为。
