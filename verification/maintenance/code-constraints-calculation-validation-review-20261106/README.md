# 计算链重复校验整改

D102：operator_engine唯一产品调用已检查amiya_continuous_reference存在，attach_result直接读取，删除重复缺项返回。

D103：source_factor与parameter_factor各自筛选并核验来源一次，复用_verified_factor进行按藏品去重及原有乘法/加法。共享函数有两个实际调用者，不增加入口校验；单项、空项、未绑定手动输入约定不变。

32项定向通过，覆盖两入口各核验一次、独立入口拒绝未核验混合、既有藏品倍率与阿米娅有限生命周期。未跑全量，无新防御。新版测试窗口待用户关闭旧助手后更新。
