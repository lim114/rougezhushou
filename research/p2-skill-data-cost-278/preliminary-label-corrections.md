# 278准备阶段原说明与修证并存

此文件保留准备阶段的错误标签，不把新核验结果覆写成从未出错。277正式公开core、证明与界面没有使用这两条错误标签；278仍未正式启动或计数。

## 原口头准备说明（未充分核验、现已撤销）

1. 初次给root的文字称UnitDataFlowConfig+Delta“仅blackboard+abilityData”。
2. 同一初次说明称SpData.Init没有对应mask bit时数组fallback“或0”。

这两条都不应在核metadata/原RIP之前作为源结论发出，现明确撤销。

## 具体修证与未受影响范围

1. 新鲜global-metadata中type11464、field87773是blackboard:Torappu.Blackboard，field87774是rangeId:System.String；boxed offsets16/24、native value参数实际槽+0/+8。方法72708 `_ApplyModifierToData` 第二参数rangeId:System.String。完整原方法body在277 source proof；对+8的检查和out引用赋值应解释为rangeId，不是abilityData。278 targeted-type-metadata-278.json保留真实类型行。
2. SpData.Init32852在0x18252b426读取RIP Single常量至xmm8；原8bytes是0000803f00000000，即1.0。无bit分支0x18252b4ab `movaps xmm0,xmm8`，随后写数组。因此该分支默认1.0。有bit时独立24bytes protected increment复制/解码；不能用1.0推该渠道启用。

SpType enum仅NONE0/TIME1/ATTACK2/DAMAGE4/ATTACK_OR_DAMAGE6/ALL7；循环slot3的bit8没有命名enum。保留slot编号3，不能发明职业/渠道标签。

后续合同必须以实际source门/metadata/byte spans为依据；未核数值资格、热修复、实际BB/派生实例和完整周期保持unknown。成本Round helper尚在独立native封存阶段；不得提前宣称它的metadata名称就是Mathf.RoundToInt（Unity module真实方法地址另为0x186b4c250）。

这些前件标签没有进入277功能08c31e5c核心、196相关验证或实际窗口的解释；root已实际搜索公开277文件确认。此说明不是回滚/新功能节，准备不计278完成。
