# 原230 adaptive 私样本缺口：独立只读诊断

原失败仍未关闭：两份原230回执均为 `AssertionError: 2312604 not less than 2312604`。当前原私样本不存在，未执行该旧case，未改生产、安全门、旧断言或历史回执。source-hashes.json 证明核心读取、动态OCR、PageOCR、路由、缓存、viewport、operator读取与原测试/manifest均与原230逐字节相同。

## 实际公共证据（不是原私样本替代）

probe_public_adaptive.py 使用实际 RapidOCR/ONNX、CachedOCR和ScreenReader；TracedDynamicOCR只添加调用日志并调用原实现，未使用engine double。绘制的 PUBLIC 42/93 与公开四个静态label patch均不含个人或实际干员数值。运行结果为 public-diagnostic.json/log：

- 公开数字帧第一次完整分析 2312604 pixels，改42→93后 dirty_regions 104896 pixels；当前42没有沿用，93当前像素已被读出；改变几何后完整重发现。
- 实际全帧 detector 输出 `PUBLIC93` 一行，ROI detector 输出 `PUBLIC` 和 `93` 两行，且retained文本顺序不同。诊断如实记录其差异，未把text-list相等或single-line断言当正确性。这不证明原干员数值读取有错。
- 由仓库公开、校验过hash的四个static-control patch合成完整标签排布，但不提供干员身份。默认reader第一步使用PageOCR完整DET；擦除elite控制一部分后，实际router变为 unknown_or_incomplete_controls，走 DynamicOCR full_discovery，2312604 pixels。PageOCR此前清空Dynamic前帧是该具体公共回退链的一环。
- 源图1280×703经过真实 prepare_frame 放大为2052×1127，碰巧得到与旧回执相同2312604。这个面积不能证明两者是同一截图；公开合成始终明确标记，不填入原native-client路径。

没有新公共证据证明存在可安全窄修的产品bug。当前potential缺失、控制损坏、域外变化或几何不可信时继续完整复核是现有安全策略；不为达到旧面积断言降低门槛。旧第二帧具有pixels键，能确定它进入DynamicOCR指标路径；不能仅凭这个最终面积确定为什么进入或真实provider推理成本。

另有直接partial operator字典的 specialized_observation_valid 调用，只验证门条件。它明确 counts_as_actual_ocr=false，不计真实OCR通过。source-notes.md 中引用的既有mock测试仅是源码说明；本诊断未用其冒充旧样本。

## 原样本恢复与重触发

original-retrigger.json 保存准确序列与逐帧所需字段。必须恢复真正的 samples/native-client/operator-mechanist.png，并有来源/字节hash证据；原230回执未记录该图片SHA，不能由面积或公开patch合成它。冷reader、默认参数、cv2原读法、擦除[400:590,1700:1920]、潜能缺失和时间递增、原less-than断言、之后原relocated第三步都保持原样。

重触发必须记录：输入/viewport分析几何，provider/version与PageOCR支持值，visual plan/domain/controls变更，首次operator.complete和verified identity，Dynamic先前image/domain/age/raw文本bounds，实际dirty合并面积阈值/域外变化，force_discovery和真实OCR调用形状/cache hits，当前missing_fields与完整fallback_reason。原230只留下最终面积，缺这些分支证据。

旧遮罩在公开canonical布局中可能同时伤elite control；但旧图片实际affine/viewport未恢复，故不称已确定旧实因。缺potential也可使 complete=False，继而在 legacy 专用区域路径触发语义全回退；同样需要真实旧链记录才能归因。source-notes.md 给全部准确源码条件。

Native Windows的原case恢复须有Native环境；Linux/Wine只可形成另一个标注清楚的重放。原失败回执继续保留，后续真实重触发另存结论。

## 小型安全入库清单

仅建议入库以下7项，不复制原图、模型、samples或生成PNG：

1. REPORT.md
2. source-notes.md
3. source-hashes.json
4. original-retrigger.json
5. probe_public_adaptive.py
6. public-diagnostic.json
7. public-diagnostic.log

脚本自行定位仓库根目录，使用项目Python依赖及真实 DejaVuSans-Bold 字体。例：`.venv/bin/python <归档目录>/probe_public_adaptive.py`。输出中的四个patch路径/hash指向已入库公共资产；无需提交重复patch图片。第一次探索的单行文字和源面积假设被实际结果否定，最终诊断使用真实分词和analysis_size记录，不是原230的通过回执。
