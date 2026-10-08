# 第95节后全量检验的只读迁移计划

这是计划与来源证明，不是新runner或已通过检验。只读基线为第91节 `59961ec3d633ac91b01014fb06b357d45e5979f7`，原full090 runner/回执与外置版本原件不修改、不复制。没有运行项目、helper、formatter、Qt、Wine、测试或网络。第92节候选来源已归档，但其正式作者/独审/根端结果应在完成后另绑定；第93缓存、第94回调及第95最终源码尚未确定。

## 必须迁移的真实旧断言

原实际full090脚本为仓库 `verification/full-090/wine-ui-runner.py`，SHA `9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9`，729181B；外置 `.continuation/ui-090-final-gate-revision/wine-ui-smoke-090-final-gate-revision.py` 与之字节相同。`.continuation/ui-090-final/wine-ui-smoke-090-final.py` SHA `bb35222b37dbbdb4416f415a011f3a0b678c5285729ac0bccb76ec8ba336983a` 是此前730/126绑定版本，其scope-plan仍为当时 pending，不应当作今天的运行PASS。

原full090的3010行已经按所请求且已核对的当前rank取 `sp_type`，3011行还只要求Attack可见。第91节后必须变为Attack或Natural可见；无需重写3010 rank来源。旧section88的8个状态中，mechanist S1两行可见性不变；Amiya E2 S1、Chen3 S3、Amiya E0 S1各两行共6行，由旧隐藏变成当前可见。原数据IDs含hidden是历史名字，应保留来源ID并标明“可见性资格已迁移”，不能把它们当今天隐藏控件证据。

当前 `scripts/verify_damage_ui.py:39` 已在91使用 `window.skill_rank_value()-1` 与Attack|Natural，SHA `0b0dcbcade07f0ff11b2bdcba7c7598a696ff4ece3418bc296312ce97c2a2d54`。这是当前脚本来源资格；本任务未运行它。单断言完整源字节可逆证明见 `visibility-single-predicate-inverse-proof.json`，仅证明必要的静态预览，不冒称最终95完整逆变换。

## 91说明与92窗口行对结果比较的影响

91深海色 S1 改的是基础回复notes的名义/窗口范围、未计倍率/持续覆盖资格，以及生命回复块的含倍率条件说明。原同一组4200/1400应保留但不能与旧全字节note相等；当参考时长或数量为0使原note重复时，文字inverse必须遵从原有ordered去重。数值、字段、直接HPS与时序没有因此获得放宽。原section63的无玫瑰每只固定速度/合计、培养和数量上界可继续作为当前head断言；旧text不应宣称unchanged。

92计划只在**已有合资格观察块**中增有效长度行：伤害块原正窗口已有length，0且non-None时新保留；治疗块原来没有length，现在non-None时含正值/0都新增。AVG的原positive guard保留。native/JSON旧新对照只能按section ID和metric key移除这两类已证新增行，再比较其它完整结果；不得删除所有window字段或统一把0当None。length采用 `estimate.skill.window_seconds` 的已计窗口，例如输入60、名义技能30可能显示30；不能把请求窗口通用于所有技能/延迟/未知来源。没有该观察块、未知长度或未定位来源时不补确定行/总量。default与technical文本分别来自相应结果，只逆掉实际新增length行，不能假设两种文本相同。

原full090 `projection090` (1014..1020；3015调用) **不含report和estimate.notes**，包含根数字/组件/时序/参考及estimate的training/base_stats/skill；它的旧数值golden不应因以上文字变化被泛化放宽。3021..3028要求当前同次estimate/default、实际UI default/technical、rawnative/输入保持，不是与旧text相等，应保留。1986/2103/2336/2385/3033的整份JSON比较是同一个当前head的inactive成对结果，应保留精确比较，不能全面丢弃notes/新行。

保存089的5条记录只有RunState观察、状态及来源native；其10条期望只有培养/标签/crew/roster，不含damage result/report/text。3083..3092赋临时state、切培养、选mechanist并update_operator会使用今日app进行自动计算/呈现。因此这些状态原字节应保持，培养consumer断言重新以93/94完成后的实际source核资格。当前 `render_damage` 仅format已有result，`format_estimate`有report就delegate，均不重build_report：仅用新formatter处理旧计算结果，不能为旧对象补91note或92window行。第95节真正需要当前head计算，不能将旧保存native/文本冒称今日输出全同。

