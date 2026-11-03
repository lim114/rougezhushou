# 第93节账户缓存候选 v2：同目标 attempt 2，未运行

v1 封存包、原源/设计包及正式 v1 独审回执全部保持不变。正式独审 `static-contract-review.json` SHA256 `ee0581b352cd9f9b64f5033c0fa8726b4b5e033cf8481281938bb006799cf099` 明确以 B1/B2 阻断 v1 产品运输；原37测试方法仍全部 UNRUN，原22源案例仍为 STATIC 预测。v2 不把这些材料计为运行通过或第93节完成。

本次根代理明确授权一次最小 source-only 修订。actual92 commit/tag 已只读核验：`f509d186e501bfcfd042e45b46e398ec756840ec` / `p2-section-092`，app 96320B，SHA256 `32818adf259dbb124ae86178e0ef82dcb1a316d0f7bf373e5c4b99aa5d25f9f6`，与实际 Git blob/工作树逐字节相同。reporting 98187B / `f71da63bd1e5cea78cda21139d01b206519cec82029c73937443aceb19512ba7` 同样匹配，但不属于候选 target。没有项目 import/API/helper/formatter/tests/Qt/Wine 执行、私态读取或 tracked 写入。

B1：v1 对合法500层 ignored JSON value 递归 deepcopy，引入旧 raw view / shallow producer 没有的 RecursionError 依赖。v2 删除 copy import 和所有递归拷贝。safe view 只复制顶层记录、剔除已知本局 operative metadata，再浅复制五个实际 mapping 容器；unknown extra/ignored leaf/source/time 值保持 opaque。合并仅作原有顶层/mapping union。没有新增深度限制、递归上限调整或 stack clone 算法。输入不变的合同指这些操作不修改 caller；任意深层修改返回 view 后仍与 raw 完全独立不是原合同要求，新测试不再强制这项附加保证。

B2：旧 locked/inert rank 在独立合法的新培养 context 下可能变成不安全的 active rank。v2 先保持原 good-old timestamp 比较，构造原正常 union；若该 union 不可消费，立即永久保护原盘，再用同一 producer 构造器和空 saved mapping 仅重建 incoming 合法事实及其 supplied time。旧贡献全部排除，未给 rank/培养项保持缺省未知并走既有标注预览。真正可消费的 union 不触发该分支，原 fields/ranks/sources/time 合并和 changed 保存决定保持。per-id quarantine 只由新的合法观察恢复；全局原文件保护无自动清除。

除这两点外，record validation、load/full-map screening、notice、save guard 的 AST 均与 v1 相同。app 和 selected registry 的 bytes 与 v1 完全相同；app 的 calculation、培养/rank/base、真实 RunState、浏览跟随及92条件逻辑保留实际92 AST。没有增加 whole-map rebind 产品 API；历史 GUI fixture alias/id 适配仍属 root 的外部 full095 运输。

测试草稿收窄原任意 nested view mutation 保证，并增加500层合法 opaque JSON 的迭代保真控制与 B2 新 context 恢复控制，包括 older rejection、合法 rank union 和后续合法观察。测试不以递归 deepcopy/whole deep equality 自身制造失败。运行状态、实际平台 skips 与 PASS 数必须由 root fresh 执行后填写；真实 MainWindow/Wine、genuine RunState precedence/snapshot、summary safe-view、原文件 bytes/path、timing/relic JSON 和完整原数值/错误顺序比较仍不可由静态材料替代。

这是同一新缓存目标的第二次候选尝试；失败原件和恢复条件在 failure-log093.json。若同目标三次仍未闭合，保留证据并按原工作规则 defer，不能借 source 整理或草稿创建计进度。
