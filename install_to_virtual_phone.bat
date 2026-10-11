@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   FS Exam Prep - Fast Virtual Phone Deployer
echo ========================================================
echo.

set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"

if not exist "!ADB!" (
    echo [ERROR] adb.exe not found at: !ADB!
    echo Please make sure Android Studio / Android SDK is installed.
    pause
    exit /b 1
)

:: Find the APK file
set "APK_PATH=%~1"

if "!APK_PATH!"=="" (
    :: Look for newest APK in Downloads
    for /f "delims=" %%F in ('dir /b /o:-d "%USERPROFILE%\Downloads\*fs*.apk" 2^>nul') do (
        set "APK_PATH=%USERPROFILE%\Downloads\%%F"
        goto :FoundApk
    )
    for /f "delims=" %%F in ('dir /b /o:-d "%USERPROFILE%\Downloads\app-debug*.apk" 2^>nul') do (
        set "APK_PATH=%USERPROFILE%\Downloads\%%F"
        goto :FoundApk
    )
    for /f "delims=" %%F in ('dir /b /o:-d "%~dp0mobile\build\app\outputs\flutter-apk\app-debug.apk" 2^>nul') do (
        set "APK_PATH=%~dp0mobile\build\app\outputs\flutter-apk\app-debug.apk"
        goto :FoundApk
    )
)

:FoundApk
if "!APK_PATH!"=="" (
    echo [INFO] No APK file specified.
    echo Usage:
    echo   Drag and drop an .apk file onto this .bat file
    echo   OR place your downloaded APK in your Downloads folder.
    echo.
    set /p "APK_PATH=Enter full path to .apk file: "
)

if not exist "!APK_PATH!" (
    echo [ERROR] File not found: !APK_PATH!
    pause
    exit /b 1
)

echo [1/3] Target APK: !APK_PATH!

:: Check if virtual phone (emulator) is running
echo [2/3] Checking for connected virtual phone...
for /f "tokens=1,2" %%A in ('"!ADB!" devices ^| findstr /r "emulator-[0-9]*"') do (
    set "DEVICE_ID=%%A"
)

if "!DEVICE_ID!"=="" (
    echo [INFO] Virtual phone is not running. Launching Pixel 8...
    set "EMULATOR=%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe"
    if exist "!EMULATOR!" (
        start "" "!EMULATOR!" -avd Pixel_8
        echo Waiting for virtual phone to boot (takes ~20 seconds)...
        "!ADB!" wait-for-device
        timeout /t 5 >nul
    ) else (
        echo [ERROR] Please launch your Pixel 8 emulator from Android Studio first.
        pause
        exit /b 1
    )
)

echo [3/3] Installing APK to virtual phone...
"!ADB!" install -r "!APK_PATH!"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] FS Exam Prep installed successfully!
    echo Launching app...
    "!ADB!" shell monkey -p com.crieck2010.fs_exam_app -c android.intent.category.LAUNCHER 1 >nul 2>&1
    echo App is now running on your Pixel 8.
) else (
    echo.
    echo [ERROR] Installation failed.
)

echo.
pause
