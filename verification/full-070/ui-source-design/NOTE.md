# 第70组末实际 Qt 全量脚本交接

冻结最终 runner 为 `wine-ui-smoke-070.py`，SHA256 `3bba0d28376165b84938906b45048f31b75d89cf6e1c4d1e5246d17f6272f9b3`。唯一基准是 root 已实际通过的 `/workspace/.compat/wine-ui-smoke-065.py`，SHA256 `4f18f54047920ac6d7dd32675e070167fe3c172528861423bc9e08f7210ecdcc`；原字节保留在 `wine-ui-smoke-065-preserved.py`。旧459项、87技能、应急招募中文来源/待确认/内部missing条件三重断言及所有旧范围统计均保留。

新增设计382项：66=120、67=74、68=72、69=36、70=80，设计总841。计数由各节真实循环生成并在执行后核验；本作者没有执行Wine或实际Qt，因此841不能写成实际通过。旧计数分别核验055的152、060的231与065的459；旧056–060及061–065计数区间已在追加前闭合。

- 66：三个技能、两模式、ghost_count/casts真实整数组合、四种观察范围。0个魂灵时声明施放次数被原门禁忽略；正次数只保留条件伤害参考，施放/次生命中时刻、随机独立性和生命周期仍未知。12个真实数字“正魂灵、正次数、零窗口”组合验证已有准确错误文本及清除旧结果；它们是预期错误检查，不是成功计算或API文字输入。
- 67：三技能、两模式、次数0/1/20，零窗口、立即消失、空供靶、100损伤抵抗与E1未解锁堕梦。70损伤参数与整数metadata保持，攻击时刻为空、未排程。零观察保留cast pending/window0；不把continuous空供靶小计硬写成frames的0。
- 68：三职业/同职业四种真实bool组合，E2三技能、E1两技能与E0一技能，两模式；E2还与four_sui False/True配对。只对所选黍确认原HP12%/AS12参数；低精英完整结果不变，四岁周期原点/首跳/阻回/回转继续未知。没有读取队伍职业数量或声称全队实际增益。
- 69：S3 rank4的真实cooperative与fragile bool组合，四观察范围与两模式，保留原物理分项条件算式。E0 S1隐藏协同控件、S3不可选，typed global flag不改变输出。实际单位位置、覆盖、同步出手及叠加来源身份没有因此核验。
- 70：S3 rank1/7/10、两模式、four_sui与播种条件False/True、正/零/立即消失观察。真实checkbox标签精确为“存在地面敌人处于播种地块”，且记录一张实际控件截图供root查看。当前目标保持未选择，checkbox直接声明存在条件；没有添加ground_type过滤、实际地面敌人识别、站位、叠层、传送或技能触发时钟。E1没有S3，S1/S2隐藏该控件并不提交inactive key。

source-first合同来自66–70最终固定patch及原始来源回执，未新增机制。外部API源码包以clean65 git对象 `b4428de479b055aca52b79e095a07cb76c21bd34` 的121个公开 `.py/.json` 为基线，只应用最终生产hunk。随后逐字节比对root clean70 `552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9` 的同121个git blobs，全部相同；没有复制root working tree或修改tracked。此121个产品文件范围不冒充root完整704个验证文件。

API设计证据单独保存：`check_public_schema.py` 真实执行382次公开计算，370次完整返回、12次预期ValueError；完整结构化结果和format_report文本无损存于 `public-schema-checks.json.gz`。源码、调用参数无漂移。该检查验证未来断言的schema，未产生任何实际Qt值或窗口文本。

`check_api_text_contracts.py` 独立执行86次公开API调用，34对完整JSON/报告严格等值与18个准确错误。数字字符串、API raw bool错误、文本条件错误及旧错误优先只在 `api-text-contracts.json.gz` 保存；它们不进入任何实际Qt检查，不能把API文字改成checkbox值或QSpinBox数值来伪造窗口覆盖。

独立静态审阅通过，收据 `independent/runner-review070.json`：逐项重建完整旧065代码并与最终070比较，旧459保留；核对841设计计数与12个数字错误，121产品source同clean70 blobs，保存的382次API设计结果无异常。该审阅没有执行Wine、GUI或原生Windows，实际通过仍需root收据。

runner继续只使用隔离临时MainWindow状态，不进行游戏捕获、聊天或读取外部私人状态。培养来自已有只读公开观察预览，实际点击计算按钮并核对QPlainTextEdit可见文本。失败会保留实际报告、公开隔离计算、timing文本与失败截图；原有最后友方时钟说明截图继续保留，文件名改为070，避免覆盖旧065回执。

最终runner/hash在早交root后未修改；新增文档和manifest不改变该冻结文件。root独占Wine执行，在clean70冻结sourcehash后确认实际计数与结果，再按既有每五节流程归档。本作者的外部草案、来源/API设计和静态证据由 `archivable-public-manifest.json` 明确列出，排除公开源码运行副本、字节码与任何私人文件。

root最终实际验收已另行完成：root own `/workspace/.compat/wine-ui-070.json` 记录841项实际检查、旧459完整保留、新120/74/72/36/80、complete_ui_validation=True、source_drift=[]，耗时28.917秒。root已实际查看MainWindow和播种条件控件截图。该收据与本作者设计/API/静态收据分别归档，不把本作者未执行的GUI改称已执行；Wine兼容性仍不是原生Windows或游戏验证。root另完成Linux1553、Wine1627、双方精选892通过加1个保留skip及pip检查，具体完整证据归root平台收据，不重复计算。
