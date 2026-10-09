# 第106节原实现环境入口观察 · Source-only v1

这不是产品验收，也没有执行过项目、helper、codec、Qt、Wine 或测试。Root已提供final105实际748份Source guard `/workspace/.continuation/full105-source-suite-guard-v1.json`；第105节可用全量仍pending，不能说成已完成。Root可绑定这份实际Source及CORE执行原API观察；本脚本没有伪造CORE哈希，也没有放宽9份已读取生产消费源码的pin。

## 共同功能组

拟议主题是本局环境身份与适用模式的一致准入，包含三条相关消费缺口：

1. `run_config.difficulty_value`只检查`modeDifficulty`；数值`prepare_run`同时检查`mode`。一个已接受的合法JSON缓存`value:2,mode:MONTH_TEAM`在复用资格里成为常规难度，在数值入口却受到现有ValueError保护。`MainWindow.sync_run_config`按dict存在锁定难度预设并标自动确认，summary也直接把raw值写为当前难度。候选应统一可用资格和未确认提示，保留原始缓存与数值入口原错误；新合法观察应能完整恢复。
2. 公共数值路径`calculate_damage→prepare_run→resolve_enemy`仅用相等匹配引用等级，布尔False/True可与固定整数0/1同等匹配。原`enemy_preview`虽有早期相等筛选，但后续`enemy_skill_reference`已经明确拒绝bool和所有非int，所以不能把预览说成也接受bool或重复修它。数值接口历史float0.0/1.0的接受语义必须保持，不扩大成全局strictint。
3. 已接受缓存的正常难度记录中，显式非文本`source`不会影响数值准备资格，但`reporting.build_report`直接字符串加source可产生TypeError。只在真正格式化消费门标明未知来源，不能将None/list/int/map/bool转成已确认来源，不能丢掉原记录或改数值。

这些是Source候选而非真实复现结论。原有技能/藏品/环境数值不改变；无新的原生时钟或召唤物机制依据。本小节不得销掉PROJECT_PROGRESS里的三大P2机制未知项。

## 冻结的公开输入与调用范围

22个缓存：8个模式资格/alias对照，8个来源metadata对照，6个难度value类型/合法0控制。11个直接目标：引用等级0/1的bool、int、历史float；已拒绝的文本/null/list；顶层False/空对象仍是不启用固定目标的旧安全语义。

所有缓存JSON显式含mandatory `operators:{},relics:{}`和同局ID、时间，不因缺容器而提前被98guard拦下。文件在`fixtures/`，原件字节/hash在manifest。直接数值情景使用机械师S3、精二90/专三/10秒窗口、声明冲锋0，没有藏品、酒类相位或未知命中计数。数据档案中的两个精确固定目标为ro6_n_1_2/enemy_1093_ccsbr/0和ro6_n_3_1/enemy_2001_duckmi/1。只以已存公开数据作原接口观察，不声称实际出怪。

直接`calculate_damage`及真正`enemy_preview`各自保留完整native结果/trace。缓存每阶段调用真实RunState.summary、recognition_context、confirmed_config、difficulty_value、calculate_damage。纯消费前后按同一native图比较caller/state和run.json/既有.tmp完整bytes。合法fresh `operators:[],config.difficulty.value:2,source:public-fresh-normal-label`另分实际apply/save phase；随后读取实际保存JSON图并真实RunState重载，不把跨JSON的内存alias丢失当产品问题。重载再次观察复用和数值入口。没有ScreenReader/OCR调用，没有MainWindow或第二窗口重开。

`observation_complete:true`只说明全部预定观察结束；`product_pass`恒为false。预期产品异常均保留真实trace，不能因外层脚本raw0改称产品通过。基础设施问题会终止脚本并封存fatal_probe_error，不按新的产品缺陷统计。

## Root执行与审计

独立Source审阅后，Root用实际final105的Source guard和已有真实Linuxvenv运行；105的Runtime全量结果单列：

```
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python /workspace/.continuation/section106-environment-original-probe-source-v1/probe_environment106.py --root /workspace/rougezhushou --guard /workspace/.continuation/full105-source-suite-guard-v1.json --out <FRESH_ROOT_OBSERVATION_DIRECTORY>
```

参数中的占位路径尚未绑定/执行，不是已验证命令。Root保留真正stdout/stderr/原始结束码、observations.json、public-state原件/已保存新JSON、全部native压缩原件。Source与CORE执行前/最后逐hash守护；每次native保存sequence从1开始，120秒deadline只保护本脚本自身，不杀其他会话或Wine。

数值例外和控件实际表现必须分开：本Linuxprobe不能证明Qt findData/currentIndex/disable或tooltip实际行为；候选未来需要真正隔离MainWindow流程、同条件健康Gold、当前完整native数值及三全文、保原disk、合法观察后close/RunState重载、4实际PNG。Root是唯一执行者和Git操作者。

## 不扩大的边界

不改effect_verified的既有strict数值合同，103保存/复用未知flag的原合同保持。不新增对squad.level、未知来源是否自然生成、正常mode历史float、任意Python对象的schema。NORMAL0–15与MONTH_TEAM原记录分开来自既有p2-run-eligibility固定原表历史回执；没有在本包重新下载原表。当前character/skill原表仅只读重哈希，hash与固定a550f5e证据一致，不作为新隐藏脚本。
