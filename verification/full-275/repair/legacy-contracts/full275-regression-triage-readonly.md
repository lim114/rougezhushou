# 275 原全量失败合同定位（只读）

没有修改 production/tests，没有读取私人运行状态、操作游戏或发送聊天。新文件均只写入本轮 `.cache`。

## 047 历史 AST

当前 Windows 本机 pre047 三份原件现在**全部存在且精确匹配原 SHA**，不能再引用 full261 当时 Linux 的“未迁移/缺件”作为本机不可用的理由。

原 `test_numerical_and_reference_functions_are_identical_to_public_backup` 是 0.47 实现边界的16函数 AST 防改测试；后来190/203/224/226/235以及203/210/229/233、075/227已按来源合法扩展三函数。证据为 `research/presentation-source-guard/source-manifest.json` 的完整提交/section receipt/AST SHA 链。当前全部16函数逐项匹配已批准的真实公开原件，没有当前版本未知 AST 漂移。

已实际执行原方法的完整16函数 AST检查：原 method 未改，只把模块 ROOT 指到独立复制的精确 pre047 和真实 public post047 文件；另外原四项 current_guard + 三项 current_successor 一并执行。8个 unittest 方法、0失败、0错误，真实退出0。工具为 `.cache/full275-historical047-contract-replay.py`，原始日志/回执与复制的六份公开源件在 `.cache/full275-historical047-contract-replay/`。这是原 AST 历史合同的恢复和当前同目的保护，**不是完整0.47历史验收**。

推荐修复：保留原方法以及原失败回执，明确让它验历史 pre047→post047 精确边界；当前16函数仍由已有 current_guard 守护，不比较当前235源码和pre047相等、不生成当前golden、不把已找到的原件标“缺失”。可在方法内显式选择真实公开 post047 路径且检查双方 SHA，或者受控runner隔离ROOT；不能用旧.source缓存替代批准改动。

## 060 历史算例

本机 `integration-before.json` 的 SHA 现已精确命中 `66e5babd5d88eeef681472958780822e6717617c1b403dbe1bdf75e1fc6e0326`。只验证了其存在/SHA/10 case名；没有执行060历史版本。

full261 `verification/full-261/repair/legacy-current/README.md` 和 source-and-case-map 记录的原11失败及13项060继任校验仍有效，但“原件未取得”只是那一次环境事实。本轮不得用它把当前十个旧失败转成缺件。应在匹配 FINAL0.60/原0.70时间修正边界的隔离真实源版本恢复原十类验收，并保留当前 successor；不要把旧1590当成当前完整total或广泛删字段归一化。

## 048/049 失败投影

两条失败断言把“失败的全平面拟合不得使用”变成“以后这个stage不得有任何合法映射”。后续230 `ff302469`、232 `6f94c63d`、242 `a14f25ac` 已加入独立双读的稀疏名义地面中心，模式是 `FixedLandmarkReference.direct_verified_centers`，没有matrix/inverse/连线/未注册格外推。

只读六探针对照中原平面绑定全部仍不存在；屏蔽 `rouge.fixed_landmark_mapping.direct_reference_for` 时六个 `projection_for` 全部仍None，原4px拒绝门未放宽。仅048的 `ro6_n_2_4` 新合法8点，以及049的 `ro6_n_3_3` 新合法7点返回直接参考；其它四stage仍None。

精确新来源：

* ro6_n_2_4：`research/p3-map-direct-continuation/source-receipt.json`，固定原bitmap SHA632a437d…644ee1 /level SHA c9ac2c40…84ee0；对应 `scripts/extend_map_direct_continuation.py` 和 `tests/test_map_direct_continuation.py`。
* ro6_n_3_3：`research/p3-direct-ground-expanded/source-receipt.json`、 `scripts/extend_direct_landmark_references.py`、 `tests/test_direct_landmark_extension.py`。

推荐修复：保持读取所有原失败probe、accepted=False、原最大误差>4、原文件SHA和原其余断言；把“原失败plane不进入runtime”的None断言限定为regular-plane路径（显式屏蔽独立直接点fallback，且核对stage不在regular data绑定）。同时实际fallback若存在，应明确验证FixedLandmarkReference、不支持segment、逆映射None；不要改生产映射或旧probe/原坐标去凑通过。已有直接点测试保留完整源字节/4px独立一致/未注册格/错SHA/Qt点击验收。

## 047 地图报告

270的新用户范围明确不需要推荐/排序/比较/自动路线，默认 `format_node` 正确改为相邻节点位置资料；旧“不是从当前位置出发”属于只显式历史诊断中的起点最短路径文案。270 section receipt与commit `af9ec5cb` 证明其获授权的范围变更。

只读同一graph/input结果：默认已含“模板相邻节点”和“实际通行状态未核验，不自动选路”；显式 `include_historical_route_diagnostics=True` 完整保留“不是从当前位置出发”原断言文本，默认不存在此句。

推荐修复：原test的候选/无概率/上限未知断言仍对默认报告；在默认报告加入adjacency/noauto边界，对显式history report保留原路线句断言。不要把路线文案恢复到默认产品，更不能取消该原断言。

## 实际探针回执

`.cache/full275-regression-triage-readonly.json` 含所有 SHA、6原probe、regular/direct返回类型、两套节点完整文本和16当前AST逐项校核。该工具 `.cache/full275-regression-triage-readonly.py` 真实运行退出0，全部 source-only，没有启动Qt窗口或读取本局记忆。
