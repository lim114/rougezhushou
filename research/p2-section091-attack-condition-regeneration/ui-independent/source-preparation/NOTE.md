仅静审固定提交 2cbc45f 的 app.py 与 verify_damage_ui.py Git blob，原字节和换行已保存。checkbox 默认 True；原显示条件仅 Attack；隐藏不重置 checked，calculate 无条件读取此值。baseline 尚无该 checkbox 的 toggled→calculate 连接。

现有 bool 控件先设置默认值，再连接 lambda:self.calculate。实际方法为 calculate()；早退之前仍会同步动画/目标强化，不能把早退当作任意构造阶段调用安全的证明。原 UI 校验 predicate 在 39 行，widget/label 断言在 43/45 行。所有项目调用为零。
