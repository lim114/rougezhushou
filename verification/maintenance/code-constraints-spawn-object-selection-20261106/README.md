# 维护：出怪与物件选择读取只执行一次

两面板selected在入口处理无资料后，只读一次entries.currentData，再查找匹配项。物件selected_action复用刷新/follow_action已取得的row，只读取一次动作控件；原有无参数调用保留。未新增函数或异常捕获。

计数验证每次selected控件读取1次，传入row后selected_action再次查找物件0次，与无参数结果一致。35项定向检查通过（182.417秒），覆盖两视图与共享资料页真实入口，未跑全量。自动测试含offscreen设置；本机主窗口另行重启，确认可见响应，截图已查看；未做游戏操作。原始证据仅.local/code-constraints-review-116/。

D227—D230原样登记，共193组待审。D228单次包装、D230重复预检仍待处理，current_battle_view外部调用尚有选择重复，明确不计整模块完成。覆盖47全/151部分/48仅异常/312结构不变。
