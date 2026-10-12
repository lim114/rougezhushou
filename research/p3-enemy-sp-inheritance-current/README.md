# 敌人SP整记录继承与条件初始化：公开原生证明

本附件补充第203候选的证据，不单独增加功能节。`native-proof.json` 保存10个选定方法完整直接CFG、全部863条物理指令字节/文件偏移/分支/pdata、来源哈希与未解析的间接调用。`selected-metadata.json` 保存6个必要字段布局及方法身份的原始字节绑定；没有复制DLL、完整metadata、进程数据或私人状态。

提交后在仓库根目录执行公开附件/运行契约的一致性检查：

```text
python research/p3-enemy-sp-inheritance-current/verify_evidence.py
```

这个模式只核对附件、计数、方法哈希、选定字段绑定与运行契约，明确输出 `native_static_file_comparison=not_requested`。云端没有安装原件时不能宣称本机逐字节回验或运行验收成功。

在持有相同原件的本机独立回验全部863指令与选定metadata/字段偏移字节：

```text
python research/p3-enemy-sp-inheritance-current/verify_evidence.py --game-dir <Arknights安装目录>
```

脚本只读取 `GameAssembly.dll` 和 `Arknights_Data/il2cpp_data/Metadata/global-metadata.dat`。必须先匹配两个完整SHA，随后逐文件偏移对比指令与字段绑定。不同SHA会失败，不能套用此基线。可通过 `--contract` 显式指定待集成契约，通过 `--output` 保存自己的复核回执。

物理回验是字节和关联检查，不自动证明业务语义；业务核对的明确地址见receipt。精确等级缺失返回null；null SP不写入，非null整记录替换；默认/显式初始化限对应热更新钩子未接管的分支。真实控制器、首次发动、完整回转、技能数组/天赋/黑板合并及关卡别名构建仍未知。当前92字节typeDef新增的offset64字段不推业务含义。

敌人参数沿用固定公开 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 数据，与编译基包是两个具名版本；当前服务器/Lua等同、实机面板和游戏动作未验证。原始培养字段只在显式技术/来源查询展示，普通预测保留有效完整量未知的边界。
