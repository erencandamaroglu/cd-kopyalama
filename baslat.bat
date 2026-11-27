@echo off
chcp 65001 >nul
title CD Kopyalayici
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Python ortami bulunamadi. Once kurulum.bat dosyasini calistirin.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -c "import tkinter" >nul 2>nul
if errorlevel 1 (
  echo Python ortami bu bilgisayarda eksik veya bozuk. kurulum.bat dosyasini calistirin.
  pause
  exit /b 1
)
rem Pencere konsolsuz (pythonw) acilir; hatalar %USERPROFILE%\CdKopyalama\hata.log dosyasina yazilir.
start "" ".venv\Scripts\pythonw.exe" main.py %*
exit /b 0
