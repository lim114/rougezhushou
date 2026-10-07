# 召唤物后续核验：望TRP-X费用参考与独立待办

本次只读生产仓库，全部草稿和调查输出位于 `/tmp`。没有读取私人状态、启动游戏、部署单位或发送聊天。

## 有充分证据的第42节候选

固定公开源提交为 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。先核对四个原始表的大小和 SHA256，完整值与 URL 见 `source-receipt.json`；复用既有0.38、0.68、0.69调查，不重新猜叠加层或数量。

望 `char_2027_wang` 的模组 `uniequip_002_wang` 直接给棋子 `token_10064_wang_stone1`：

- `battle_equip_table.uniequip_002_wang.phases[0..2].tokenAttributeBlackboard.token_10064_wang_stone1[0]` 的键均为 `cost`，值均为 **-1**。
- `uniequip_table.equipDict.uniequip_002_wang` 明确归属望，解锁条件为精二60级。模组三个等级均有这个直接费用加法。
- `character_table.token_10064_wang_stone1.phases[0..2].attributesKeyFrames[0..1].data.cost` 均为 **3**。培养费用参考因此应在合法解锁/装备时为 **2**，无模组、精二59级、精一仍为 **3**。

既有0.69原生回执已经给出通用调用链：`AttributesCalculator.TryGetFinalData` → `FetchUniEquipAttributeAddition` → 按当前token key读取 `tokenAttributeBlackboard` → `FetchEquipAttributesAdd` 写入装备加法数组。这个通用链不依赖触手名字。这里复用归档的字段与CFG证据，不声称在云端重新核对不存在的DLL、元数据或AB原件，也不声称当前热更新/实机等价。`source-receipt.json`记录复用文件的当前SHA256以及`new_native_byte_verification=false`。

当前共享 `summons.module_reference` 仅认深海色。`calculate_damage` 加上香氛以显示独立棋子面板后，合法望模组三阶段仍显示费用 **3**，费用加法漏接。示例：

```python
calculate_damage({
    'operator': 'char_2027_wang', 'skill': 1,
    'elite': 2, 'level': 80,
    'module_id': 'uniequip_002_wang', 'module_level': 1,
    'relic_ids': ['rogue_6_relic_legacy_91'],
})['relic_token_stats'][0]['deployment_cost']  # 当前3，固定参数参考应2
```

已用公开接口检查 **88个情景**，其中 **36个合法解锁情景**漏掉费用修正；覆盖三技能、两时序模式、模组0/1/2/3、精一与精二59/60/80边界。未改变入参。生产相关文件哈希在这次调查前后完全一致。10名已支持且有独立token档案的干员共39个token培养阶段与固定原始数据全部一致；只深海色和望的模组有非空`tokenAttributeBlackboard`，共6个阶段。

`/tmp/p2-draft42`仅准备望的直接费用参考，通过独立`module_cost_reference`接入共享token属性与报告。深海色的SUM-Y费用、HP叠加、库存/在场上限路径保持。不让“模组”标签自动带入SUM-Y的触手指标；无藏品也能展示这个已知的费用参考。香氛与散轶诗简的原有生命、攻击、回复及免费部署位机制保留。草稿是精确anchor替换，未整文件覆盖生产仓库。

## 严格保留的未知

同一棋子黑板的第二项为 `max_deploy_count=+1`。棋子原始培养基础是4/5/6；潜能3的隐藏token天赋也有`max_deploy_count=+1`，但与S3脚本/被自动生成棋子的计数语义不是仅凭这些参数即可闭合。当前没有取得望token实际prefab与隐藏天赋附着、`dontOccupyMaxDeployCnt`等区别的完整证据。因此第42节不把这两项相加得出实际在场上限，不限制或扩充手动棋子伤害计数，不推断库存、站位、技能产生/退出或生命周期。

费用2是固定版本已知培养/装备的局外参考。实际部署是否发生、何时发生、持续多久、当前热更新是否覆盖和实际扣费记录均未核验。

## 独立后续候选：手动all_units来源的面板遗漏

本候选不放入第42节草稿，也不涉及新的游戏机制猜测。公开调用显式`effects`作用域为`all_units`时，`Combat.token_effects`/`effects_for_token`已经让触手模型使用手动来源，但`relics.finish`的token面板仅收集已解析藏品及`origin=run_squad`来源，遗漏手动来源。三个复现位于`public-reproduction.json.manual_token_panel_followup`。

精二70深海色、SUM-Y三级、香氛、观察10秒：

- 手动`hp_pct=.5,target_scope='all_units'`：面板仍2318.4生命、23.184回复/秒；沿0.68已证明的普通生命层应为2016×(1+.5+.15)=3326.4、33.264回复/秒。
- 手动`attack_pct=.5,target_scope='all_units'`：触手S1每次伤害已经970.2=462×(1+.5+.6)，常态面板仍攻击462而对应常态手动参考应693。不要把S1技能攻击层错误改为693×1.6。
- 手动`attack_speed=100,target_scope='all_units'`：触手模型使用200攻速、10秒内15次，而面板仍100。

这是已接受手动参数的模型/报告来源不同步，可后续统一共享属性管道。修正时需保留operator-only来源不流向token、token_ids选择器、符文整数写回/普通层顺序、潜能/信赖隔离以及未知HP层保护。没有利用当前敌人消失时间推断召唤物或友方状态。

## 可重放与回归

重新只读审查：`/workspace/rougezhushou/.venv/bin/python /tmp/p2-audit/after-040/summons/audit.py`。

第42节窄草稿最终66项相关测试通过（12项新测试、54项既有），隔离精选601运行/600通过/1历史skip，零失败/错误。88个公开情景全部费用参考符合固定源；伤害、时钟、其它统计以及棋子以外的报告与禁用该费用规则时相同。最初一个新测试误读取并非所有技能都提供的顶层`hits`，改为核对`components`中的命中数据；生产实现没有为该修正变化。第一次精选的隔离目录未挂入既有公开research，导致夜刀测试找不到公开receipt；加入只读research路径后通过。第一次完整公开字段比对发现新模组面板的来源标签漏写仅提供回复的香氛，已在望的成本面板保留“模组及藏品”而不改变任何回复数值。源码调查最初抄写的uniequip SHA缺少一位，停止并更正；没有拿错误hash继续写机制。

真正Windows/游戏集成尚未验证；Wine兼容回归由root每五节统一执行。
