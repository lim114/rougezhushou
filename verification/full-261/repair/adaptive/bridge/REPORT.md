# 第261节识别复用修复与边界

修复已应用到 `rouge/recognition.py`、`rouge/page_ocr.py`、`rouge/dynamic_ocr.py`，新增注册模块 `tests.test_page_ocr_seed_bridge`。应用后相关检查 **66 PASS、0 skip**（12项新协议边界检查及54项旧检查）。协议检查使用明确的引擎替身；真实 OCR 证据另列如下。没有改旧断言、45%面积阈值、12区阈值、8次年龄门、域外变化守卫、显式强制发现或语义资格门。

## 已实证原因与修复

原默认路径每次 PageOCR 结束后，无条件清空 DynamicOCR 的上一帧、原文本与范围；尽管 PageOCR 已对当前整图完成 DET，并按 RapidOCR 原分批/最大宽度完成所有当前文本的 REC。下一帧局部静态控件损伤使视觉候选失效时，DynamicOCR 没有基线，只能重新请求整图。这是可独立复现的当前缺陷。

现在仅当四个完整覆盖元数据都是 Python 严格 `True`，真实加载几何一致，当前像素 SHA/shape/dtype 一致，而且与 PageOCR 成功推理所持的不可共享快照逐字节相等时，才复制完整原始文本和当前图像作为 DynamicOCR 无范围基线。任何不完整/未知/错误几何/旧签名/变化像素（包括哈希碰撞）都保持原清空处理。成功移交后释放 PageOCR 快照；推理异常无完整快照。移交只保存 OCR 原文本，所有干员、图标和页面语义仍对当前图重新判断。

## 相同公开输入的真实前后复验

输入是明确标记 `PUBLIC SYNTHETIC FIXTURE` 的新公开面板，由已入库静态控件、公开潜能6图标和声明文字构成。来源/hash见 `work/adaptive-261-public-operator/fixture-manifest.json`；精确PNG与解码像素hash见 `frames.json`、`owner-sequence-frames.json`。没有写入或冒充 `samples/native-client` 原图。

真实 RapidOCR 1.4.4 / ONNX Runtime 调用均调用原方法并返回真实输出，只有形状/计数/耗时观察包装；未改变模型、provider类别、配置、输出或阈值。BEFORE保留实际原代码哈希、当前结果、raw文本、viewport、请求与推理形状，AFTER逐项与已保存的真实 fresh uncached 整图 oracle 相比。身份、scope、全部fields、skill_ranks、missing_fields、complete严格一致；序列模型字段仅作JSON键名标准化，不调值或四舍五入。

| 实际场景 | 原默认路径 | 修复后 | 结果边界 |
| --- | --- | --- | --- |
| 局部精英控件损伤 | 整图2,312,604像素，DET1/REC2 | 单区40,572像素，DET1/REC1，请求196×207 | 当前身份、潜能保留，当前selected_skill仍unknown，与fresh整图一致 |
| 只擦除潜能图标 | PageOCR当前完整DET | 同样完整DET，缺潜能 | 不把旧6当新值，不补造完整资格 |
| 域外新增 `PUBLIC OVERLAY 261` | 当前完整DET发现新文字 | 仍发现13框、其中2个guard框 | 域外文字真实返回 |
| 1800×3200位置/尺寸变化 | 整图5,760,000像素 | 整图5,760,000像素 | 完整发现与fresh结果一致 |
| Fang→Vanilla→Vanilla局部损伤 | 末帧整图2,312,604像素 | 末帧40,572像素 | 三帧均匹配独立fresh，末帧仍为当前Vanilla，无Fang串用 |

40,572/2,312,604约1.75%，是这组确定输入的请求面积，不能推广为所有画面或保证耗时比例。实际推理耗时保留于原JSON，受共享环境负载影响，仅是当次观察。完整前后工作量与模型形状见 `before-after-summary.json`，全部真实结果见 `candidate-real.json`；候选实跑前后源hash一致，正式应用保持recognition原CRLF且标准化hash严格等于实跑源，见 `production-apply-manifest.json`。应用后的66项结果/hash见 `production-unit.json`。

## 原第230节不可替代的恢复条件

`verification/full-230/native.json` 与 `native-after-repair.json` 中的 `AssertionError: 2312604 not less than 2312604` 保持不变。旧原图 `samples/native-client/operator-mechanist.png` 当前缺失；精确路径历史没有入库原图，旧回执没有原图hash，也没有路由/域/完整性/实际请求trace。其失效像素指标证明当时走过DynamicOCR指标路径，但不能从面积反推出宽高、初始完整资格或实际路由。

本次闭合的是已实证的当前全图基线丢弃缺陷；没有声称这个缺陷已证明为旧230唯一原因，没有宣称旧私图断言或真实Windows已复验通过。原掩膜 `[400:590,1700:1920]=0` 在某些公开变换下会同时损坏静态精英控件，不能预设为仅擦图标；某些路径还可能正确触发语义不完整强制整图、几何/域失效、45%/12区或年龄门。

必须恢复带真实来源的原始授权截图并保存PNG及解码像素hash，使用新的空ScreenReader，保持原掩膜及全部断言，记录首次和第二次的viewport/shape/dtype、provider资格、候选/当前域、seed覆盖绑定、route_age/retry_after、原文本框/dirty矩形/union面积、force/guard/full-seed参数、实际OCR请求/模型调用、当前fields/missing/complete和semantic重试原因，才可区分这些条件。原第三帧定位断言当时未到达，亦不可补称已通过。精确重触发字段见 `original-retrigger.json`，搜索/不可替代边界见 `native-input-recovery.json`。Linux、Wine与原生Windows的回放要分别标注。

## 复验与安全归档

生产相关检查：`.venv/bin/python work/adaptive-261-bridge/run_production_unit.py`。

同字节公开实跑：`.venv/bin/python work/adaptive-261-bridge/replay_real_frames.py production`；脚本读取封存PNG并逐hash核验、使用保存的原真实fresh oracle、不生成替代原图。候选实跑命令末参数为 `candidate`。公开原代码before已封存，当前代码重跑生成不同结果应另存，不能覆盖原before回执。

`archive-manifest.json` 提供小型允许入库清单及逐文件hash：只含公开声明输入PNG、来源/形状/hash、实际JSON/log、小型脚本与协议回执；不带private图、个人内容、OCR模型/运行时二进制、Wine prefix、候选源码重复副本、探索失败或pycache。生产4文件由root正常提交，全局进度/索引与完整回归由root负责。
