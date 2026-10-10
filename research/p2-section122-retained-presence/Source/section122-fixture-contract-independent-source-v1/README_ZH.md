# 第 122 节持有栏输入分类修正独立 Source 审阅

第 122 节首轮失败源于作者的公开测试包：held_bar.relics.ids 同时列了两件藏品和一件战术道具，而 tactical_tools.ids 又正确列了同一道具。真实视觉/OCR producer 明确分流两个 ID 列表，只让图标和总数覆盖完整三件持有栏；既有完整用例也采用此契约。RunState.apply 信任已分流列表，把错误工具再写入 state.relics，之后 app 的 summary 按合法藏品目录读取就会 KeyError。用 summary.get 或跳过检查会保留重复分类和错误库存数，不能作为修复。

原作者只封存输入和绑定修正，我独立全文读原 GUI/Saved 并核 v2：窗口 writer 全字节保持 38509 B /83e96…；cases 全部数据仅移除一次 held_bar.relics.ids 的工具元素，3图标、count3、tool.ids 和所有 expected/原型/顺序不动。Saved 只改 CASES_SHA 与 WINDOW_MANIFEST_SHA 两常量；归一化两 pin 后整个 AST 与旧版完全相同，所有函数和断言不变。两封包的18 payload与MF全部bytes/hash一致，10个变更payload逐块正反向全字节重建原版；新 GUI MF、cases、helper、runner 和 README 全部精确绑定。

42完整状态、13精确更新区间、6次真实关闭和从JSON独立推导的双重重载、2幅有界PNG，全 caller/result/context/三报告跨图 alias、所有普通控件纯度、typed/native/hash/CORE/Source/时限/fsync门禁均保持。没有以 case/phase 名字放宽状态改写，也没有删除 expected 或缩小验证范围。

旧封包、旧审阅及实际首轮失败证据原样保留；此前 Source 审阅漏判分类，需要明确纠正。该改动属于测试输入修正，未修改产品，不能算新的产品功能。仅读取 Root 允许的普通 failure 字段与 checkpoint 元数据；没有读取 native/gzip/PNG，也没有执行/import 项目/API/tests/helper/Qt/Wine/Git。未发现此最小修正版新增可达 Source blocker，但这不是 Runtime PASS。Root 必须用 fresh Source/CORE绑定完成第二轮真实窗口、Saved v2，并独立查看两张原图；本批终点仍为第125节。
