# P2 026–030 候选：瞬发与多段窗口只读审计

本审计不指定实际开发节号。五个独立候选可由主代理择序落地。未修改仓库、未执行网络请求、未重试 PRTS 已拒绝路由、未查私态或模拟游戏。已阅读 AGENTS.md、CLOUD_HANDOFF.md、PROJECT_PROGRESS.md 与 WORK_IN_PROGRESS.md 顶部。当前分支为 codex/p2-development。22 敌人选择器、23 手动重量、24 古米/黍 S1、25 初雪积雪生命周期均排除；已有灵知、维什戴尔、水月、伊内丝、安洁及星熊 S3 修复不重复。

已应用 cloud-environment-onboarding:setup 与 cloud-environment-runtime 技能的只读检查约束；没有配置修改需要保存。所做验证只证明 Linux 计算缺陷，不代表 Windows/游戏/客户端动作绑定。

## 原始来源与再现入口

固定原表来自 Kengxxiao/ArknightsGameData，commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。复用 research/p2-phase-guards/source-receipt.json 指定缓存；完整原表在 .cache/p2-s1-binding。重新逐字节核验：

- skill_table.json：11,447,929 字节，SHA256 `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`。
- character_table.json：14,975,251 字节，SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`。

完整原表 URL、角色技能映射、原始 skill level 对象、当前相关生产文件 hash 及 70 个公共入口计算结果见 source-and-reproduction.json。`reproduce.py` 可在当前 checkout 的 `.venv/bin/python` 重跑，仅向本证据目录写 JSON。

每次以 base_attack=1000、skill_rank=10、enemy_defense=0、enemy_resistance=0 调用 `rouge.damage.calculate_damage`。五个候选各覆盖 frames/continuous 两模式 × 默认、window0、window1、本体供靶范围为空、0秒消失、全程打断、5秒后本体供靶，合计70次本地计算。JSON 的 no_target 标签仅代表 `target_windows:[]`，不证明独立盾牌/飞行物的可命中目标为空。不是新增仓库回归测试。

当前 `rouge/data/timing-profiles.json.operators.{char_4182_oblvns,char_1044_hsgma2,char_1048_orchd2}` 的 normal:null、skills:{}、binding_status:reference_only 明确没有这些技能的实际时序绑定。不能将普通攻击参考、原表 duration:-1/NONE 或尚未绑定的视觉事件转换成技能实际持续时间。

## 1. 丰川祥子 S1：八个音符无条件计入零窗口和空目标

精确选择器：`character_table.char_4182_oblvns.skills[0].skillId == skchr_oblvns_1`；`skill_table.skchr_oblvns_1.levels[9]`。

已证：描述“演奏出8个音符”，各倍率依次 1、0.92、0.75、0.58、0.42、0.33、0.17、0.05；duration:-1、durationType:NONE、可充能2次。这个数据没有证明八音符同刻命中，也未证明瞬间结束。

生产位置：operator_engine.py 的 char_4182_oblvns/S1 分支将 mode=instant,duration=0，逐个调用 emit，无目标/窗口资格检查，也无 times_seconds。当前默认、window0、window1、空目标、0秒消失、全程打断都输出3376；window1仍显示0秒。frames/continuous结果一致。默认还给出duration0、周期3.533333333333333秒、周期伤害5776，未放置的八音符直接进入阶段/周期总量。

可改边界：明确指定零窗口的观察输出为0，保持声明窗口1秒。mode=instant 作为“瞬时触发”分类本身可以保留；duration:-1/NONE 不证明该分类错误，也不证明实际0秒结束。正常情景保留八倍率与每音符条件参考；实际命中时序无法放置时，观察/阶段/周期总伤应明确未知，不把所有emit分项当开启时刻命中。不应把duration:-1解释为普通无限持续技能。本体范围与飞行音符实际碰撞范围绑定未证明，不能只因本体target_windows为空便宣称全体音符不可能命中。

未知：首音符产生/命中、后续间隔、独立弹道碰撞/消失、初始无目标时是否仍演奏、实际结束/阻回及充能回转。原表不支持凭借相邻普通攻击时钟补齐。

建议测试：0/1窗口保持值；两时钟模式0生命周期不发布确定伤害，本体供靶范围为空保持碰撞未知；八倍率保持；有目标的每音符条件参考不伪造times_seconds；阶段/周期未知与报告展示一致。全程打断案例仅作再现，是否取消已生成音符需脚本证据，不能直接臆定零。

## 2. 斩业星熊 S2：盾击与盾牌环绕被归为零秒瞬发

精确选择器：`character_table.char_1044_hsgma2.skills[1].skillId == skchr_hsgma2_2`；`skill_table.skchr_hsgma2_2.levels[9]`。

已证：投盾同时对阻挡敌人三连击，每击0.9倍；盾牌环绕一圈，接触敌人时每0.5秒造成1.3倍法术伤害，自身回复盾牌实际伤害的15%。duration:-1/NONE 没有给一圈时长或结束相位。接触次数不等于施放时刻。

生产位置：operator_engine.py 的 char_1044_hsgma2/S2 分支 duration=0；三连击使用instant；`shield_contact_ticks`（默认1）直接emit环绕盾牌伤害与伤转治疗。默认、window0都输出4000法伤+195治疗，window1仍显示0；frames本体供靶范围为空/0秒消失/全程打断仍输出盾牌1300+195治疗；continuous连三击都保留4000+195。本体供靶为空而残留盾牌条件伤害不单独构成缺陷：原文明确盾牌环绕接触，且手动次数声明一个独立接触来源。

可改边界：0窗口输出0伤害和0伤转治疗；声明窗口保持。`target_disappears_seconds:0` 是当前目标全局生命周期为0，故盾牌对该目标实际伤害及对应伤转治疗确定为0，两时钟模式同样适用；它和本体target_windows为空不同。保留三击2700、每次盾牌接触1300、每次伤转治疗195及0.5秒间隔的条件参考；手动次数不得自动转换为0秒、等间距tick或完整一圈持续，也不能因本体供靶为空自动清零。未放置的盾牌伤害与治疗须分别保护未知，不能只调用伤害mask后仍把195作为实际治疗。完整结束/充能/周期保持未知。

未知：投盾绑定、三击相位、一圈轨迹与时长、接触进入/离开及首跳/同目标判定、三击与盾牌快照关系、是否可与回转期共存、技能阻回与普通攻击恢复。移动/打断如何影响已投出的盾牌不能依据通用instant guard推断。

建议测试：0窗口伤害与伤转治疗同时0；frames/continuous全局消失0实际伤害与伤转治疗均0；本体供靶为空时仍保留独立接触参数参考，但没有时钟就不能发布195为实际窗口治疗；手动0/1/N接触次数仅改变条件参考；每次减伤后伤害×15%依赖保持；正窗口的实际tick/治疗及阶段/周期未知。加入本体范围为空+手动正接触次数情景，防止新增错误的统一供靶归零。

## 3. 焰狐龙梓兰 S1：四箭/五箭整段瞬发进入零窗口

精确选择器：`character_table.char_1048_orchd2.skills[0].skillId == skchr_orchd2_1`；`skill_table.skchr_orchd2_1.levels[9]`。

已证：4支箭各1.6倍；有额外充能时再耗1层发5支箭各2倍；duration:-1/NONE，没有箭矢时钟或技能结束。当前double_charge输入只声明选择该条件参考。

生产位置：operator_engine.py char_1048_orchd2/S1分支 mode=instant,duration=0，对4/5次调用instant。当前默认与window0/1都输出18860，window1显示0；默认duration0、recharge8、cycle8、cycle_damage30860。frames的空目标会挡住全部箭矢，但continuous空目标仍18860。

可改边界：零观察窗口为0、保持声明窗口；当前目标全局生命周期0则对它实际伤害为0。本体target_windows为空不证明整个箭矢路径无目标。保留4×1.6、可选5×2及既有强击瓶条件来源参考；不把4/5个emit次数标成0秒命中，也不把8秒充能参考当可验证完整回转。首箭、后续箭与额外充能消耗/结束绑定未知时，完整观察与周期保护未知。

未知：箭矢发射/飞行/目标重选、额外充能消费的动作相位、全部箭矢是否共享强击瓶前50次加成、实际结束和阻回。迟到供靶不能因为0秒无目标直接推整次为0；也不能假设技能等待迟到目标。

建议测试：double_charge false/true条件参考倍率与次数保持；0/1窗口；frames/continuous的空生命周期；首箭与各段times未知；充能参数和已验证完整结束时间分别展示。

## 4. 焰狐龙梓兰 S2：12箭与落地整段计入0/1秒窗口

精确选择器：`character_table.char_1048_orchd2.skills[1].skillId == skchr_orchd2_2`；`skill_table.skchr_orchd2_2.levels[9]`。

已证：4.2秒技能参数，起飞后3次射击分别3、4、5箭（共12），各1.8倍；之后落地3倍伤害。黑板fly_duration0.2、fly_end_duration0.2只证明对应参数，不证明首击或3轮间隔。

生产位置：operator_engine.py char_1048_orchd2/S2默认mode=timed，但两项instant把12箭+落地整段当施放时刻来源。window0/1都是28290；window_seconds确实0/1，故1秒DPS被报为28290。所有分项缺times_seconds；落地分项因单次被标instant_event。frames空目标挡住来源，continuous空目标仍28290。

可改边界：零窗口为0；保留现有0/1窗口长度；12箭与落地只保留条件总量参考。没有射击与落地时序时，不从4.2秒/0.2参数推定命中。实际短窗口、阶段总伤和周期总伤需未知保护；4.2技能持续参数可单列原表依据，但它不证明最后碰撞在4.2内或当前热更新真实结束帧。

未知：开启/部署自动释放相位、3轮与12箭事件绑定、落地伤害触发时间、飞行/碰撞/目标生命周期、结束/阻回/普通攻击恢复。原表描述部署后立即释放一次，与普通初动充能计算间也存在待审差异，当前候选不要借此自动改initial_seconds。

建议测试：0/1/4.2窗口及落地不得标instant_event；3/4/5箭与单次落地倍率保持；frames/continuous空生命周期；未知tick不能以均分4.2或4.2末尾补时钟；默认来源参考与实际阶段明确分开。

## 5. 焰狐龙梓兰 S3：3秒蓄力被当整个瞬发持续并扩长用户窗口

精确选择器：`character_table.char_1048_orchd2.skills[2].skillId == skchr_orchd2_3`；`skill_table.skchr_orchd2_3.levels[9]`。

已证：原文“蓄力3秒后”射出无限射程贯穿箭，每飞行一段距离对周围敌人造成3.6倍物理+0.6倍法术。duration:-1/NONE，wait_duration1.5、dist_interval0.25、max_dist99是黑板参数。没有证据证明wait_duration就是3秒蓄力全阶段、dist_interval是时间、或3秒就是技能/箭矢结束。

生产位置：operator_engine.py char_1048_orchd2/S3直接mode=instant,duration=3，覆盖此前min(rawduration,window)结果。window0/1都显示3秒并输出4830；duration3、recharge25、cycle28、cycle_damage49830。frames在0秒检查供靶，5秒后供靶判0；continuous空目标仍4830。各分项没有贯穿命中时钟。

可改边界（最优先、无需任何动作猜测）：window0/1必须保持0/1，不被3秒蓄力参数扩大，零窗口输出0。3秒仅保留蓄力描述参数；指定dragon_arrow_hits只给独立条件伤害参考，不能当0秒或3秒内全部命中。完整持续、释放/贯穿实际时钟、充能阻回与周期保护未知。原文顺序支持“先蓄力后射箭”，但没有可绑定观察帧时不能新增time=3或凭1.5替代它。

未知：蓄力起点/倍率/动作绑定，释放与观察相位，箭速、距离到命中时间、贯穿重入、离开供靶后仍碰撞、实际结束与阻回。不能把供靶窗口等同贯穿路径，不能猜延迟供靶必须命中。

建议测试：0/1窗口不扩长；dragon_arrow_hits 0/1/N参考次数独立；3秒与wait_duration1.5分别保留原语义；物理与法术逐段减伤不变；正窗口实际输出/阶段/周期未知，不造首伤t=3。不要因全程移动或打断便假设已射出的贯穿箭消失。

## 共同实现范围建议

最少可以先修用户明确窗口的保留与零窗口输出，它们有现有 [开始,结束) 口径和直接公共复现，不依赖未知游戏脚本。其后按已有uncertain_sources模式增加明确的条件来源参考与未知保护；星熊S2额外需要治疗依赖保护。不要全局改instant helper使所有技能同时改变，也不要将duration:-1全部归类为infinite。推荐下一组以三个独立节处理：28祥子S1、29异格星熊S2、30梓兰S1/S2/S3共享窗口问题。

保留有来源的倍率和条件总量，并将未放置来源从实际窗口/阶段/周期区分。正窗口不应在缺时钟时假装确定全量；本体空供靶不证明独立盾牌/飞行箭矢无目标。任何打断取消、重选目标、等待、发射顺序或蓄力结束相位应另查直接证据；本报告对这些没有默认解答。
