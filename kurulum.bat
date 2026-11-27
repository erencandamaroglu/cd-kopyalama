@echo off
chcp 65001 >nul
title CD Kopyalayici - Kurulum
echo CD Kopyalayici - Kurulum
echo ------------------------
echo.
cd /d "%~dp0"
set PY=
call :python_bul "py -3"
if not defined PY call :python_bul "python"
if not defined PY (
  echo Python 3.8 veya uzeri ^(tkinter ile^) bulunamadi. https://www.python.org adresinden Python kurun
  echo ^(kurulumda "Add python.exe to PATH" ve "tcl/tk" secenekleri isaretli olsun^).
  goto hata
)
echo Kullanilan Python: %PY%
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import tkinter" >nul 2>nul
  if errorlevel 1 (
    echo Mevcut .venv bu bilgisayarda calismiyor; yeniden olusturuluyor...
    rmdir /s /q .venv
  )
)
if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv
  if errorlevel 1 goto hata
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto hata
call :kisayol_olustur
echo.
echo Kurulum tamamlandi. baslat.bat ya da masaustundeki "CD Kopyalayici" kisayolu ile acabilirsiniz.
pause
exit /b 0
:hata
echo Kurulum tamamlanamadi. Yukaridaki hata mesajini kontrol edin.
pause
exit /b 1
:python_bul
%~1 -c "import sys, tkinter; sys.exit(0 if sys.version_info>=(3,8) else 1)" >nul 2>nul
if not errorlevel 1 set "PY=%~1"
exit /b 0
:kisayol_olustur
rem Hedefi ag surucusunde olan kisayolun ikonunu Explorer gostermez: hedef yerel cmd.exe (kucultulmus,
rem baslat.bat'i calistirir), ikon %USERPROFILE%\CdKopyalama altindaki yerel kopya.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$k = (Get-Location).Path; $ws = New-Object -ComObject WScript.Shell;" ^
  "$l = $ws.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'CD Kopyalayici.lnk'));" ^
  "$l.TargetPath = $env:ComSpec; $l.Arguments = '/c ' + [char]34 + (Join-Path $k 'baslat.bat') + [char]34; $l.WorkingDirectory = $k; $l.WindowStyle = 7;" ^
  "$i = Join-Path $env:USERPROFILE 'CdKopyalama\ikon.ico'; New-Item -ItemType Directory -Force (Split-Path $i) | Out-Null;" ^
  "Copy-Item (Join-Path $k 'varliklar\ikon.ico') $i -Force; $l.IconLocation = $i + ',0'; $l.Description = 'CD Kopyalayici'; $l.Save()"
if errorlevel 1 (echo Kisayol olusturulamadi.) else (echo Masaustune "CD Kopyalayici" kisayolu olusturuldu.)
exit /b 0
