# 0.66 · 自然回技来源与医疗职业筛选

2026-10-06。先核验来源，再修正计算资料。生产数值文件只变更医者－自医的职业筛选：空字符串改为 `medic`。不改计算引擎、读取算法或本局状态。

## 原始依据

- 固定[黑流树海原始表](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/roguelike_topic_table.json)，本地 `.cache/game-data/roguelike_topic_table.json` SHA256 `f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86`。医者－自医使用 `global_buff_normal` → `modify_sp_recover[medic]`、自然回技加0.3，表内没有独立职业黑板键；旧生成器因此漏掉医疗筛选。
- 安装基包 `26-08-16-14-00-43_415873` 的 `battle/prefabs/[uc]globalbuffs.ab`（199332字节，SHA256 `74d1efe9b1b2d456681788bd635a0ab512692209c7dbc72b24e95626054bd20d`），按清单大小/MD5和完整类型树解析。2272对象全部精确消费字节，选中11个含SP名称的prefab，其中当前规则只用普通与医疗两种。`read_globals.py`、`globals-prefabs.json`保留结果。
- `battle/prefabs/[uc]dynamicabilities.ab`（134181字节，1048对象全部精确消费），提取幸运饼干与止痛片的两个能力，见 `read_abilities.py`、`abilities-prefabs.json`。未把其它主题的最终倍率prefab当作黑流树海来源。
- 安装DLL SHA256 `6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce`；metadata SHA256 `ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118`。纯文件读取，不执行DLL或读取游戏进程。
- 本批11个有界控制流方法、1589条原生指令逐条比对磁盘字节，所有遍历无截断；分别记录于 `global-selector-cfg.json`、`sp-application-cfg.json`、`sp-helpers-cfg.json`。这些是默认原生路径，不能证明当前XLua热更新未覆盖。
- 资料复核：[医者-自医](https://prts.wiki/w/医者-自医)、[幸运饼干](https://prts.wiki/w/幸运饼干)。前者说明全体医疗的回技效果，后者说明随机领取者。实现依据以上固定原始表与安装文件，而非由文字猜测乘区。

## 已确认范围

医疗prefab开启高级目标筛选，`professionMask=8`。原始元数据 `ProfessionCategory.MEDIC=8`；TargetOptions字段偏移48，值类型去掉16字节对象头后，原生访问为+0x20。`_VerifyAdvanced`读取该mask和目标职业，0x1809e5675调用 `CheckProfessionMask`；后者位与并比较目标职业。枚举/字段提取可用 `read_target_metadata.py`重现，输出与先前提取结果严格一致。

| 当前来源 | 普通自然回技加算 | 范围与叠加依据 |
| --- | --- | --- |
| 香草沙士汽水、羽兽肝酱、迷梦香精 | 0.2、0.35、0.5 | 同一普通global键，经GBuffStack.Preprocess合并数值黑板；总和1.05 |
| 医者－自医 | 0.3 | 医疗职业；独立buff禁覆盖 |
| 幸运饼干个人增益 | 0.8 | 已确认领取者；独立buff禁覆盖 |

三种当前prefab都使用attribute14、formula0（普通ADDITION），不是attribute30或FINAL_SCALER。属性加载、职业判定、全局叠加入口新查；`Blackboard.AddBlackboardStrictly`复用0.54固定研究。0.65已有证据证明attribute14和30各自默认min0，以及Entity回技getter先各自取值后相乘。本批只确认上述正值来源和职业适用性，不新增任意倍率或负值的默认算法。

扫描原始表的relics与charBuffData所有buff黑板键，在含`sp_recover`键的范围找到6个来源：以上5个及止痛片。这个范围不能证明关卡、分队、特殊脚本没有其他速度来源。止痛片依赖战斗中HP曲线，保持资料展示，未纳入局外计算；其0.25秒触发模板和HP曲线只作来源核查。模板原件为 `.cache/research/p1-rules-050/buff_template_data.json`，SHA256 `b119917318c464f92d28fc5eb40b2069e3644674d26cace165f17bf9044e00ff`，固定来源见生成器。

## 修改、回归与限度

`build_relic_mechanics.py`现在为医疗prefab补显式职业；同时同步四条河谷已完成的资料说明，避免重新生成覆盖0.60结论。这四条在生产JSON本来已经正确，仅生成器旧文案需要更新。最后重新生成的整份JSON与生产文件字节一致；生产数据相对本批前仅一个叶节点变化，`verify_sp_sources_066.py`有整份比较。

新增10个测试方法，覆盖32干员87技能的职业分支、先锋回费周期、能治疗的重装、三件通用加算与医疗组合、24种排列与重复ID、幸运饼干绑定、攻回技能排除、战斗HP来源不参与局外计算及生成器。87是技能子情景数量，不冒称87个新测试方法。

初始红测保存于red.log，其中还含一个错误的测试预期：曾要求止痛片HP效果参与计算，随后按用户边界纠正测试，生产offline_scope没有改变。green/green2记录中间失败，不作最终验收。最初完整CORE仅失败旧0.60测试对整个藏品表的冻结比较；现在它仍严格对比河谷完整记录，不再阻止无关藏品的独立修复。整份数据仅医疗职业变化由本批来源核验另外约束。

最终CORE：1208运行，1138通过，70历史跳过，0失败/错误，源码与测试起止哈希一致。732个既有完整计算结果完全保持、无豁免；该旧算例集不含医者－自医，不能用它替代新医疗矩阵。27项临时Qt检查含4项新的医疗回技场景；均为已解析合成输入，不宣称真实游戏面板或新识别样本验收。公开wheel验证新医疗筛选与全部Python/34视觉资源。

P1仍缺：任意回技倍率和负值的完整来源、当前热更新等价性、稳定预计/实际面板成对核对，以及待办中的其他机制。此报告不将默认静态路径当成这些缺口的完成证明。
