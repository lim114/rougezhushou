#!/bin/bash
set -euo pipefail
compat_root=/workspace/.compat
export WINEPREFIX="$compat_root/wine-prefix"
export WINEARCH=win64
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
export WINEDLLOVERRIDES="ucrtbase=n,b${WINEDLLOVERRIDES:+;$WINEDLLOVERRIDES}"
export WINEDEBUG="${WINEDEBUG:--all}"
export WINESERVER="$compat_root/wine/usr/lib/wine/wineserver64"
export WINELOADER="$compat_root/wine/usr/lib/wine/wine64"
export WINEDLLPATH="$compat_root/wine/usr/lib/x86_64-linux-gnu/wine"
export LD_LIBRARY_PATH="$compat_root/wine/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$compat_root/wine/usr/lib/wine:$compat_root/wine/usr/bin:$PATH"
exec "$compat_root/wine/usr/bin/xvfb-run" -a "$WINELOADER" "$@"
