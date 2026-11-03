# 085梓兰条件来源封包

固定产品 `b5a40f30683bfc0945decaabbd4db5914c28427f`；原游戏数据 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。重新核对现有完整character/skill/battle_equip/uniequip四表原件的大小与SHA；没有下载、重建或猜机制。三个原skill对象、30个rank全部黑板/名称/描述/时长、三个技能解锁资料、完整角色含具名和隐藏天赋、完整模组元数据/三级parts均保留。

“翔虫机动”是原 `character_table.char_1048_orchd2.talents[1]`，prefabKey1。E1等级1原atk=.10，E2等级1=.15，atk_duration均30。E0没有此具名天赋。模组X2/X3在E2L60覆盖同index1/prefab1/name的atk=.20；各自另一index3/nullname候选只有respawn_time−17/−18，不能误用隐藏再部署身份判断near资格。

固定真实 `selected_talents` 源完整保留。它按phase/level/potential选最后合资格候选，再按合资格模组parts应用同index覆写。85类型检查要调用此真实helper并检查已选具名“翔虫机动”，不能仅检查elite。此source-only封包没有执行helper或API；实际选中结果和完整计算由随后的作者/正式独审核验。

当前near消费者是初始化 `apply_self_talents` 的具名天赋分支（operator_engine.py:211–219），适用于所有已合法选中的技能，并影响后续normal计划。E0inactive仍应忽略任何near字段。它不是实际部署位置/30秒覆盖的读取，新工作不能重写已有atk层或建立30秒事件。`double_charge`只在S1箭矢参考与初动/周期资源消费；本85只修near文本，不扩张double_charge合同。

Qt有明确原生产者：OPTIONS bool默认false→app.py:665–666真实QCheckBox；owner/skills三技能匹配决定显示及1035–1037的`isChecked()`序列化。double_charge只S1、缺省true。未启动Qt，不能将静态生产者证明称为实际界面验证。

候选检查位于 `damage._evaluate_damage_once` 的build_report之后、return之前，仅在Orchid、near值为str且真实helper选中该天赋时拒绝。已有培养/技能/模组/敌人/藏品/时序与所有finisher/report错误先运行，保持旧错误优先；期望从当前已计算结果返回改为明确类型错误，不改合法结果。83/84后续同函数late guards由root独立合入，85只做独立插入hunk。

历史ea7866b已有2个near调用保存为完整JSON及3份报告：base_attack1000、E2L90、S3、rank10、frames/10秒，boolFalse攻击1000，文本false攻击1150。旧4件精确SHA已复核且原封包字节未变；本目录复制保存历史来源。初次全125公共源byteidentity绑定在operator_engine.py正确拒绝：b5新增苏苏洛文本guard；当前其余124件相同。失败诊断与原diff保留，因此这2例只作历史证据，不计当前85新调用、不作为当前matrix复用基线。当前作者验证需针对改变过的固定源码新计算。

本封包0新API、0helper运行、0tests、0draft、0GUI/Wine、0tracked改动。只读准备曾猜错raw缓存和两个测试路径，随后rg定位真实路径；错误保留于回执。未知实际站位覆盖、原生附着、箭矢/充能/结束时钟、当前热更新均保持；机制扩张需对应版本附着、实际覆盖/事件与组合层依据。类型修复不要求这些未知变为已知。
