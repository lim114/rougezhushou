#!/bin/bash
set -euo pipefail
compat_root=/workspace/.compat
python3 "$compat_root/verify-cached-inputs.py"
mkdir -p "$compat_root/wine" "$compat_root/python-windows/package" "$compat_root/windows-sdk/package"
for archive in "$compat_root"/apt/cache/archives/*.deb; do
  dpkg-deb -x "$archive" "$compat_root/wine"
done
python3 - <<'PYCODE'
import zipfile
from pathlib import Path
root=Path('/workspace/.compat')
with zipfile.ZipFile(root/'python-windows/python.3.12.10.nupkg') as z:z.extractall(root/'python-windows/package')
with zipfile.ZipFile(root/'windows-sdk/microsoft.windows.sdk.cpp.10.0.26100.4654.nupkg') as z:
    z.extract('c/Redist/10.0.26100.0/ucrt/DLLs/x64/ucrtbase.dll',root/'windows-sdk/package')
p=root/'wine/usr/lib/wine/wineserver'
s=p.read_text().replace('wineserver32=/usr/lib/wine/wineserver32','wineserver32="$(dirname "$0")/wineserver32"').replace('wineserver64=/usr/lib/wine/wineserver64','wineserver64="$(dirname "$0")/wineserver64"')
p.write_text(s)
link=root/'wine/usr/share/wine/wine'
if not link.exists():link.symlink_to('.')
link=root/'wine/usr/lib/x86_64-linux-gnu/wine/x86_64-windows/zlib1.dll'
if not link.exists():link.symlink_to(root/'wine/usr/x86_64-w64-mingw32/lib/zlib1.dll')
PYCODE
# First boot creates this isolated prefix; only Wine-managed files are used.
"$compat_root/run-wine-python.sh" -c 'import sys; print(sys.version)'
cp "$compat_root/wine/usr/x86_64-w64-mingw32/lib/zlib1.dll" "$compat_root/wine-prefix/drive_c/windows/system32/zlib1.dll"
"$compat_root/run-wine.sh" wineboot.exe -u
cp "$compat_root/windows-sdk/package/c/Redist/10.0.26100.0/ucrt/DLLs/x64/ucrtbase.dll" "$compat_root/wine-prefix/drive_c/windows/system32/ucrtbase.dll"
"$compat_root/run-wine-python.sh" -m ensurepip --default-pip
"$compat_root/run-wine-python.sh" -m pip install --no-index --find-links 'Z:\workspace\.compat\wheels' --find-links 'Z:\workspace\.compat\wheels-qt69' --find-links 'Z:\workspace\.compat\wheels-numpy22' -r 'Z:\workspace\rougezhushou\requirements.txt' 'PySide6==6.9.3' 'numpy==2.2.6' --no-cache-dir
"$compat_root/run-wine-python.sh" -m pip check
