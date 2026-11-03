# 多记录实验共同残差假设与留出复核

本组推进首批三人实际成对校准的实验验收能力。单个前后对照或单组时间界限不能回答：不同声明条件下的全部独立读数能否同时容纳一个共同残差、哪些记录形成矛盾、未用于训练的技能或培养条件是否仍相容。

`calibration_experiment(experiment)` 要求明确控制条件、允许变化的 `scenario` 键、同一干员/通道/证据类别，以及实验和每条记录的来源版本声明。每条记录独立保留 `scenario/observation/context_token/source/bounds`，角色须明确为 `training` 或 `held_out`。版本只是调用方声明，不证明客户端或热更新。

所支持的假设只有 `common_additive_residual`：每记录残差界限为独立观察范围减同口径既有模型参考，训练记录求共同交集。区间相容只说明这个明确假设尚未被声明界限排除；不将交集称为实际加成、机制、拟合参数或引擎修正。任何训练样本被阻断都阻断整个训练结论，不能删掉坏记录后宣称通过。

空交集给出两个真实记录ID及其不相交残差界限作为矛盾见证；开放端点保留，不加epsilon。留出记录分别显示所有训练候选仍被允许、仅部分候选重叠、或无重叠。全部留出还进行一次联合求交：各自与训练相容但彼此矛盾也不能被误判为全组相容。同条件重复记录保留并互相列出，不假定统计独立、不输出概率或置信度。

面板通道支持首批三人的同一面板层与同一字段；时刻通道沿用有界校准的明确 `metric/cycle_id/interval_index`、来源/时钟/FPS和声明排序协议。未填字段、未绑定原生相位、模型未知或不匹配的充值需求阻断所选通道，不补零。共同残差不能证明完整面板或原生时钟。

来源闭环复用固定原件 `Kengxxiao/ArknightsGameData` 提交 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`、既有 `catalog.operator_attributes`、面板校准和技能时钟模型。`source-audit.json` 保留培养关键帧、信赖、技能SP参数、银灰初始SP天赋及现有机械师S1条件30Hz初动口径。没有改变任何数值机制。

公开模板只作字面量公式假设演示：三等级攻击各加声明常数5、三技能初动各加声明常数2秒。它们不是游戏面板或游戏事件，也不生成默认测量精度。三人×两通道×相容/留出反例/控制漂移共18个演示向量，结果分别应相容、矛盾、阻断。

Qt工作区 `CalibrationExperimentPanel` 支持实验总表、独立样本草稿、明确训练/留出角色、显式保存、条件导入/标识确认及矛盾记录回指。切换样本保留草稿；未保存草稿不自动进入计算，界面明确提示。自动条件刷新或选择新模板不替换实验。实际来源、客户端、原生时序与偏差原因仍未知，不加载运行记忆或修改引擎。

准备时245冻结源码暂未包含250前置模块，首次隔离导入报 `ModuleNotFoundError: rouge.bounded_calibration`；随后只复制根代理封存的250原件到候选 `dependency_snapshot` 并验证。未修改生产或全局文档。源码恢复后可直接运行正式测试选择器 `tests.test_calibration_experiment`；隔离命令如下：

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python work/p2-experiment-candidate/run_candidate_tests.py
.venv/bin/python work/p2-experiment-candidate/research/p2-calibration-experiment/reproduce.py
```
