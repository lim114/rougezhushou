# 245全量不可用记录与公开来源恢复方案（只读审计）

当前只做元资料/公开Git历史审查，在work保存计划。未运行测试、下载原件、恢复cache、写生产、生成golden或读取私人运行状态/个人截图。260结束后由ROOT集中执行恢复/维护。缺失与失败仍均不计通过。

## 全部392条记录

保留Linux205条（163父项）和Wine187条（145父项）各自原ordinal、test、kind及reason，不能合并后当作392个不同测试。规范化83个路径/依赖组，分类如下：

| 分类 | Linux记录 | Wine记录 | 路径/依赖组 |
| --- | ---: | ---: | ---: |
| 可公开恢复原始来源 | 17 | 18 | 13 |
| 旧cache/基线，需要逐件核原件 | 23 | 23 | 20 |
| 平台依赖 | 19 | 0 | 19 |
| 私有截图或由其派生/混合的冻结夹具 | 146 | 146 | 31 |

unavailable-audit.json保存每一条记录、按路径详细方案、找到的原SHA和出处。四类是范围归并，不代表每个“公开”文件已经能按原字节取得；recoverability逐项说明可验证URL+SHA、待定位原附件、或者必须找原始历史叶文件。每条只反映245首个缺失原因，恢复后可能继续暴露其依赖。混合public/private夹具不能用public训练图代替原个人holdout。

## 先恢复确知可核原字节的公开基础

public-source-recipes.json列出138个原件完整URL/固定commit/SHA256/长度：5原始excel表、1敌人数据库、68独立完整level、64独立正/背面骨架。关卡共有105个引用，其URL去重为68，不能把去重与测试/地图覆盖率混为一谈。骨架文件名按cid-Front/Back保存，另校原Git blob；不能覆盖到同一个cid.skel或用另一面补缺。game commit为a550f5e048bb94e7cdefc6eb97a4091f0c4c7add，resource commit为d0b5af0b004b044d322397ce5ae79632b6d9fcdd。

预备脚本stage_public_originals_after260.py当前未运行。默认只打印未取得的计划；ROOT260后显式--download --stage-dir工作目录，会只将实际逐字节核对通过的原件写隔离work，验证SHA/字节/Git blob，并产生当前实际staging回执，不写真实.cache或生产。失败下载/哈希不符不当通过。ROOT独立核对后才按确切原路径恢复公开cache，再针对实际变化作必要检查。--verify-only仅检查已暂存字节。

可新派生但必须明确不是历史原件的来源索引：

- .cache/game-data/receipt.json：先核完整原表，依据catalog.source创建注明复建来源的当前source-index；不能伪造旧下载日期。
- .cache/research/battle-039/image-receipt.json：固定公开PNG已在Git，逐个验证SHA/尺寸/资源Git blob后，从原stage.image映射重建明确标注的新资产回执。原测试只比较image元资料及实际PNG字节，不能制造游戏验收。
- .cache/research/timing-048/skeleton-downloads.json：64真实骨架全部核完后派生清单；绝不重新生成生产动画或借解析结果反造原skel。

其它有公开源但还不是确知可恢复旧字节：TapTap训练附件（页面850014064758230845、源SHA00f11513…、3168×1440）、另一公开holdout页面835181757304145324、BV14aK26bEuP原帧、新约能天使旧HTML及Arknights_timer6264b020模板。公开页/视频不保证能取得当年同字节图片、JPEG编码、全页HTML或OCR回执。当前新取得资料应另封新来源；不更名为原SHA历史采样。计数训练builder还依赖两个个人negative样本，不能仅恢复public正例就称整个旧训练/holdout链闭合。

## 047源码保护具体处理

historical-047-060-source-audit.json读取公开Git历史，保存16个受保护函数AST摘要和12次后续有证变化。最早Git为0.70导入30f631f1；原.cache/batch-047-before路径无Git历史，检查现有三文件全部Git版本均没有匹配FINAL_0.46里的完整文件SHA。不能把0.70或当前文件冒充046原件。

现有guard变化集中：

