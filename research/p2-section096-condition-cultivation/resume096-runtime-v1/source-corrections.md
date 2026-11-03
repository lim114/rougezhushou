# 第96节真实窗口计划的源码纠正

旧 plan.json 保持原始字节（SHA 55eab397b5bc908263d073318e610c7e23ddd33116759935b31e302144dc20fc），全部 146 编号步骤与 144 次手动按钮请求保留。此文件仅解释新 runner Source，未执行窗口或项目。

旧 0-based step 142（1-based 143、placeholder/overview）要求空总览自然早返，与此前 priority/sparse-run 的真实源码行为冲突：RunState.apply 把苏苏洛置 present=True；MainWindow.recruited_operator_ids 保留她；BranchChoice.entries(__overview__) 因而包含她。新 runner 在这一原步骤核验真实已招募总览仍选择苏苏洛、保持原数值结果。当前选择未变，BranchChoice 默认 notify_unchanged=False，所以这一自动动作不额外发计算回调；实际手动按钮仍运行并与 gold 完整对照。原 planned 对象包括历史错误 expected 一字未改，receipt 明列纠正。

真正的空总览早返在第一个 fresh-window 的空公开 run 中覆盖：在安装普通观察信号之前真实切换空总览，核验 owner=None、result=None、原全文提示、真实 MainWindow.calculate 进入且没有数值 API 进入，再真实恢复最初的干员并核验计算回调。额外构造探针的完整 native/UI/全文、调用、状态前后均另行保存与 gold 比较，不新增编号步骤或手动按钮，不重置/改写 RunState、不伪造结果。

另一个旧模板问题是构造后没选伤害页，却断言来源 QLabel.isVisible。新 runner 在 gold/candidate 两侧统一真实选伤害页、以实际可见行/tooltip 验证即时更新；四张候选 PNG 来自黍声明、水月模组、苏苏洛账号模组参考、回到本局基础来源。Root 必须实际查看。

新版仅包装明确真实 calculate_damage/_prepare_damage/MainWindow.calculate/AccountCache.observe/RunState.apply 与 formatter，没有全包 profile/trace；完整 caller-return 图谱、类型、容器别名、浮点比特及三份全文保存 pickle protocol 4 + gzip，Source 运行前后守卫完整 rouge 文件集合。每步成功前缀单独落盘，JSON进度逐步刷新；失败保留未完成 graph。600 秒线程 watchdog 对持 GIL 原生挂起不承诺独立硬限，Root 使用外层 timeout --signal=TERM --kill-after=30s 650s 并保存真实结束状态。硬终止只能承诺已写前缀与当前步骤记录，不伪称未返回调用完整。
