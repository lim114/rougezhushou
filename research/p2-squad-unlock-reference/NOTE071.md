第 71 节：强化分队的解锁条件资料

固定公开基线为已提交 59531ff2e9475410a84ef0e60836f89793fd35a9 的 git archive，2179 个文件均有 SHA256/bytes；没有纳入 root 工作树。早先 b4428de 探索快照的元数据单独留存，实际源核验、草案及完整矩阵均使用本 59531ff 快照。

既有 research/p2-technology、p2-run-eligibility、p2-enemy-rune-selectors、p2-aglna-manual-weight 已先阅读。重新哈希的固定原 topic 为 a550f5e048bb94e7cdefc6eb97a4091f0c4c7add，17,943,244 字节，SHA256 f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86。22 个分队 composite 的全部 band/item/buffs 字段及 commonDevelopment 全数据与持久档案精确相同。独立审阅也核验了所有冻结文件与提交对象相同。

七个一级强化版本有明确原 unlockCondDesc：指挥/后勤/矛头分别激活“分裂/卵生/胎生”；文明开化/开拓者/多边贸易分别激活“顶冠/角/鳍”；特勤要求机械师提升至精英二阶段。前六项通过原 condition 文本、唯一科技名称及原科技 rawDesc 中同名分队效果提升，双向闭合至明确节点。前三项同时保留原 3/6/9 门槛 enableDesc。完整原 band/item/relic/node/gate 与精确选择器留在 source-receipt071.json；不是凭图位置推导解锁逻辑。

草案新增只读 squad_unlock_reference helper；只有已明确选择的一级强化版本才接入 run_resolution.squad_unlock_reference，报告新增一个“强化分队 · 条件资料”专节。条件/节点/门槛均为来源参考，账户解锁和条件实际激活保持 None。当前选择干员的培养不能证明账户中机械师的培养，原等级门槛不能切换分队版本、覆盖 effect_verified 或自动授权效果。明确已确认的现有本局分队属性继续按原情景计算；没有新增 buff 数学、资源、初始赠品、随机库存或账户状态写入。

新增 9 项测试通过。相关 59 项：58 通过、1 项因固定提交中没有公开 samples/native-client/run-map-empty.png 而明确跳过；初次缺该旧截图测试 fixture 的完整错误收据已留，未替换私人/当前截图、未修改旧 tracked test 或读取本局私态。该旧测试涉及自己的 TemporaryDirectory RunState，并不代表真实账户或实际本局验证。

1264 对 / 2528 次公共调用保留完整 before/after JSON 或错误：843 个已选强化版本仅增加上述一个数据块和一个报告专节，删除这两个精确新增位置后整份旧 JSON 相同；365 个基础/无分队情景整份 JSON 相同；56 个原错误类型/文本相同。所有现有数值、培养、明确确认状态、来源分辨、四岁未知周期时钟、报告原条目和输入/静态缓存隔离不变。数据包括 22 个分队版本、全部公共技能、两个时序模式、培养/模组、零窗口/敌空、独立属性、级别边界和既有错误。

剩余本局环境不据此销项：177 个已有解析 native 文本的精确 outbuff/band/commonDevelopment 搜索无命中，仅证明本次已有缓存的范围；原 details 的 15 charBuff/0 squadBuff 不能当成 57 长期科技的实际绑定。长期科技的账户状态、实际 buff 属性层/目标、模式/持久/重置，以及关卡 env_system_new/env_gbuff_new/global_buff 的目标与时钟仍未知。恢复需要精确 ID 对应的实际脚本/写入/模式绑定与授权的账户观察；不下载 native 二进制、不从 display 数字制造公式。现有直接分队属性只有已接入的矛头基础/强化两版，关卡既有 scoped enemy_attribute_mul 不重复重写。

独立补丁审阅已通过，无 blocker。独立新 127 对 / 254 次公共调用：76 项仅新增资料、34 项全 JSON 相同、17 项原错误相同；9 项新测试通过。作者全部 1264 对已保存完整 JSON/error 再次严格复比通过，未重跑作者 2528 次调用。独立 git apply 重建了三个 source 文件和一个新 test 的精确字节，其余 2177 个冻结文件在草案中不变。审阅提取器初次漏计 patch 新 test 文件已留完整错误收据并修正，非产品差异。

作者未改 root tracked 文件，未运行 Wine/GUI/原生 Windows，未读取或重置私人本局。父线程负责应用补丁、注册 tests.test_squad_unlock_reference 和本批实际控件验证。独立调用数单列，不混入作者矩阵。
