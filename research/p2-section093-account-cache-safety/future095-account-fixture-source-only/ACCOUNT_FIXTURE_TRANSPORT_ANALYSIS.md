# full095 账户 fixture transport 来源补充（不执行、不计节完成）

只读来源为正式第92节提交 `f509d186e501bfcfd042e45b46e398ec756840ec` / `p2-section-092` 及已封包的93 v1候选。真实92 app SHA `32818adf259dbb124ae86178e0ef82dcb1a316d0f7bf373e5c4b99aa5d25f9f6` 与 v1指定base一致；候选APP SHA `3dd6810e3398471ddb6dbe9545824c7b92ba4d141fc23f889287a8044670a48f`。v1是已FINAL的静态候选，并非93批准/提交/运行结果。v2仍待作者FINAL；其B1忽略的深JSON值复制、B2新context激活旧union无效时incoming-only恢复必须随后绑定实际最终helper及独审，本文不把草稿SHA当合同。

旧runner `verification/full-090/wine-ui-runner.py` 原件729181B，SHA `9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9`。本补包没有复制runner或全部旧archive，没有改变此前STOPWRITE的10份SOURCE PLAN文件。refs含来源路径/SHA/git blob、精确位置、有限摘录、输入schema及全部38个train静态调用位置，均不是执行计数。

## 别名与完整旧位置

v1 APP102调用正式AccountCache构造器，103把operator_observations绑定到其records；APP777的current_operator_state及473的账户摘要读取helper.view。helper158..169从records消费并隔离坏记录；调用点属性的整表替换不会更换helper.records，因此旧restore会让后续fixture写入一个不被safe view消费的分叉字典。

旧账户access恰15处：5个直接记录写入、5个raw备份、5个整表restore。3076另是无id模板生产位置。

| 动作 | 原source位置 | 原来源事实 | 后续最小transport |
|---|---|---|---|
| 水月record | 1260..1262 / 写1261 | owner=char_437_mizuki，E2 L60、Y模组2、rank10；只有fields/ranks，无id/time/scope | 补同key的id；其它已消费值保持，写到原records |
| train生产器 | 1271..1273 / 写1272 | 38处静态调用，fields六项与给定ranks；默认各技能rank10；无id/time/scope | 统一为每个实际owner补id；保持每次完整替换的原fields/ranks与后续select/update |
| 来源边界record | 1640..1646 / 写1645 | silverash member已有id；账户副本显式scope=account；raw含recruitment_kind及char-buff metadata | 保留raw副本与真实run member；safe view按正式合同去除账户本局metadata，不能把账户来源转成run |
| 保存089参考 | 模板3076..3077 / 写3083..3084 | mechanism/myrtle共同的E2 L60、无模组rank10模板，无id/time/scope | 各按mechanist/char_151_myrtle补独立id；不修改5份保存RunState或10条consumer合同 |
| raw备份 | 1634 / 2410 / 2552 / 2740 / 2928 | 分别account_snapshot/account075/account080/account085/account090；保留完整raw records | snapshot保持原native值；不要把live storage对象当备份，也不要用safe view替代raw备份 |
| 整表restore | 1714 / 2484 / 2717 / 2902 / 3143 | 原assign导致别名分叉 | 在同一个records中恢复整个raw snapshot；两属性持续指向同对象，不重新assign其中一方 |

## 合法消费与旧oracle资格

所有legacy临时账户record均由上述直接fixture写入，runner1056..1064使用新TemporaryDirectory并把三条状态路径放入其中；旧runner没有apply_operator_observation/sample_received调用，也未生成captured_at。正式构造器保持原启动流程；禁止为避开真实AccountCache而替换构造器或consumer。

有效producer的最小身份增量只是id=实际map key。1261/1272/3076原缺id，会被helper43..44隔离；1645已有正确silverash id和账户scope。knownid范围来自正式operator_profiles合并合同(catalog.py15..19)，非相邻别名推测：mechanist、silverash和char_*保留原键；OPTIONS25个owner均在32个已实现档案中。每个档案阶段上限、技能解锁/等级数、合法模组/stage已记refs，不向消费者塞未知owner以逃过筛选。

