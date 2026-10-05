@echo off
setlocal
pushd "%~dp0"
if not exist "%~dp0.venv\Scripts\pythonw.exe" (
  echo Missing project runtime. Please follow README.md.
  pause
  popd
  exit /b 1
)
start "" "%~dp0.venv\Scripts\pythonw.exe" -m rouge.app
popd
endlocal
