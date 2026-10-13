# 种子培育与跨局黄色襁褓

本组新增完整来源比较：30固定零件、4文档明确黄色襁褓原ID、9原同组变体待证，共43独立引用。14零件有明确种子标志，6概念体只按中/高档类条件保留；光彩松露、笼控器2特殊来源待证，8类别不符。原legacyItems总数14，黄色明确组覆盖13；隐藏开局助力1未列入黄色来源。

黑流数据库434599的完整襁褓培育室raw明确：黄色是种子奖励且在下次探索收获，蓝色是羽蛇后续额外行动奖励的收藏品。黄色文档4原ID与固定原表明确组指针核验，猫/狗各3同名原记录，羽蛇6同名原记录都保留；羽蛇6后续支援靠原force_add_choice直接指针识别，不按后缀推断。

猫下次初始+5源石锭，狗+1希望；三头犬额外1次选择、羽蛇额外1个蓝色支援需本局至少通过2区域，不借用当前层/最高层或当前库存。常规模式限制只应用于黄色襁褓，未套到全部普通零件培育。培育完成声明不是实收；不把蓝色收藏品加给本局，实际一次消耗种子件数未知。

10项首轮Qt/模型检查全部通过，记录first-tests.txt。构建时曾有脚本路径import失败及口头计数错误导致期望黄项14失败，都已按完整原表修正；功能测试首轮10/10通过。首组原topic与零件冻结资料复用，本组只新查黑流数据库的未知黄色/蓝色来源定义。

产品转移：

- seed_cultivation_planning.py → rouge/seed_cultivation_planning.py
- seed_cultivation_view.py → rouge/seed_cultivation_view.py
- build_seed_cultivation_reference.py → scripts/build_seed_cultivation_reference.py
- test_seed_cultivation_planning.py → tests/test_seed_cultivation_planning.py
- cradle-source.wiki、seed-source-fragment.html、selected-seed-original.json、source-receipt.json、first-tests.txt、README.md → research/p3-event-continuation/seed/
- data/seed-cultivation-reference.json → rouge/data/seed-cultivation-reference.json。data另外2个文件是只读symlink，留在scratch。完整黑流数据库html/raw只是检索scratch，使用可审核培育室片段及完整网页摘要，不复制故事章节。

转移后 `scripts/build_seed_cultivation_reference.py` 会自动指向仓库，`build()`必须与JSON全等。必要检查：`QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest tests.test_seed_cultivation_planning -v`。

接口 `seed_cultivation_reference(context=None, seed_quantity=None, cultivation_completed=None, current_normal_exploration=None, next_normal_exploration=None, completed_regions=None)`；`SeedCultivationPanel.set_reference(item_id=None, context=None)`、`set_context(context)`，`originalChoiceSelected(str)`只展示后续原支援引用。root可挂秘境行商功能节点或零件目录；原选择ID信号可定位既有原记录资料，不导航或触发游戏。

本组没有改既有UI、全局索引，没有提交推送。实际成功、原变体、下一局状态、随机池与当前服务器资格始终未知；offscreen不冒充原Windows、游戏或聊天验证。