- battle_preview.enemy_preview：190、203、224、226、235；全属性原字段、SP继承、构造、宝箱来源、四辅助实体。
- enemy_skills.enemy_skill_reference：203、210、224、229、233；原生构建、精确资格、资源预算及具体预制体。
- spawn_reference.movement_reference：075、227；原移速符文边界及FP写回。

test_readable_battle_047.py:17–28的原意是047展示批不改变数值/引用源码，不是禁止以后已授权且有来源的能力改动。维护不能删原guard/直接给整个函数豁免。先找原public前批文件并验FINAL_0.46 SHA；若原件无法取得，仍记录旧047原档不可用。将未改的受保护函数继续严格守住，变化函数逐个附实际commit、原始证据、适用条件、既有数值/引用字段不变及新增未知/条件行为的直接检查。可以使用明确命名的真实0.70 Git见证作新的有限基线，但不能叫它pre047、不能据此宣布原046检查通过。

## 060完整输出基线具体处理

原.cache/research/river-effects-060/integration-before.json固定SHA66e5babd5d88eeef681472958780822e6717617c1b403dbe1bdf75e1fc6e0326，路径未进本仓库Git；不能用当前calculate_damage输出重建这个oldgolden。应取原Windows保存的公开算例文件（不是私人局状态），验SHA并保留原字节；恢复后将10例每个结构差异独立列出。

已有一个确定陈旧约束：test_river_reporting_060.py:83起仍要求phantom_river total_damage=1590并删除known_subtotals，而0015c20e/BATCH_CLOUD_P2_S1_BINDING.md已按原件撤回S1首次附着/黑板刷新倍率假设，完整受影响总量必须None、法伤小计独立保留；tests/test_s1_neural_boundary.py:42–66直接覆盖这个新边界。这条应按原scenario证明其法伤小计和已证动作/半开窗口，同时要求neural实际/完整周期未知；不能要求伪确定1590，也不能凭其它新例的数值猜原scenario小计。

其余mechanist/myrtle/mantra等9例的新增字段、warning、时序/本体/召唤归属差异需绑定真实后续源变更逐叶审证；未映射差异继续失败。不整树换expected，不广泛归一化/删除报告字段，不以源码SHA变化当数值变化证明。若oldgolden原件仍不可取得，保留缺失并另作有明确源的当前行为检验，不能虚称原10例全量闭合。

## 必须保留的限制

- 19Linux导入失败为真实win32gui平台依赖，Wine真实Windows依赖已能加载；不放占位模块、不编造Windows/game/chat成功。
- 31个私有/混合截图或派生OCR/性能来源组留原机；无法从云端取得，不从其它图猜像素、改写golden、合成同局状态。
- native230原12失败（0471条、06010条、识别复用1条），245首次Linux139退出/1fail3errors、Wine3fail4errors、旧窗口failure均保留。本次审计没有宣称修好。
- 245后真实CJK字体followup可单列其来源/必要检查范围；不能追溯把原字体失败换为pass。
- 全量选择器范围362保持；恢复新原件会暴露后续缺失，不应以本83组当作整个传递依赖完整表。ROOT260后的任何维护不增加功能节数。

## 260后实际公开原件恢复（已授权执行）

ROOT260后授权下载/恢复本138项。实际6并发通过继承HTTPS代理及TLS验证，138项均首次下载验证成功；恢复后再次逐路径核SHA/字节，64骨架另核Git blob。全部114,756,561字节已恢复到确切.cache原件路径，零既有冲突。不生成任何golden/receipt基线/截图或测试期望，不改生产/全局文档。当前结果见 work/full245-public-originals-after260/restoration-receipt.json、final-cache-integrity.json、summary.json。原只读审计的“尚未恢复”是当时阶段描述。

初稿动画计划首三人6个文件使用了档案别名而非原角色ID，完整预检在任何网络/cache写入之前拒绝；first-plan和preflight-first-rejection保留，按明确metadata.id纠正后保持原URL/SHA/bytes/Git blob并完成恢复。原失败不能改称通过。
