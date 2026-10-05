# 0.69 · 深海色触手同时在场上限的直接证据

2026-10-06。本调查只读固定数据和已安装基包，不改生产代码、原有报告/回执，不读取进程内存、运行游戏代码、操作游戏、发送聊天或读取私人状态。

## 已证明的范围

已安装基包 `26-08-16-14-00-43_415873` 的默认配置与原生判定链支持：无额外部署数修正时，深海色精零/精一/精二的触手各自同时在场上限为 **2/3/4**；合法解锁并装备 SUM-Y 任一等级时，精二默认上限为 **7**。这里是该召唤物自己的数量限制，不保证关卡还有七个全局部署名额、七个可用地块或七份库存。

结论不是从“持有七个”猜“能在场七个”。决定性的新资料是 `battle_equip_table` 的 `tokenAttributeBlackboard`，所有 SUM-Y 等级均给触手 `cost=-2`、`max_deploy_count=+3`。0.38的简要机制回执只列了持有数量、费用和生命参考，未把这个原始字段完成对接。模组额外三份补充库存和触手最大部署数增加是两条来源。

## 固定原始数据

固定提交 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`：

- [character_table](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/character_table.json)：触手所有精英阶段培养字段 `maxDeployCount=1`；隐藏天赋键1的 `max_deploy_count` 为 +1/+2/+3。
- [battle_equip_table](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/battle_equip_table.json)：`uniequip_002_deepcl.phases[0..2].tokenAttributeBlackboard.token_10001_deepcl_tentac` 都明确写入 `max_deploy_count=3` 和 `cost=-2`。

本批逐文件核对本地原始表 SHA256 与0.38证据固定的哈希完全一致。新网络检索 [深海色](https://prts.wiki/w/深海色) 与 [触手](https://prts.wiki/w/触手)，公开说明再次确认持有上限+3，但仍不足以单独证明并发上限；数值结论由以下原始资源和静态程序链支持。

## 实际触手资源

原始资源路径不是不存在的 `charpack/token_10001_deepcl_tentac.ab`，而是 `pkgrps/btl_pfb_tokens_0.ab` 内的 `dyn/battle/prefabs/[uc]tokens/token_10001_deepcl_tentac.prefab`。AB大小5084314字节；清单大小/MD5验证成功。精简可重放提取写入 `token-group-prefabs.json`。

资源根对象 `401036205085339412`，天赋所在 GameObject `7502276321476128532` 名字为 `1`；包含 Talent `-6104297881906401516` 与 PassiveBuffAbility `2100531260680023828`，两个类型均通过对应 `PropertiesHash` 在已核验的 MonoScript 表中唯一匹配，不按字段形状猜类型。两组件都在 dummy 上应用，目标选择器为空。唯一 `tentac_t_1` 属性是 `attributeType=16`、`formulaItem=0`、从黑板加载、非外部实体属性；模板 `empty`，持久，最多一层且禁止覆盖。当前元数据确认16为 `MAX_DEPLOY_COUNT`，0为 `ADDITION`。因此默认基数1按培养天赋加1/2/3；装备模组的原始 token 属性另加3。

该资产组10962个对象；只沿实际根对象本地引用提取62个对象。所有用于机制的对象精确读完整字节。引用到的 Spine 二进制 TextAsset 单独保留其边界，不尝试当 UTF-8 文本，也不参与数值证据。开始查找时试读 `skinpack/token_10001_deepcl_tentac.ab`，其对象属于外观且二进制骨骼不能用文本读取器解码；未拿它证明机制，随后已找到真正的战斗 prefab。

## 原生数据与数量判定链

DLL SHA256 `6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce`；元数据 SHA256 `ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118`。调查提取32个完整有界CFG共4827条指令，`read_evidence.py` 重新逐指令核对当前文件物理字节；完整方法清单及哈希在 `native-proof.json`。

1. `AttributesCalculator.TryGetFinalData` 调用 `FetchUniEquipAttributeAddition`（`0x181a9c50d`）。该函数在 `isToken` 分支读取 per-level pack +0x28（`0x181a9b65c`）；当前元数据直接证明该字段是 `tokenAttributeBlackboard`。按当前 token key 选黑板，然后在 `0x181a9b6e0` 调用 `FetchEquipAttributesAdd`。后者用字段的黑板键取值并在 `0x181a9b496` 对装备加法数组进行 FP 加法；`TryGetFinalData` 在同一属性循环中带此装备加法计算并写回结果。不是把主角生命/攻击的装备字段套到召唤物。
2. `TokenCard.Init` 从卡片属性取 `MAX_DEPLOY_COUNT`（`mov edx,0x10 @0x1806f714a`、`GetValueRoundToInt @0x1806f714f`），写入 `maxDeployCnt` 背字段 +0x1e4（`0x1806f7214`）。在场计数不是库存字段。
3. Init还会把最大部署数提高到 `max(已计算属性上限, initialCnt)`（`0x1806f74e8/0x1806f74ea`，写回 `0x1806f753c`）。这一分支不能遗漏。普通主角的 `_ConvertToTokenData(host,slot,...)` 走 `_ConvertInternal`，后者初始 `r15d=0 @0x180abb2bd` 并将其写为 `tokenInitialCnt @0x180abba14`；普通 host 路径不改此初始数量。预定义或显式传入初始数量的 overload 是独立情景，不能在普通干员上套用。并发7的依据仍是模组明确写入最大部署属性+3，不是 initialCnt=库存7。
4. `TokenCard.get_isMaxDeployed` 在默认分支比较 `m_spawnedCnt @+0x1d0` 与 `maxDeployCnt @+0x1e4`，执行有符号 `>=`（`cmp @0x1806f897e`、`setge @0x1806f8985`）。原始元数据给出字段名与偏移。
5. `TokenCard.OnSpawned` 在未设置 `dontOccupyMaxDeployCnt` 时增加该计数（`inc @0x1806f7b43`）；`OnRecycle` 在同样条件下减少（`dec @0x1806f7a07`）。`readyToSpawnWithoutCheckCost` 通过 vtable槽18调用 `get_isMaxDeployed`（`0x1806f8bfc/0x1806f8c0a`），达到上限时返回false（`0x1806f8c10`）。槽18由元数据核对。

由此普通基数 + 已解锁隐藏天赋 + 已合法装备的模组固定加值为：无模组2/3/4，精二SUM-Y为1+3+3=7。

## 可复现与边界

运行项目虚拟环境的 Python，执行 `.cache/research/summon-limit-069/read_evidence.py`。成功输出：32个方法、4827条指令、无模组2/3/4、精二SUM-Y7。该脚本重读实际AB/原始表/元数据及静态CFG字节，只在本调查目录生成文件。

CFG由已有只读工具 `.cache/research/p1-native-cost-054/extract_cfg.py` 提取；各 `*-cfg.json` 中保留源方法名、映射的元数据方法索引、指令的物理文件偏移与字节、完整CFG边界及源码文件哈希。可按其方法名重新提取到本目录，不需启动游戏。

仍未证明当前XLua热更新没有覆盖默认实现；未做当前实机同时部署测量。本程序不参与局内操作，所以不以部署测试填补。其它召唤物、其它更改最大部署数的机制和全局剩余部署名额不在本批结论内；`dontOccupyDeployCnt`（不占全局部署位）与 `dontOccupyMaxDeployCnt`（免于该召唤物自身计数）是不同字段，不能互换。合法模组的解锁精英/等级边界继续沿用已有固定数据。UI可展示“本类召唤物同时在场上限7，仍受关卡可用部署位约束”，不应写成“保证部署七个”。
