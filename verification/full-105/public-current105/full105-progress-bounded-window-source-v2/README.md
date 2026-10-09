# 第105节新全量尝试2 · 部分进度存档与1200秒预算Source v2

这是Root新授权的仓库外验证脚本准备。作者仅运行自己的标准库Source transport/AST/hash/compile builder，未执行window/supervisor、项目、helper/native codec、Qt、Wine、测试或Git，tracked写入0。代码需非作者Source独审后由Root实际执行，不计第105节通过。

## 实际失败历史与本次目的

Root已报告新105尝试1：GUI执行99581实际primary124，独立监督器child -9、timed_out、600.146秒。仅形成movement、medical、sown三PNG，没有最终52场景archive/完整receipt。stderr只有X connection killed信息；未确认原assert失败，也未定位sown之后为何未在预算内结束，不能凭Source猜慢因。监督器确认no-live-owned-execution，但absence/reaping不成立，因为仍有已终止Z条目133362/133365；这不是活执行，也不能说尸体已回收。

保留原`full105-window-actual-v1`、`full105-window-supervisor-v1.json`及.primary-v1原件，绝不覆盖。这里是该新105的第二次实际尝试Source，不是旧095再次尝试，也不是把第一次改名为成功。

本次仅做两项Root授权验证流程调整：child和独立supervisor实际预算600→1200；在未改原功能流程的前提下，初始化进度0并每累计32条checks.append保存一次简短已追加检查进度。没有减少case/矩阵、拆开跳过失败组、改变Gold或提前宣布检查通过。

## 冻结基线与生成代码

基线`full105-bounded-window-source-v1/window.py`：661258字节，SHA256 `98e6cef848ffea73d36f330edb071e28cc884e676838a876a76995d28ea821a5`。

基线`supervisor100-preserved.py`：8964字节，`d8db890b33aad0531779aa0a1892b281cb826286193c4c5ac548b3e8210f45ab`，此前与实际full100监督器逐字节相同。本次保留它的真实process group闭合和Z/live区分，不能继续用旧600秒监督器启动新的1200秒child。

新window.py：663293字节，SHA256 `0004f90b316ec6bc576ac893ce67f52e09e9db4508edd8708f431676b36695a1`。

新supervisor105.py：9034字节，`477cf622f56e77a87850790f99c37dbdef3d6466b74697e9783417e83cf3efc3`。

`exact-local-transports.json`列出八处window局部before/after和三处supervisor改动；forward唯一，按逆序inverse精确恢复基线全部bytes。`window-source.diff`/`supervisor-source.diff`没有输出巨型原literal数据。builder仅读Source、生成新off-repo文件及内存compile，不import/exec生成代码。

## 原验收主体严格保留

作者e1cc82/0标准库检查确认原全部831个assert AST及順序同；整个顶层functional Try的body/handlers/finally完整AST仍为 `dd4b5c7ccc7771e1c95d069842eb8d051444b3fc53a9d7a6ca4de8c9014faf5c`。41个原top-level helpers不变；仅_deadline_check100和_hard_timeout100的预算与尝试label改变。新增_write_progress105和_ProgressChecks105在原Try之外，checks初始化替换也在Try之外。

所有原循环、输入场景、Golden literals、52状态输出、全部数值/可见性断言、原三全文、PNG literal名、narrow observer测量、conditional reference范围和Source guard都不动。root map仍748及真实CORE，绝不是749；106未应用。Source全遍历仍原入口/固定边界/结束检查，没有在每个append或热循环新增整仓hash。无global trace/profile或旧095完整函数vector采集。

## 小进度文件的真实范围

`checks`只从`[]`换成list子类实例；receipt['checks']仍引用同一个可追加列表对象。_ProgressChecks105.append先真正super().append(item)，原None返回保留，len/index/iteration和最终JSON数组内容保持list合同；没有替换任何产品输入、返回、state或已存检查内容。已读原Source，checks仅append、len、receipt最终JSON使用，没有exacttype(list)或native090(checks)消费者。

