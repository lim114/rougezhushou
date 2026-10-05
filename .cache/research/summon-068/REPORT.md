# 0.68 · 深海色模组生命叠加

2026-10-06，按用户最新要求先推进P2，P1保留断点。本次只处理SUM-Y的触手生命合成与依赖生命的回复，不改识别、攻击时序、召唤数量或本局状态。

## 先查来源

复用0.38的培养、费用、库存及模组等级依据；复用0.56的符文层和整数写回、普通天赋乘区依据。重新定向查询[深海色](https://prts.wiki/w/深海色)及[触手](https://prts.wiki/w/触手)的模组/同时部署资料；公开说明确认10%和15%，但没有补齐同时在场限制，也不足以独自证明叠加层。未用持有数量推断在场上限。

新的决定性依据是已安装基包`26-08-16-14-00-43_415873`的`battle/prefabs/[uc]equips.ab`：728182字节，SHA256 `4218a40e8a033c5309cbb601e8afdfeb3bff7a2266256b116972c46b372f6874`。解析9220个对象，全部精确消费字节；选出深海色5个模组资源。`read_equips.py`可重现，读取原始文件、不执行游戏代码、不读进程内存。

固定原始表：[battle_equip_table](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/battle_equip_table.json)。二、三级分别引用`deepcl_equip_1_2_p2`和`deepcl_equip_1_3_p2`，`isToken=true`、`target=TALENT`、`prefabKey=10`；黑板`max_hp=.1/.15`。实际资源中的Talent也指定键10；PassiveBuffAbility没有外部目标选择器，唯一buff为`deepcl_tentac_e_talent`，模板empty、持久、禁止覆盖、最大堆叠1。

该buff明确写入`attributeType=0`、`formulaItem=1`、`loadFromBlackboard=1`、`fetchBaseValueFromSourceEntity=0`。固定元数据确认0为MAX_HP、1为MULTIPLIER。两个MonoBehaviour的PropertiesHash分别唯一对应PassiveBuffAbility与Talent；不是仅据字段形状猜类型。加载与普通属性路径复用0.66的`Buff._LoadAttributesModifier`和0.65的`Attributes._CalculateAttributeValue/Reset`等完整CFG，本批重新逐字节核对11个方法、1806条指令。DLL/meta与0.56/0.65/0.66相同。

`verify_summon_sources_068.py`核对实际AB大小/MD5/SHA、类型、字段、两阶段原始黑板及既有原生字节，输出`native-proof.json`。普通乘区的含义不是本批新增假设，复用已经核验的属性公式。

## 应用规则

生命先使用独立触手培养值，套用已支持的藏品/分队符文并执行其整数写回；之后模组生命与其他普通生命百分比相加。模组不乘召唤师信赖、潜能或本体装备属性，也不是一个新的独立最终乘区。

示例：精二70级触手生命2016，召唤物生命符文30%先得到2621；三级模组再得到3014.15。若另有已解析普通生命25%，结果为2621×1.4，而不是2621×1.25×1.15。百分比回复按最终生命计算；1%回复为30.1415生命/秒。这里只是已知局外情景，不冒充实机测量。

`summons.py`对已核验规则执行此路径。未核验模组仍保留复合未知保护；一阶段无生命加成，等级/精英解锁边界继续沿用原判断。报告显示预测生命与回复并说明顺序，删除此组合旧有的未知提示和分离参考；其它干员不增加此栏。

## 限度

未证明当前XLua热更新没有覆盖默认配置；未取得当前预计/实际面板成对样本。持有上限7不证明能同时在场7个，现有局外0至基础已解锁数量的范围保持。其他召唤物模组、技能时序及P2其它事项仍未完成。

开始查找时尝试`charpack/token_10001_deepcl_tentac.ab`，清单不存在该路径，解析停止，没有拿缺失文件作证据。实际结论来自随后完整提取的equips.ab。首轮验证器将类名误写为PassiveBuff，已按唯一匹配的真实类型PassiveBuffAbility更正；不是生产机制修复。
