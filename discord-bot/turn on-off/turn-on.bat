@echo off
REM ============================================================
REM  Sets up a Windows scheduled task that runs the C.A.T.S.
REM  timer reader every 15 minutes, automatically.
REM  Run this file ONCE (double-click it) to turn automation ON.
REM ============================================================

set TASK_NAME=CATS_Timer_Reader
set SCRIPT_PATH=%~dp0C.A.T.S. Timer Reader - Send to Discord read timer only.py

schtasks /Create /TN "%TASK_NAME%" /TR "python \"%SCRIPT_PATH%\"" /SC MINUTE /MO 15 /F

echo.
echo ============================================================
echo   Done! The timer reader will now run automatically every
echo   15 minutes in the background.
echo.
echo   To STOP it at any time, double-click: stop_auto_timer.bat
echo   Or open Task Scheduler and disable/delete "%TASK_NAME%"
echo ============================================================
pause
