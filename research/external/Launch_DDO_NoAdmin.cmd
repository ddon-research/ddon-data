@echo off
setlocal
cd /d "%~dp0"
set "__COMPAT_LAYER=RunAsInvoker"
start "" "%~dp0DDO.exe" %*
endlocal
