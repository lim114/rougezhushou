# PySide6-Frameless-Window

Copyright (c) 2021 zhiyiYo. LGPL-3.0. The library is kept as replaceable Python source.

Source: https://github.com/zhiyiYo/PyQt-Frameless-Window/tree/fc00919f4915c91a2b6320a8ae7eb1d977ca4f57
Branch PySide6, version0.8.2. 18 upstream source files are byte-for-byte unchanged. windows/__init__.py has one
dated local change: screen-change frame refresh adds SWP_NOACTIVATE and
SWP_NOZORDER to preserve focus and stacking. The exact source patch is retained
in research/shared-player-frame-20261101; no other upstream behavior is changed.
LICENSE contains LGPLv3; COPYING contains GPLv3 incorporated by that license.

This application uses FramelessDialog and StandardTitleBar through rouge/player_window_frame.py.
Acrylic/Mica blur, capture exclusion, WebEngine and maximize controls are not enabled.
The webengine optional module is not used by the application. This namespace-local
copy does not register a top-level qframelesswindow package.