初始化写count0。其后仅count%32==0写 `full105-progress.json`；最多挑最后一条已追加记录的scope/section/operator/skill/pair_id五个公开字段，且只接受exactstr/int/bool/None，另存count/elapsed/attempt2。没有dump整个checks、向量、case、window、rawstate、函数调用图或重新扫描Source。一个旧检查记录可以包含多个动态assert，appended_checks是追加条数，不能冒充831静态assert已执行次数或矩阵总通过数。

每次只写自身OUT目录中的`.tmp`，stream flush/fsync后os.replace独立progress文件。该文件通常滞后不足32次成功append；如果IO/进程终止，最后一次成功原子替换是有据的较早下界，不根据elapsed猜进度。它恒passedFalse/workflow_completeFalse/complete_function_vector_measuredFalse，最终完整receipt/archive仍是原Try产生的独立验收依据。没有最后再全列表dump的checkpoint，也不承诺progress最后计数等于4283。

observer IO错误不吞、不改成功：append内错误传播到原功能Try的BaseException失败处理，Root需识别它是进度存档基础设施异常。初始化0在Try前写入，若其IO失败则原执行不会开始、raw非0，不能当产品缺陷或完成。fsync+replace支持进程被终止后的已写文件证据，不宣称跨设备断电/文件系统损坏持久化保证。没有从进度文件自动恢复Python堆或跳过已有检查；本次是完整fresh重跑。

## child与独立监督器预算

child _deadline100/_deadline_check、threading.Timer和hard-timeout/receipt全部1200。hard timeout仍只os._exit124本进程；独立Linux supervisor process.wait真正使用1200减自身已耗时，metadata同1200/after105/attempt2。二者各自真实计时起点不同，不编造同一时钟或保证哪一方先触发。

supervisor的session_members、finish_owned_session整个函数AST不变；只main预算/身份metadata变化。start_new_session、真实child_primary_exit、timeout负signal、owned group SIGKILL、bounded closure、no-live/Z/absence/reap分开和日志fsync均原样。无global wineserver kill，额外闭合最多仍原5秒/等待10秒，不是延長产品验证预算。Root必须保存独立primary/raw/status/stdout/stderr及每阶段实际结果，不能以监督器给子进程虚构0。

## Root真实执行形状与检查

Root实际guard仍`full105-source-suite-guard-v1.json`，原实际748+CORE。新OUT/status/log/primary路径必须fresh-v2，不能复用第一次路径。请Root独立确认argv实际包含新supervisor105.py与window.py，而不是复制旧600秒wrapper。

```text
<Linux Python> supervisor105.py --status <fresh-v2-supervisor.json> -- <Root reviewed isolated Wine launch argv> window.py --root <actual105 public root> --guard <actual105748/CORE guard> --out <fresh-v2-evidence out>
```

上述只是参数形状，未执行/未绑定RootWine转换或环境命令，不是新真实进程receipt。Root保存最终raw0/child0、no timeout、无live owned执行、完整4283checks与52archive+4PNG，实际打开PNG并用新runner pin独立Saved readback审计。旧saved-audit脚本若固定98e6 runnerpin必须fresh准确适配新0004f90b；不能借旧第一次或full100 PASS。

## 保留的功能覆盖限制

旧full100实际成功记录530.168秒及监督器549.828仅是基线历史，不证明本次105时长或通过。本runner继承的52旧publicGolden比较只检明确projection，旧完整full result SHA字段是历史标识，不是全旧Gold/alias证明；当前完整result/三全文原样保存供Root独立审计。5个saved public synthetic状态两视图合10次是内存consumer replay，没有new constructor/apply/reopen，也没有天然OCR producer/private replay。旧095调用vector、原生Windows、游戏capture/chat、动作/时钟/召唤物未证机制不在此验收。

106专项与96–104已有单独真实回执仍分开，本runner原scope note不改。新105完整Runtime、Saved审计、图片查看和Git发布未完成，本包仅Source准备。
