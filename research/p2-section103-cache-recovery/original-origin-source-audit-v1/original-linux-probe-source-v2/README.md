# 原743来源证据叶子：Root-only 原实现观察探针 v2

本稿只compile文本；作者没有执行项目、native helper/codec、Qt、tests、Wine或Git，没有修改tracked文件。产品候选仍未准备。旧v1编号0不满足可信native helper的正数协议，Root未执行，原稿保留为Source失败，不能计产品问题。v2只有len(native_rows)+1这一处更正，全部14公开fixtures和helper原pin不变。

独立Source审阅结论到位后由Root运行；完整公开fixture、同条件健康对照/unused/stale/legacyGold控制见上级audit-origin-provenance.json及SOURCE_SCOPE_AND_REPRODUCTION.md。Root必须保留真实primary exit/log，不将observation_complete/0或product_pass=False当作产品通过。

```
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python /workspace/.continuation/section103-nested-consumer-source-audit-v1/original-linux-probe-source-v2/probe103.py --root /workspace/rougezhushou --guard /workspace/.continuation/full100-completed-source-guard-v1.json --fixtures /workspace/.continuation/section103-nested-consumer-source-audit-v1/fixtures --out FRESH_OUT
```

--out必须是新的仓库外路径。guard绑定当前原743维护Source map、RunState1b6f及CORE a75d，执行前后不可漂移；冻结100期间这个probe只加载freshout下公开文件，不写repo。public-state每case独立run.json和预存.tmp哨兵，deadline120s。实际RunState构造、summary、apply、restart的原生输入/状态/字节/路径flags保留native记录和异常trace；apply(True)明确是合法观察/保存phase，不能误写成原盘不变。Caller输入必须逐原生等同；本次成功freshmarker可能覆盖旧source叶子，原观察失败不能因此被忽略。

后续若决定第103节修复，必须在Root真实复现后，再绑定实际已完成第102节基线；不能把这份原743 probe直接当候选实现验收。分队reuse/resource其他Source候选的独立文档另留，本probe没有声称覆盖这些路径。
