@echo off
REM ClawCat Launcher for Windows
REM Activates conda environment and starts service manager

setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PLUGIN_ROOT=%SCRIPT_DIR%.."

REM Change to plugin root
cd /d "%PLUGIN_ROOT%"

REM Try to find and activate conda
set "CONDA_FOUND=0"
set "CONDA_BASE="

REM Try conda in PATH first
where conda >nul 2>&1
if %ERRORLEVEL% == 0 (
    REM Get conda base directory
    for /f "tokens=*" %%i in ('conda info --base 2^>nul') do set "CONDA_BASE=%%i"
    if defined CONDA_BASE (
        if exist "%CONDA_BASE%\Scripts\activate.bat" (
            call "%CONDA_BASE%\Scripts\activate.bat" base
            if %ERRORLEVEL% == 0 (
                set "CONDA_FOUND=1"
            )
        )
    )
)

REM If not found, try common locations
if %CONDA_FOUND% == 0 (
    if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
        call "%USERPROFILE%\miniconda3\Scripts\activate.bat" base
        if %ERRORLEVEL% == 0 (
            set "CONDA_FOUND=1"
        )
    )
)

if %CONDA_FOUND% == 0 (
    if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
        call "%USERPROFILE%\anaconda3\Scripts\activate.bat" base
        if %ERRORLEVEL% == 0 (
            set "CONDA_FOUND=1"
        )
    )
)

REM Start service manager (which will handle dependency installation and window launch)
python "%PLUGIN_ROOT%\scripts\service_manager.py" start

endlocal

