# 第72节：头狼培养资格与现有浮游单元参考

基线为已提交 `552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9`；121 package 和191 test 源文件从该固定 git blob 导出。root 工作树、用户 state、Wine 均未读取或修改。

原始角色表 `char_1038_whitw2.talents[0]` 的头狼四候选最早为精一1级；精一/精二和潜能6的 interval 分别为30/26/20/16。选中天赋函数已经正确过滤培养条件，但浮游参考额外单位计数只检查operator与 `time>=3*interval`，缺失天赋时仍使用20 fallback，使精零在60秒后多出一个参考单位。

最窄 patch `section72.patch` SHA256 `b92662a951f4dc66389f582c33438aa1229639e6d4b4b05bb440f9ab2d2e50eb`，6773 B，包含engine的一个选中天赋资格变量与原 ceiling/count 两个条件，以及8个新测试。保持精零S1原有被动+1，共2个技能状态参考单位；不误改为1。实际独立单元到达、索敌、命中、同目标暖机和S3光环首跳/覆盖仍未知。

完整消费者审计显示 ceiling/count 数值消费仅在engine，报告与estimate消费这些产物，未另有头狼资格派生。空switch观察原合同仍有默认30秒 canonical hit_count参考；该 metadata 同样修正资格，不生成实际观察窗口命中。

作者原始paired档案：每侧2544调用，实际2328 public calculate +216 prepared normal reference 调用；5088 paired calls。1502接受、1042错误每侧，完整结果/报告/technical report/estimate文本均保留为严格JSON gzip。normal helper是源码参考路径，不把它称为public calculate或用户私有state。共享catalog和调用参数未漂移。64相关测试执行全通过（8新+56旧），无skip。

作者汇总harness三次遇到归纳断言/输出形状错误（0攻击只改变count；空switch窗口仅canonical metadata变化；normal plan无total_damage键），已按三次规则停止该harness并保存失败说明及最后log。生产代码/新旧测试和原始输出没有失败；独立review使用自己程序审两个档案，不读取作者compare.py。

独审已报告实际结果，最终以其sealed receipt为准：独立2448 public calculate pairs，252改变/2196严格整份保持；2112精一/精二全部严格保持。336精零结果均等于同组年龄0基线，84组年龄参考不再凭空变多。作者档案独立diff156改变/2388严格保持（146 calculate、10normal），1042个错误原文/类型全部保持，所有本体分项/单次倍率/资格identity保持。

固定character/skill原始字节只重新核对hash，没有重新下载；三技能30 ranks与四天赋candidate匹配、192培养/潜能/module selection记录保存在source closure。没有新native byte、当前hotfix或实机机制验证。

最终独审sealed receipt SHA256 `d29d9cbe3b98e38fce7d3aa480618b5c0152afed71567ee15df30d1b58d54acd`，80测试方法全过、0skip；独立/作者档案实数以上均已逐receipt核对。作者harness仅保留为deferred诊断，最终结论使用独立程序；root后续fresh integration另计。
