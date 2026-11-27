@echo off
chcp 65001 >nul
title CD Kopyalayici
cd /d "%~dp0"
rem Ek paket gerekmez; Python 3.8+ ve tkinter yeterli. Pencere konsolsuz (pythonw) acilir.
set PYW=
call :python_bul "pyw -3" "py -3"
if not defined PYW call :python_bul "pythonw" "python"
if not defined PYW (
  echo Python 3.8 veya uzeri bulunamadi. https://www.python.org adresinden Python kurun
  echo ^(kurulumda "Add python.exe to PATH" secenegini isaretleyin^).
  pause
  exit /b 1
)
start "" %PYW% main.py %*
exit /b 0
:python_bul
%~2 -c "import sys, tkinter; sys.exit(0 if sys.version_info>=(3,8) else 1)" >nul 2>nul
if not errorlevel 1 set "PYW=%~1"
exit /b 0
