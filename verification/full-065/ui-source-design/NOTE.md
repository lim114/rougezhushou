# 第65组末实际 Qt 全量脚本设计

本外部候选以 `/workspace/.compat/wine-ui-smoke-060.py` 为唯一基准，SHA256 `d10e4ba78041eee2e70c6793ddf211c06830c6b0bf7f588fa099e59eacbf10a1`。该基准已由root实际完成231项检查，含原055的152项与056–060的79项，覆盖87个技能。此次追加保留这些检查和已修正的“应急招募来源”可见中文/待确认/内部missing key三重合同；源基准原字节另存 `wine-ui-smoke-060-preserved.py`。

新增设计为228项，分节计数为61=96、62=8、63=78、64=28、65=18。它们由真实循环和控件构成，统计将由执行后 `supplemental_checks_by_section_61_65` 与 `total_actual_checks` 记录；总459只是设计数量，不能冒充实际已完成。运行结束还分别核验旧152、旧56–60的79与整个旧060的231均保留。

- 61：24个既有 owner/key QSpinBox，涵盖23个被查询的整数参数；第一适用技能、两模式、真实整数0/1。检测控件和提交参数都为int，并实际点击计算。API原始bool拒绝无法由QSpinBox产生，留在回归测试。
- 62：黍E2 S3与E1 S2、两模式、真正False/True的QCheckBox序列化。E1完整结果不变，E2保留攻击加成与原4秒/1SP参数，实际SP首跳/回转未知。文本拒绝只在API回归，不伪造checkbox值。
- 63：深海色E0/E1/E2无模组、E2低于SUM-Y40级门槛以及符合门槛的三阶段；合法真实整数0/1/既有上界2/3/4/7、两技能（E0只S1）与两模式。核验报告数量int、S1固定每只回复率、模组持有/并发资料与局外假设提示。合法API数字字符串另外有全结构回归；不假造GUI文字字段，不从声明数量推出库存或实际部署时钟。
- 64：凛御银灰S3 rank1/7/10，实际脆弱和协同checkbox两种值、两模式；保留所选等级倍率1.15/1.25/1.3与原物理分项算式。E1只开放S1/S2，S2隐藏对应控件但其typed bool不影响完整输出。GUI原默认脆弱True与API缺省False分别是既有调用约定，脚本均显式选择状态，不从默认猜测。没有证明首次施加、实际覆盖或多个原生来源叠加规则。
- 65：异格傀影S2真实bait_triggers整数0/1，正观察窗口、零窗口、零敌方生命周期、空target_windows，两模式；0无诱饵reference，1保留未知快照/首跳和未排程边界。零窗口/生命周期为0，positive或空target_windows的受影响完整输出未知；不会硬写跨模式的已知小计为0。S1隐藏该控件，并确认producer没有提交inactive key。

所有输入在 MainWindow 的已有隔离临时状态内操作，不运行游戏捕获、聊天或读取外部私人状态。培养条件来自既有只读观察预览。每项新检查点击真实计算按钮并比较实际QPlainTextEdit与真实format_report结果，不能用单独API结果冒充实际可见文本。

API-only设计验证与实际UI分开：`check_public_schema.py` 在公开源副本上真实执行228次公开计算，完整结果和人类格式文本无损存于 `public-schema-checks.json.gz`；`public-schema-summary.json` 明确 `gui_executed=False` 和 `wine_executed=False`。源副本读取时root HEAD为 `0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb`，121个公开源码/JSON无读漂移，随后只在外部副本应用64/65候选source hunk。它不声称该观察HEAD已经完成64/65集成，不能代替root fresh最终分支检查。

静态审阅发现最早草稿把window_dps误写为结果顶层字段，已在真正执行前纠正为 `estimate.skill.window_dps`，设计v0原字节保留在 `design-v0-before-static-review/`。脚本构建器首次辅助AST提取的局部变量错误也已修正，未运行GUI。最终source/API验证没有抹掉错误或把这些准备错误算作验证通过。

新脚本同时加强失败现场收据：保留原异常，并保存当时实际可见文本、选中干员/技能、公开隔离计算、timing文本及失败截图，方便root判断产品遗漏与断言错误。该捕获不会改变失败状态或完成标志。

`build_runner.py` 默认生成 `section65_final_checks_pending=True` 的安全候选。只有第65节来源/schema独立审阅完成后才以 `--ready` 重建最终文件，记录新hash和差异；root在实际集成clean commit后冻结 sourcehash并独占执行Wine。此子任务未执行Wine、GUI或原生Windows，也未修改tracked文件；最终通过与实际计数必须引用root真实回执。

第65节独立source/API审阅已通过，固定source补丁SHA `973a718b445bb72e917137b85202b176c1f1b434c87d56b94ce91c8ec2099622`。已据此生成ready最终runner，SHA `4f18f54047920ac6d7dd32675e070167fe3c172528861423bc9e08f7210ecdcc`，source pending标志False。另有针对该最终runner第65节block与source契约的独立静态检查通过，收据在 `p2-ui065-static-independent/static-review.json`；它只审65 block、语法与marker，没有深审61–64，也没有执行本次实际459项。不能把这个静态通过扩写为全GUI通过。