fields必须仍为mapping；六个原培养值、ranks string keys和原特殊extras保持。原固定E2 L60/80/90按各档案上限核对；水月Y2、望2、棘刺/灵知/遥等原模组identity与1..3stage属于各原档案。低E0/E1边界使用原rank1/4/7（例如deepcl2010..2020、Shu2278..2281）；E2用原1/4/7/10。helper69..109允许合法但未解锁的模组请求保留，不能把module_id删掉来让below-gate比较通过；锁定技能的安全数字仍按原formatter消费，extra不存在的skill3条目不扩成真实第三技能。参数化group071..085来自cases075251..303、cases080497..664、cases085810..981；实际输入的培养tuple/rank路径已逐段读取，仍需95真实调用safe view核定每个消费结果。090的52条literal请求有14个去重培养组合列在refs；选定技能rank和当前rank来源继续保持。

absent captured_at按合同保持absent，APP851在非空state读取默认0；absent sources/field_times/skill_times保留各自缺省，不虚构墙钟、来源或已确认时间。所有显式timestamp新增测试必须等正式helper在实际平台的localtime/strftime资格检查，本文未调用任何时间消费函数。不能改用observe作旧fixture的无差别运输：observe会产生captured_at、sources/times/merged_from_pages、union与save动作，改变089完整native oracle并引入新调用账；若95后选择正式observe路线，必须逐个登记这些额外delta及真实磁盘/保护影响，而不能放宽旧比较。

089必须同时迁移expected_state：3095的account-only expected添加mechanist的同一个id，3101完整native equality保留；active-run分支3096..3100继续由真实member覆盖id/scope、合并培养、保留member ranks与run_confirmed_fields。两条账户fixture各自id不同，不能给共享模板硬编码同一个owner。3105培养整映射、3106..3109技能/rank、3111全部旧labels、3113summary、3116roster、3117完整RunState native、3118crew整数及3129..3130无constructor/apply/load回放事实全部保留。这里是sourceproducertransport身份delta，不是damage/text golden迁移。

58的1658..1709真实run来源和账户来源三种边界继续原样断言：run member的recruitment_kind、scope、应急雇佣label；账户only或run training关闭时scenario来源None、原数值不增益。safe view按合同移除账户recruitment_kind等本局metadata；原raw仍保存该来源用于证明账户事实存在，不能直接改raw删除它来削弱ownership案例。APP843..860原培养/账号参考/本局确认label分支保留；93notice按正式状态追加，其增量需95逐条资格记录，不能预称所有文本相等。

## 后续95边界（无代码草稿）

最小建议为统一接入现有record storage：生产器补合法id后直接写同一个records，原raw备份和所有五个restore均保留该对象，保留每次原select/update和finally控制恢复。全局preserve_original、load_issue和per-id issues不重置、不清除；合法record被已有隔离状态挡住时视为可见失败，不能通过fixture清保护/删issues掩盖。legacy好fixture在真实新临时cache的clean scope运行；93坏文件/隔离恢复案例另用正式构造器和隔离公共路径，不让旧fixture运输代替正式observe的恢复检查。

95最终source冻结后，逐位置登记producer id、expected_state id及五个storage restore的精确delta/inverse；再次确认window.operator_observations与helper.records始终同对象。保持RunState真实事实与原所有完整native/ownership断言，记录startup、全部control、explicit、cache view/observe/save、render与restore的实际调用账。不能屏蔽callback或清保护维持旧数字，也不能以当前同次formatter守卫当旧text golden。原4217/4283只是历史记录数；不能声称全值/文本/来源unchanged。guard732至多是候选新文件的预计数量，最终93/94/95源码、guard条数与新测试/回调/API次数均待actual95 HEAD并真实验证。

本包仅SOURCE_READ_ONLY，0项目/import/API/helper/formatter/tests/Qt/Wine调用、0tracked改动、0private读取，runtime未运行、代码迁移未实施、root独审待办，不算93或95完成。作者v2 FINAL、rootreview、实际95冻结后才允许runner codedraft及真实回归。
