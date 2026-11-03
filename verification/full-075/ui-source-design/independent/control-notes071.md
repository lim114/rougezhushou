71 的 MainWindow 没有可供用户选择分队或强化等级的控件。`difficulty` 下拉框属于分析预设；`calculate()` 从 `window.run.state['config']` 原样取得本局配置。测试应明确写成“隔离窗口中的合成公开本局配置 + 真实计算按钮 + 真实正文”，不能称为分队控件选择、OCR 识别或账户解锁验证。

可验证的输入边界：

- 从固定 `run-config.json` 读取真实 ID、name、bandLevel、normalBandId、usage。7 个强化 ID 是 band_2、22、5、7、16、18、20，`bandLevel == 1`；另外 15 个基础版本不生成新 reference/section。不要按仅有的中文分队名称推断版本，因为同名版本共存。
- 合成记录的 `level` 应取原 `bandLevel`。报告 helper 按固定档案中 ID 的 bandLevel 选择 reference；运行中 record.level 只是现有 summary 显示来源，不能称作新资格校验。`effect_verified` 使用真实 bool，仍只确认原情景效果，不确认账户解锁或科技实际激活。
- 三个 DIFFICULTY 节点原 gate 为 3、6、9。保密等级高于/低于门槛都不得自动切换分队、改变 effect_verified 或把 activation 改成已知。其余三个 outbuff 节点没有该 gate reference；band22 仅原“机械师提升至精英二阶段”条件，不能由当前选择干员的 E2 培养推出账户条件已满足。
- `sync_run_config()` 会同步已确认 difficulty 到真实下拉框并将其禁用；无已确认记录时保持可修改预设。可核控件当前值/启用状态，但该控件并不修改 scenario.run_config 中的 squad。
- `window.run.summary()` 对 record.level==1 显示“强化”，level==0 显示“基础”，level==None 不显示阶段。此展示不证明账户解锁。

真实 Qt 结果应核对 scenario.run_config 中完整的合成记录、7 个 source reference 与唯一新增报告节，并核正文“账户解锁状态：未知”“解锁条件实际激活：未知”和原 unlockCondDesc。默认正文不得泄露 rogue_6_band / outbuff / commonDevelopment 技术 ID。已确认矛头强化的原 15% 属性与未确认时的 pending 都要保留；不能把 reference unknown 当作取消已确认效果的理由。原级别/技能资格、Shu 四岁周期 SP unknown、零观察窗口结果等不因新资料改变。

保持与已验证 070 runner 相同的隔离边界：构造窗口前将 RUN_STATE、OPERATOR_STATE、SETTINGS 和 DesktopBackend 文件路径指向 TemporaryDirectory。只注入该窗口的公开内存结构；不读取真实 run/account 文件，不调用 OCR、capture、reset 或 RunState.apply()/save() 来构造这组状态。

使用 try/finally 保存并恢复 window.run.state 的 deepcopy；如 train() 修改 operator_observations 或 use_run_training，也保存和恢复它们。恢复后更新 run_summary、sync_run_config、operator/skill 选择和必要的 relic/target 控件。若记录没有已确认 difficulty，另行恢复先前预设值；sync_run_config 不会自动恢复这一预设。每个结果都核 scenario 中 owner、skill、mode、window 与 run_config，避免旧成功结果被误用。结束时仍核 auto=False、capture.target=None、desktop.process 未启动、临时 chat 目录未生成。

依据：固定 71 draft071 的 app.py、run_config.py、run_state.py、run_modifiers.py、squad_unlock_reference.py、reporting.py；71 final patch b7003b715318a7ac8d01413aaed2fce0532cf8a57cd41182e32d2bbe8dcddff6。071 独立 source/API review 已通过。070 runner SHA 3bba0d28376165b84938906b45048f31b75d89cf6e1c4d1e5246d17f6272f9b3 的既有 841 checks / 87 skills 应保留。本 notes 仅静态设计复核，未执行 Qt/Wine，也未审查未冻结的 72–75 schema。
