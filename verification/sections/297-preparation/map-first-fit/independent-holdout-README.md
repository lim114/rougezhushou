# 第297节独立地面中心观测

本目录仅供独立验收 holdout，不是地图拟合输入或生产数据。

- 读取对象：`rouge.battle_preview.battle_data()` 原 map、tiles、固定来源元数据，以及 `rouge/data/battle-maps/ro6_c_2.png` 与 `ro6_c_4.png`。
- 两张图均实际使用 view_image original 查看；`*-nearest3.png` 只是 PIL NEAREST 三倍原样放大辅助图。没有画假游戏图，没有改原 PNG。
- 最终读数写于 observations.json。row/col 是 0-based 的 map[row][col]，row0 为图上方、col0 为左侧；pixel 是原始 512×286 图的整数 (x,y)，不是放大后的坐标。source_level_row 单独保存原关卡方向的行号。
- 全部接受点均由原 map/tiles 验证为 tile_road / LOWLAND，只读清晰木板地面近似中心；排除高台顶面、石块遮挡、出生/终点入口顶和脚点；拒绝理由单列。
- ro6_c_2：17 点，跨4行、9列。ro6_c_4：16 点，跨4行、8列。
- 各点按可见木路格逐一读取；没有运行 fit，没有看候选拟合、矩阵、投影结果、其他代理点或本目录以外的缓存，未按拟合调点或平均。点在任何拟合比较之前冻结。
- 这只是近似图像读数，不证明真实游戏位置、操作精度、人类或绝对精度。木板纹理/边线及低分辨率存在视觉不确定性，未建立实测误差上界。
- 此次只写当前缓存目录，没有改生产文件、Git、私人运行状态，没有启动 Qt、游戏或聊天，没有跑测试或做生产集成。

原图 SHA256、网格与其 SHA256、level_source URL/SHA256、资源提交都在 observations.json；原图实际哈希已与 battle_data 元数据核对。sourcelevels 只引用现有固定元数据，未重新下载。
