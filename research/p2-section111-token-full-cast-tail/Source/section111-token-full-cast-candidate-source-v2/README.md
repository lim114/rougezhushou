# 111 深海色触手完整施放尾弹：局部产品候选（Source）

候选只替换operator_engine.py348的一行消费：保存token_stream，再仅在frames、window缺省、not-normal的完整施放中选择emitted_times_seconds。窗口shown、normal充能期和continuous仍消费times_seconds。原事件生产、SP/时钟、目标寿命、属性与叠加不改。完整产品delta是1行变2行，不覆盖110对timing/SP的工作。

当前109已编入engine SHA f6c0a17e114435c5d9b80cabc6a38444fffce1bf21260125eb8e5e58a062f7e3；Sourcecompose/inverse精确、原/候选engine和新test均compile-only通过，未导入或执行项目/测试/native/helper。Root110结束后须对完整Source+CORE和届时cloud selector重新绑定，才能实际应用。未预填未来guard或检验PASS。

8个测试方法覆盖S1/S2完整归属与public窗口分离、0/短窗口、远期命中不进phase/cycle、目标消失、unit range exit保留已锁定弹体、normal仍截断、continuous/零delay守恒、0/1/4个声明召唤物与三模组stage/手动token属性组合。固定24/16、44/36命中数仅为明确局外输入的源算术：token1.25秒/100AS→38帧，显式前摇1/后摇0，S1名义30秒/S2名义55秒；不证明游戏真实前摇、弹道或触手在场时长。原18public场景由Root之后实际取得，不冒称已观察值。

正式登记只需向届时verify_cloud.MODULES追加tests.test_token_full_cast_tail_111一次；full_available现自动合并cloud，不能用本包覆盖110 selector或机械扩大NEW_TEST_MODULES。Root负责精确局部应用、源守恒、实际测试/原API/candidate窗口/读回、保存commit/push。

游戏触手当前热更新、实际技能回复覆盖、动作绑定、真实射弹/寿命、稳态跨轮尾弹仍未核验；本候选只闭合已有局外计算接口的完整施放归属。

V2仅修正非作者发现的一个测试预期：10秒travel下完整施放尾弹位于技能阶段结束之后、cycle结束之前，故本周期应含full total+normal，而非phase+normal。增加该例全部full尾弹位于cycle内的断言；200秒travel例仍检验不进cycle。产品两行transport不变，v1原件/错误预期保留，未实际运行。
