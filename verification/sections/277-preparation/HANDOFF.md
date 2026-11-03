# 277 独立必要验收终态

独立测试文件为 `test_skill_sp_cost_independent.py`，最终SHA `51b62a097ad722bf73278cceaa322add4c7a4d579f905e8d0e292705448ce3a4`。全部48方法实际通过，退出0；严格EPS/Int32极值/负成本/MIN64 Abs的字面量来自原signed整数规则，没有复制核心计算代码或产生当前输出golden。候选core始终为 `08c31e5c7d3b5ee58d4e64eb310e1618420157d9414fd6594ee883c08f02f502`，没有为测试修改。

终态原stdout/stderr、真实exit、测试/core字节副本、前后SHA在 `final-portable-48/`。更早的 `schema-corrected-48/` 为同一核心的嵌套结构更正后回执；最后一次仅增加可迁移入口定位，48方法未删。

首45方法实际3fail+1error，是独立测试过早假定NEG前缀字典包含ctor字段，未发现公式/分支问题。原第一次工具输出未保存为文件；`first-unchanged-replay/` 保存的是真实同源重放完整失败日志，不能冒称原第一次raw。详见 `FIRST_FAILURE_CLASSIFICATION.json`，原源件与错误断言完整保留。后续精确拆开前缀与ctor资格，所有原数值断言仍在，另加136-byte opaque copy/未知NewSp路径/身份label未知独立验收。

无需公共data注入。测试拒绝额外data/alive/maxChargeTime，独立SP-owner、NewSp-owner与Apply receiver，不借state写值代替getter，不从正常/Apply true推已付款、实际SP或施放成功。normal/value未知的未来called=null，已证早退/失败的called=false。

根代理可将同字节测试提升到 `tests/test_skill_sp_cost_independent_277.py` 并登记维护选择器。入口通过真实 `rouge/app.py` 找项目根，生产模块存在时默认读 `rouge/skill_sp_cost_reference.py`，否则仅fallback到候选cache；也可显式选择文件。独立运行命令：

```powershell
.venv\Scripts\python.exe -X utf8 .cache/section277-independent-tests/test_skill_sp_cost_independent.py --module-file .cache/section277-draft/rouge/skill_sp_cost_reference.py
```

提升后需由根代理在真实集成源执行必要验收并普通提交/推送。这里的cache通过并不等于277功能、实际Windows界面、当前SP/技能时钟或云端发布完成。
