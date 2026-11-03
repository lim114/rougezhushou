# 地图候选已停止：首轮拟合未过门

本目录的regular地面投影原生脚本仅为缓存草案，从未执行Qt、测试、GUI或游戏/聊天。没有提升canonical、没有绑定acceptedlist、没有形成新的产品功能或验收通过。

根代理首轮拟合原件：

- .cache/p3-297-ground-candidate-revision2/research/p3-map-ground-challenges-297/initial-fit-results.json
- SHA256：a76a1d3dc60a0b7a232b0f1d2886890f06248e3ffde03f4662ca20dde3425d92
- ro6_c_2：17个独立holdout，最大源像素误差5.251894793993438，accepted=false。
- ro6_c_4：16个独立holdout，最大源像素误差8.931892780491939，accepted=false。

本代理只读取上述实际原件及其结果，没有另行拟合、调点、平均、改动4源像素门或晋升任何矩阵。两组均不满足既有4像素门，故停止此线；production/data和旧12/24、direct10/18/58均未由本代理修改。

原脚本SHA5b0d2cb0285ffc91650a950e0419ef38236054f45b5033bfc3bdfe97a31aa8dd及合同保留；原READY保存为READY-before-map-gate-failure.json，原来的静态语法检查不等于拟合接受或产品通过。新的READY只记录STOPPED，不允许运行/宣称PASS。

恢复条件：取得新的独立来源或对地图地面建模有实质依据后，由根代理重新定义范围并保留本次全部失败前件；不在看过误差后静默调同批读数或放宽门。297改为另有证的“未涉足之树派出/归来结果”，应另建原生候选，不复用本目录为完成证明。
