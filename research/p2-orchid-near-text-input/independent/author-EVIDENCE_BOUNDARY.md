# 085正式审查中的证据口径更正

本说明是新增metadata附件。冻结补丁、源码、测试、197保存记录、comparison、原NOTE及47件pending清单全字节保留，没有为了改口径重跑已成功检查。

作者197对的“typed JSON”只证明 **JSON值类型**：bool/int/float/−0.0、JSON array/object及全部编码后的值与三份报告。作者编码前没有另存native type tree，因此不以它们证明Python tuple/list等编码前容器类别逐项相同。原comparison中的“original nested containers”及NOTE的“完整typed JSON”应按此JSON边界阅读，不能扩成编码前原生容器类型的执行证明。正式独审将另用不同窄fresh输入保留native type tree，不重算作者394次matrix调用。

作者old-error矩阵与新测试中 `elite=0,skill=2,skill_rank=1`、`elite=1,skill_rank=10` 两个输入沿base工厂保留level90。这会先触发等级超范围，因此它们准确证明的是**原等级错误优先且保持**，不能把它们说成实际闭合了技能解锁/低精英专精错误顺序。两者仍是有效旧错误保持证据，24对old errors的计数不改变。正式独审另用合法level43补实际技能资格错误；其执行范围/结果以独立最终回执为准。

以上不修改产品guard。所选资格、旧错误优先的源码位置与197既有比较结果没有因此失败；其完整public/native合同仍由formal窄fresh检查验证后在最终handoff列出。作者9新+40旧测试曾通过的状态保留，只明确它们实际覆盖的范围。
