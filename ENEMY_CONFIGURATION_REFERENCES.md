# 固定敌人配置与计算资格

固定数据库必须存在精确引用等级，才会使用其属性参与目标伤害计算。当前105关卡中的1087处敌人等级引用，有1029处满足此项资格；其余58处保持未知。缺失等级的原字段投影仍可在技术资料中查看，但不能替代别名、默认构建或当前服务器机制。

`enemy_skill_reference` 现在同时保留原等级记录、本关覆盖、基包技力分项及 `compiled_configuration`。后者按原生构建规则解析技能和天赋黑板；`inheritance_resolved` 仍为false，表示完整实战机制没有闭合。固定战斗预览与局外工具显示中文配置状态；实际发动时刻、完整回转和技能伤害仍未知。

| 来源情况 | 已证基包行为 |
| --- | --- |
| 顶层天赋黑板null或空 | 保留旧黑板；初始None不变 |
| 顶层天赋黑板非空 | 旧目标None时才创建，然后按key合并；其他旧key保留 |
| 技能列表null或空 | 不清空旧列表；最终空列表写None |
| 新技能未匹配旧同prefab，或新黑板为空 | 整记录替换同prefab，保留新黑板的原None/[]及两列值 |
| 匹配旧同prefab且新黑板非空 | 深复制新技能全部字段，复制旧黑板后按key合并新黑板；旧冷却等标量不保留 |
| 执行黑板合并helper | 删除所有同key后追加；空/None字符串走数值构造，非空字符串将数值列置0 |

按原数据库等级顺序处理，再应用精确关卡覆盖。字段0有意义；null不等于空列表。key和prefab使用原字面比较，不做大小写或空白改写。这里保留的是序列化数值参考，没有将它们用于未知的实际技能总量。

依据为固定游戏原件的 `ApplyDefinedData`、`_ApplyBlackboardData`、`_ApplySkillData`、各predicate和精确generic实例，以及ESkillData类型/字段绑定。16个相关方法、1415条唯一指令和283处绑定字节已逐项核对；证据在 `research/p3-enemy-configuration-current`。DeepClone的字段判断仅限已绑定的六字段Serializable ESkillData，不扩展到任意对象。

运行独立核验：

```powershell
.\.venv\Scripts\python.exe research/p3-enemy-configuration-current/verify_native.py --game-dir 'D:/Hypergryph Launcher/games/Arknights'
```

不传游戏目录时仅检查公开产物一致性，并明确报告原文件比较不可用。脚本不执行DLL或序列化代码，不读取进程或私人状态。精确等级和处理顺序另有第203节公开原件证据。当前热更新、默认/别名路径、技能控制器、首领阶段及实际触发仍待核验。

元数据标志解释依据：[FieldAttributes](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.fieldattributes)、[TypeAttributes](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.typeattributes)、[SerializableAttribute](https://learn.microsoft.com/en-us/dotnet/api/system.serializableattribute)。这些文档只解释.NET标志；游戏行为结论来自对应原件调用和控制流。
