# 第 67 节独立审查

结论：无未解决 blocker，最窄 metadata 修改可以集成。独立审查只使用外部精确提交 `0d446fc3523fd09452c84f65c133d23f33b31696` 的 frozen 与作者 draft；未冻结当前 root 工作区，未改 tracked 文件或作者成品。

## 来源和代码

独立重新哈希当前 character_table / skill_table 原字节，吻合固定 game-data commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 的来源回执；精确比较 3 个原 selector（酒神两个天赋候选集及 S3 rank 10），4 份既有研究回执重新核验哈希一致。堕梦两原候选均在精二 1 级开放、普通攻击损伤参数均为 70；计数仍不提供实际攻击时刻、间隔或 burst 先后。S3 每秒参数未用来填实际首跳、种子绑定或生命周期。

696 个冻结公开代码/测试/脚本文件哈希复查无漂移；patch、实际 engine 和新增测试文件哈希均与最终来源回执相等。

actual engine 的唯一改动是 metadata 中 `int(raw enemy_attack_count)` 改为 `int(self.option(..., maximum=10000, integer=True))`。将这一处转换精确换回旧文本后，整个 engine 与冻结原字节相等。实际 plan 内既有整数查询、raw bool 排除、字段上限、pending 资格门、损伤计算、SP 时钟、None、scope 和报告原代码均未改变。plan 的 parsed local 不在后续结果方法作用域，复用相同实际查询没有增加跨阶段状态或新 count-to-clock 规则。

## 独立公开验证

probe067.py 新执行 102 对输入 / 204 次公开 calculate_damage，保存完整结果与错误：18 个合法整数 decimal/exponent alias 从晚期 bare-int 错误恢复，完整结果精确等于原整数控制；70 个其他完整输出保持，14 个原错误保持，0 未解释差异。覆盖 S1/S2/S3 两模式、零文字、零窗口、目标生命 0、空敌方窗口、损伤免疫、精一无堕梦与其他干员 inactive 字段。

已直接核验：

- metadata 仍为 int 计数，70 点参数保持；events_scheduled=False、attack_times_seconds=None，不生成攻击或爆发时钟。
- 零观察窗口实际总伤 0，cast pending 与 window 非 pending 的区分保持。
- 空敌方窗口沿各模式原合同：frames 已计窗口小计 0；continuous S2/S3 原小计分别 25,000 / 40,500。没有把帧模式规则套到 continuous，也没有恢复完整实际总伤。
- 零计数、life0、免疫及未解锁天赋保留旧 source gate；inactive 字段继续忽略。
- raw bool 的原 enemy_attack_count 错误保持。S2 bait_triggers raw bool 仍先返回其原错误；精一 S3 未开放仍先返回资格错误。
- 调用者、缓存 catalog 与源码起止哈希保持。

独立执行全部 8 个新增测试方法通过；没有重复作者 89 方法的 related 全套。

另外读取作者已经保存的全部 1,620 对 before/after 完整 outcome，对 baseline 另与原只读 gzip 逐项核对。180 个合法 alias 恢复均精确等于其原整数控制；1,440 个 outcome 完全相同，其中 520 个原错误和 920 个原成功输出。全部 528 对语义 alias 的完整 outcome 相等。这里仅重新比较已完成记录，没有重新执行作者原 3,240 次调用，也不把它们计为本次 204 个新调用。

原作者 initial test 错把 continuous 空目标小计当作 frames 零值，失败版本已明确保存在 unreviewed-test-scope-v1。独立探针核验了正确的原模式边界，不删掉反例或改原数值以通过验证。

## 审查成品

- patch SHA256：`a8bae03fe3b1a7ab34da2b26fce646352c02f80decf0b4819cd2dda41407848b`
- draft engine SHA256：`3789031e1587c06a12b77b8ef353a1dd42a93eab94e96721311f44e63629c416`
- new test SHA256：`06a8e4feb86b7eb7c38dabe80367bad1ff84af754a3c97270e64c0afe17d75a4`
- source-and-saved-comparison.json：来源/冻结/旧成品全比较及准确数量。
- baseline.json、draft.json、probe-comparison.json：新独立输入、完整 outcome 和断言。
- new-tests.log：8 个新增方法通过。
- probe067.py、verify_source_and_saved067.py：独立检查脚本。

没有 Wine、GUI、原生 Windows、游戏操作或当前热更新验收。真实普通攻击时刻、同帧回调、次生首跳、附着/刷新、所有者退场及完整实际损伤仍按原边界显式未知。root 负责正式集成、runner 注册与当前分支相关/精选回归及每五节的全量和实际窗口验证。
