# 旧窗口重试3失败观察更正（追加）

原sealed archive及stderr保持不变。此前“WMI/finally栈”及可能在finally遮蔽原异常的表述有误，应撤回。

实际window.py的唯一platform.platform()在1267行receipt初始化中；主try从1307行开始，finally为3506–3534行，finally没有该调用。完整stderr先记录若干1267行平台/WMI栈，最后0xc000070a栈落在1329行：QApplication、MainWindow、show、processEvents共用一行。仅据该复合行不能区分具体失败调用，也不能把较早的WMI栈直接当作最终根因。

官方将0x8007000E命名为[E_OUTOFMEMORY](https://learn.microsoft.com/en-us/windows/win32/seccrypto/common-hresult-values)，表示必要的内存分配失败；此码本身不能证明整机物理RAM耗尽。最终0xC000070A的官方名称是[STATUS_THREADPOOL_HANDLE_EXCEPTION](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55)；名称不是本次具体native根因的定位。

root另有后续内存观测，但本更正没有重新采样，也不把该时点观测冒充崩溃瞬间状态。根因仍待调查；不能据此证明或排除另一个功能问题。child3221227274/supervisor1、完整验收及typed未通过的结果不变。

对应原件SHA、精确行位和按记录顺序分组的fatal栈见correction.json，所列源行见window-line-excerpts.txt。
