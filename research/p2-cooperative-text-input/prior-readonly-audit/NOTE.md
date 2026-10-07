# 第69节只读审计：协同覆盖不能由文本truthiness确认

固定代码为已提交63 `0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb` 的独立gitarchive，排除根代理当时64修改。697个源/JSON哈希末尾重查无漂移；此目录没有patch、production edit或新机制。最终修复获授权后将另用已提交64基线，不把此63审计当64集成证明。

public operator `silverash` 对应凛御银灰 `char_1045_svash2`。重新核验固定game commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 的character/skill原表SHA。关键S3 selector `character_table.char_1045_svash2.skills[2]` 明确unlock PHASE_2/level1、skill `skchr_svash2_3` 并override `token_10057_svash2_eagle3`；该token的skills[2]→`sktok_svash2_3`。并非仅从己身S3黑板或相邻天赋猜协同。

原token S3描述：“变革已至”技能期间首个干员部署时，风雪之眼会部署至该干员所在位置并与凛御银灰同时进行范围直线攻击，技能期间可再次部署改变位置并返还费用。10对own/token等级原记录和9个培养选天赋控制完整保存在source-receipt。命名天赋只支持现有初始SP/再部署/防御/生命回复引用，不是协同checkbox的类型合同。隐藏cnt/weak[limit]、部署说明和黑板参数均不证明实际覆盖人数、站位、快照、事件ownership、首伤时钟或倍率叠加。

实际公开路径是 calculate_damage→_prepare_damage资格检查→legacy _skill_damage_base silver S3；该branch以scenario.get(cooperative) truthiness复制现有component为“协同丹增”，build_estimate用同callback重算cast/window/cycle，report也沿exact owner/skill truthiness显示召唤分项。Qt MainWindow.cooperative 是“协同攻击持续覆盖同一目标”复选框，实际serializer isChecked输出bool，源码没有文本parser。本审计未执行新的Qt/Wine。

1932次公开调用保存完整JSON或错误类型/原文（1896成功、36原培养资格错误），1884次严格whole-outcome控制比较通过。两mode默认base1000/10秒：False窗口16000；非空文本false/unknown/0与True的整份输出完全相同，变为32000并产生协同分项。这里只证明输入进入既有局外持续覆盖假设，不能证明游戏实际伤害。空文本与False相同，但仍不是明确boolean覆盖声明。

保留观察到的旧bool/numeric0/1/null和其它nontext truthiness兼容性，没有宣称它们均为官方API合法域。S1/S2及其余86个owner/skill ×两mode的字段变体保持整份省略输出；E0/E1 S3保留早先培养资格错误；零窗口/目标life0/空targets/短窗口/脆弱/外部伤害修饰/酒类和限时攻速均按本mode老scope保持。其它owner已有堕梦、破屏、四岁unknown clock场景与省略cooperative完整相同。未知字段仍未知。

67项相关既有tests全通过。复用64 source receipt和62旧合同审计，并重新按本cooperative精确token路径核验；不把64脆弱来源当协同实际时钟证明。既有公开测试只使用真实checkbox bool；62旧cooperative active text兼容曾作为其它修复保留范围，不能在本后续字段修复时成为阻碍旧误确认的永恒合同。

建议只在合法银灰S3资格通过之后，且在64 fragile文本guard之后，拒绝cooperative raw str，不猜false/unknown的语义。所有nontext、数值/clock/phase/scope保持。未经根代理单独授权前本审计不写patch。真实Windows/游戏native和实际Qt/Wine未在本审计验证。
