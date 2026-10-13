# Wine11.19维护环境复用

当前已验证路径：/workspace/rougezhushou/work/wine-persistence-audit/runtime11/run-python11-devel.sh

```sh
ROUGE_WINE_PYTHON_LAUNCHER=/workspace/rougezhushou/work/wine-persistence-audit/runtime11/run-python11-devel.sh bash scripts/wine_python.sh -m unittest tests.test_persistence_initial_install tests.test_run_persistence_099 tests.test_account_cache_093
```

应用产品patch前的候选验收命令：

```sh
.venv/bin/python work/wine-persistence-audit/run_candidate_tests.py candidate-linux-final
bash work/wine-persistence-audit/runtime11/run-python11-devel.sh work/wine-persistence-audit/run_candidate_tests.py candidate-wine11-final-clean
```

目标两模块+新14个行为方法共76 tests，两端0skip且exit0。当前Root应追加全量维护范围、旧窗口与当前MainWindow的同环境验收；这些尚未由本候选宣称通过。字体原例 Linux/Wine10/Wine11各1PASS/exit0。真实Windows和32bit未验收。

现有宿主Noto文件由wrapper传 Z:\usr\share\fonts\opentype\noto\NotoSansCJK-Regular.ttc；Linux全量设置 /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc。候选launcher PATH必须含 /workspace/.compat/wine/usr/bin 的真实 Xvfb。

同版运行时包、SDK原件哈希、签名来源在 runtime11/migration-manifest.json；只复制小型说明与回执入库，勿提交前缀、解包目录或deb。原Wine10和原245回执保持原样。此次先复用已验证绝对路径；若搬迁launcher/运行时/前缀，更新明确路径后重跑验收才切默认。