## 92 callbacks与全量调用账本

原40秒spin初始化和原checkbox创建在新增connect前；92候选未增加setter或重置默认值。connect本身不是显式计算请求。启动总API不能据此预定0，应保留真正constructor instrumentation。

候选为 `limit_window.toggled -> calculate` 与 `window_seconds.valueChanged -> calculate`，后者即使limit关闭也会走calculate；原scenario仍只在limit已勾选时写入window字段。原full090有大量setChecked/setValue，从1115、1144等到2961/3163及finally恢复；它们现在可能触发自动计算，不能把52个显式button与整套调用数等同。相同value/checked不必推定信号有无，需实际测量，不屏蔽信号来维持旧数字。

旧profiler只覆盖启动和86–90新增组，未覆盖全部旧prefix；未来95应统一profile完整runtime，并保留startup、各control action、显式button、formatter/render、恢复/关闭scope分段。现profile090不统计MainWindow.calculate或两个signal，需添加这些计数且与数值 `calculate_damage` 分开。原多处setprofile重置必须纳入统一/显式委托设计，避免新global profiler被旧嵌套profiler覆盖而漏记。不同事件可以带一个source-context标签，不能从backend总数反推callback个数。构造/apply/load和读取consumer同样独立记账。

旧before_click/after_click的“1个数值API”只是settled后那次显式click的局部期望，须在95实际代码上验证；自动控制请求另记。原>=52和automatic=total-52仅限其原新增组，不能扩为全量/启动scope。不预定自动次数、全局formatter总数或完成行数。

## 最小可执行迁移顺序

1. 完成91–95后，以实际95HEAD/tag冻结全部维护源，确认clean和branch，再产生新pre-import guard及runtime before/after guard。原730是full090历史数，不能把旧hash或旧数量提前当新95。供依赖/精选复用的full-source byte比对也等实际95，源码变更会要求对应检查新运行。
2. 从精确旧9f7f runner读取构造一个**新的独立full095 runner**，原件只读。注册必要差异：3011可见性、actual95源guard、唯一95输出目录/文件名、完整调用scope instrumentation、历史ID资格及91–95新增组。每个差异精确inverse；去除新增组、还原登记差异后旧保留代码应还原精确9f7f SHA。不能全局replace所有090/旧字段，也不能只迁一个断言后声称完整byteexact。
3. 保留旧动作/断言来源，包括4217旧前缀和090的66新增组，但把6个visibility记录标为迁移；对91text及92row差异逐处记录。4217/4283仅为旧记录数，不是新输出、文本或来源全unchanged的结论。最终长度需由旧来源行与新组实际完成数共同验明。
4. 在新91–95组验证当前rank下Attack/Natural控件及label、真实输入切换/结果刷新；深海色S1基础30秒/10秒4200/1400与玫瑰84/168含倍率速度的资格、零观察条件速度/S2边界；92窗口toggle、on/off下数值变化、0/short/overlong有效长度、伤害/治疗各自AVG边界、原时序模式/供靶与友方潜在治疗限定。使用91/92正式保存结果和root界面验收来源，避免另造笛卡尔。真实默认/technical/raw必须关联同次当前结果。
5. 等93账户cache与94 callbacks最终source/正式证据：重核saved089回读、临时文件隔离、启动/自动写入/恢复scope、readonly标签及观察callback状态。本计划不给未定93/94规定具体实现或成功次数；发现实际影响再补精确迁移。实际Qt/Wine及Linux/Windows兼容广回归由root执行，缺失样本和native Windows/game/desktop仍分开报告。
6. 最终保存唯一95运行脚本、实际源码绑定、byte inverse/delta清单、分段计数、成功/失败/缺失回执与截图/根检视。PASS只来自新head的真实运行，不来自这份计划或历史4283。

启动、信号与恢复预算在95最终runner冻结时确定；本任务为0运行规划。原始路径/SHA、6行迁移、saved089依赖及非执行资格见同目录JSON。
