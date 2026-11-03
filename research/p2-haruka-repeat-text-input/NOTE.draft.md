第84节处理遥二技能“第二次及以后开启”文本误作肯定声明。原界面 `haruka_repeat` 是 False 默认、只对S2提交的 QCheckBox，`isChecked()` 提供bool。原引擎只在遥非normal S2读原值 truthiness，并切换既有攻击加成与无限持续模式；非空 `"false"` 因此得到True结果。保存的旧公共矩阵中，精一1级/S2等级7/基础攻击1000/frames/12秒窗口：False为timed、治疗5250与伤害10500；True及`"false"`均为infinite、治疗6562.5与伤害13125。这是已有分支被文本错误选择，不是新的二次开启机制结论。

固定第82节 b5a40f30683bfc0945decaabbd4db5914c28427f Git对象720份公开Python/JSON，719份旧文件逐字节不变。生产只在 `rouge/damage.py` 的 `_evaluate_damage_once` 完成所有原计算、finishers与 `build_report` 后、最终return前增加两行CRLF：实际ID char_4202_haruka、实际S2且原 `haruka_repeat` 为str才抛 `haruka_repeat 不接受文本条件；请使用布尔值。`。没有改现有owner/技能消费者、normal治疗或SP时钟，没有解析任何文本真伪。False/True、旧数字0/1、null及其它旧非文本truthiness保留；兼容保留不代表推荐把容器作为新声明。normal、S1、S3及他owner不消费repeat，旧行为保持。

原资料固定 a550f5e048bb94e7cdefc6eb97a4091f0c4c7add，character/skill/battle_equip/uniequip四完整字节实际重hash。角色S2绑定 `skchr_haruka_2`、PHASE_1等级1，十rank原文均写第二次以后攻击力提升且持续无限；atk为1–3级.15、4–6级.20、7级.25、8级.30、9级.35、10级.40，首次专用值为0，目录黑板与原文完全一致。6个实际selected_talents/module_parts选择证明精一无扶摇花火也可以消费S2 repeat，精二才有的扶摇花火只约束第76节浮泡治疗/派生来源，不能拿它门控本flag。BLS-Y 59/60级与实际模块资料核验只是保护原资格；原生目标组合、额外受疗者、浮泡时刻/邻接和附着仍未知。

作者216个独立公共输入、baseline/draft共432次fresh calculate_damage。原生类型树在JSON编码之前保存，同时保存完整结果、实际source helper选择和三份实际格式化报告，零归一化严格复比：64个实际S2文本改唯一新ValueError，134个整份成功/报告/source全同，18个旧错误类型与原文全同。覆盖两种时序、十rank与精一资格、非文本别名、S1/S3/他owner、潜能/模组与未定位来源、零攻击/零窗/零受疗者/零敌方生命/空供靶、部署限时攻速路径与wine ID的既有不适用规则/报告兼容。实际已保存的18个wine/部署组合对照逐份确认：遥S2为INCREASE_WITH_TIME，原prepare仅给攻击/受击回复技能保留periodic_sp，因此wine97周期规则在S2不适用；不能说本节运行了遥的周期wine相位路径。therapy105组合确有原deployment_clock_reference，按实际现有部署路径比较。原bubble_bursts与timing、培养/目标数/模块/他owner旧报告错误先执行，不让新text guard抢原错误；旧时间型S2不消费的initial_target_windows原合法行为保持，不增加validator。

最终8项新增检查与39项原Haruka/整数输入相关检查全通过，无跳过。8new首次为7pass+1失败：测试把时间型S2+wine97中未消费的initial_target_windows错当旧错误。源码核对后只把该情景改为旧合法兼容控制，生产两行未变，原测试/首fail日志/首freeze与诊断保留；正式216对矩阵进一步验证旧合法完整结果保持。运输辅助初次用相对patch输出路径，文件写外部后git换cwd找不到；原脚本/日志/有效初patch保留，改为resolve输出路径后read-only numstat/applycheck通过。测试假设与封包路径准备问题不冒充产品机制故障，也不计作成功的新检查。

提供的 `make-root-transport84.py` 仅读取root明确批准的当前damage SHA，在AST函数最终return前、已有第83节guards之后追加已冻结两行并输出patch与receipt；它不写root源码，去两行严格恢复全部prior当前bytes。此辅助已在第82节实际source上只读验证，patch仅2/0 damage与117/0新测试，applycheck0。root第83节会改同一文件，最终必须在第83节approved bytes上重新生成运输；不能复制作者b5整份damage覆盖第83节。`root-current-source-084.py`提供但作者未执行，实际root集成及注册后要检查去本两行等于approved83 SHA、末guard AST、测试/登记、8份未改source、4原件与6个helper选择。

当前断点：作者source/guard/216矩阵/47最终检查冻结，正式独审进行中；root独占tracked集成、83之后的新运输与当前源实际回归。全部公开证据与准备异常保留，已通过大矩阵不重算。无tracked、GUI、Wine或原生Windows/game实测动作；第85節后的全量cadence由root统一执行。
