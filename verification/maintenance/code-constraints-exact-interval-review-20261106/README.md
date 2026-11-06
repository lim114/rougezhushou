# 精确区间契约整改

D114：核对bounded_calibration的面板/时刻区间及calibration_experiment的残差/交集生产链，均经_interval生成精确端点；没有需迁移的当前生产者。_bounds直接读取lower_exact/upper_exact，删除浮点端点兼容和无效默认值求值。

56项定向通过，覆盖缺精确端点暴露、显示端点不参与计算、分数运算、开闭端点、实验交集和有界比较。正常None未知区间不变。未跑全量。原生来源摘要缺口及新版测试窗口更新仍待补。
