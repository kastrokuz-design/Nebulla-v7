@echo off
title NEBULA v7 — ChatGPT Library Image Downloader
setlocal EnableExtensions
cd /d "%~dp0"

echo ======================================================================================================
echo  NEBULA v7 — Bibliotheque Images / Library Images (Improved)
echo ------------------------------------------------------------------------------------------------------
echo  FR: 1) Lance Chrome debug/profil propre. 2) Connectez-vous. 3) Ouvrez Bibliotheque^>Images.
echo       4) Appuyez touche pour demarrer (scroll auto + progression).
echo  EN: 1) Launches Chrome debug/fresh profile. 2) Sign in. 3) Open Library^>Images.
echo       4) Press key to start (auto-scroll + progress).
echo ------------------------------------------------------------------------------------------------------
echo  Options: python attach_chatgpt_images_v7.py --parallel --out out/
echo  Credits: You + ChatGPT + Grok (xAI)
echo ======================================================================================================
echo.

:: Setup
set "OUTDIR=%CD%\out"
if not exist "%OUTDIR%" mkdir "%OUTDIR%"

:: Python
set "PY=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"

:: Chrome
set "CHROME=chrome"
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"

:: Temp profile
set "TMPDIR=%TEMP%\nebula_profile_v7"
if exist "%TMPDIR%" rmdir /s /q "%TMPDIR%" >nul 2>&1
mkdir "%TMPDIR%" >nul 2>&1

:: Launch
start "" "%CHROME%" --remote-debugging-port=9222 --user-data-dir="%TMPDIR%" --new-window "https://chatgpt.com/library?tab=images"
echo [INFO] Chrome lance: https://chatgpt.com/library?tab=images ^(port 9222^)

echo.
echo FR: Quand pret, appuyez touche. EN: When ready, press key.
pause >nul

echo [INFO] Demarrage... / Starting...
"%PY%" "%CD%\attach_chatgpt_images_v7.py" --out "%OUTDIR%" --debugger 127.0.0.1:9222
set "ERR=%ERRORLEVEL%"

echo.
echo ======================================================================================================
if "%ERR%"=="0" (
  echo FR: Termine ! Fichiers: "%OUTDIR%"
  echo EN: Done! Files: "%OUTDIR%"
) else (
  echo FR: Erreur %ERR%.
  echo EN: Error %ERR%.
)
echo Credits: You + ChatGPT + Grok (xAI)
echo ======================================================================================================
echo.
pause
rmdir /s /q "%TMPDIR%" >nul 2>&1
