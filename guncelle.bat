@echo off
chcp 65001 >nul
title CD Kopyalayici - Guncelleme
echo CD Kopyalayici - Guncelleme
echo ---------------------------
echo.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Python ortami bulunamadi. Once kurulum.bat dosyasini calistirin.
  pause
  exit /b 1
)
if exist ".git" (
  where git >nul 2>nul
  if errorlevel 1 (
    echo UYARI: git bulunamadi; kod guncellenemedi. https://git-scm.com adresinden kurabilirsiniz.
  ) else (
    echo GitHub'dan son surum aliniyor...
    git pull --ff-only
    if errorlevel 1 goto hata
  )
) else (
  echo Bu klasor git deposu degil; kod guncellemesi atlandi.
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q --upgrade -r requirements.txt
if errorlevel 1 goto hata
echo.
echo Guncelleme tamamlandi. Ayarlar ^(%%USERPROFILE%%\CdKopyalama^) korunur.
pause
exit /b 0
:hata
echo Guncelleme tamamlanamadi. Yukaridaki hata mesajini kontrol edin.
pause
exit /b 1
