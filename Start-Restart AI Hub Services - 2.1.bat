@echo off
setlocal enabledelayedexpansion
echo AI Hub Services Manager - Start/Restart Script
echo =============================================

:: Set the path to the Anaconda/Miniconda installation
SET "CONDA_PATH=C:\Users\james\miniconda3"
:: Set the project folder path
SET "PROJECT_PATH=C:\src\aihub-client-upgrade"

echo.
echo Checking for running services...
echo.

:: Define the scripts we're looking for
set SCRIPTS=wsgi.py wsgi_doc_api.py app_doc_job_q.py app_jss_main.py wsgi_vector_api.py wsgi_knowledge_api.py

:: Kill each script's process
for %%s in (%SCRIPTS%) do (
    echo Looking for processes running %%s...
    
    :: Get process IDs directly from WMIC for processes containing the script name
    for /f "skip=1 tokens=2 delims=," %%p in ('wmic process where "name='python.exe' and commandline like '%%%%s%%'" get processid /format:csv 2^>nul') do (
        if not "%%p"=="" (
            echo [!] Found process %%p running %%s - killing it...
            taskkill /PID %%p /F
            if !errorlevel! equ 0 (
                echo [X] Successfully killed process %%p
            ) else (
                echo [E] Failed to kill process %%p
            )
        )
    )
)

:: Alternative method: Kill all processes at once using a single WMIC command
echo.
echo Using alternative method to ensure all processes are stopped...
wmic process where "name='python.exe' and (commandline like '%%wsgi.py%%' or commandline like '%%wsgi_doc_api.py%%' or commandline like '%%app_doc_job_q.py%%' or commandline like '%%app_jss_main.py%%' or commandline like '%%wsgi_vector_api.py%%' or commandline like '%%app_agent_api.py%%' or commandline like '%%wsgi_agent_api.py%%' or commandline like '%%wsgi_knowledge_api.py%%')" delete >nul 2>&1

:: Also kill by window title
echo Cleaning up any remaining windows...
taskkill /FI "WINDOWTITLE eq AIHub*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Administrator:*AIHub*" /F >nul 2>&1

:: Wait for processes to terminate
echo.
echo Waiting for processes to terminate...
timeout /t 3 /nobreak >nul

echo.
echo Starting all AI Hub services...
echo.

:: Start services
echo [1/7] Starting Document API Server (wsgi_doc_api.py) in aihubant environment...
start "AIHub Document API" /D "%PROJECT_PATH%" cmd /k "color 0B && title AIHub Document API && "%CONDA_PATH%\Scripts\activate.bat" && conda activate aihubant && python wsgi_doc_api.py"

timeout /t 3 /nobreak >nul

echo [2/7] Starting Document Job Queue (app_doc_job_q.py) in aihubant environment...
start "AIHub Doc Job Queue" /D "%PROJECT_PATH%" cmd /k "color 0C && title AIHub Doc Job Queue && "%CONDA_PATH%\Scripts\activate.bat" && conda activate aihubant && python app_doc_job_q.py"

timeout /t 3 /nobreak >nul

echo [3/7] Starting JSS Main Application (app_jss_main.py) in jss environment...
start "AIHub JSS Main" /D "%PROJECT_PATH%" cmd /k "color 0D && title AIHub JSS Main && "%CONDA_PATH%\Scripts\activate.bat" && conda activate jss && python app_jss_main.py"

timeout /t 3 /nobreak >nul

echo [4/7] Starting Vector API Server (wsgi_vector_api.py) in aihubvector2 environment...
start "AIHub Vector API" /D "%PROJECT_PATH%" cmd /k "color 0E && title AIHub Vector API && "%CONDA_PATH%\Scripts\activate.bat" && conda activate aihubvector2 && python wsgi_vector_api.py"

timeout /t 3 /nobreak >nul

echo [5/7] Starting Agent API Server (wsgi_agent_api.py) in aihub2 environment...
start "AIHub Agent API" /D "%PROJECT_PATH%" cmd /k "color 0F && title AIHub Agent API && "%CONDA_PATH%\Scripts\activate.bat" && conda activate aihub2.1 && python wsgi_agent_api.py"

timeout /t 3 /nobreak >nul

echo [6/7] Starting Knowledge API Server (wsgi_knowledge_api.py) in aihub2 environment...
start "AIHub Knowledge API" /D "%PROJECT_PATH%" cmd /k "color 0F && title AIHub Knowledge API && "%CONDA_PATH%\Scripts\activate.bat" && conda activate aihub2.1 && python wsgi_knowledge_api.py"

timeout /t 3 /nobreak >nul

echo [7/7] Starting Main Application (wsgi.py) in aihub2 environment...
start "AIHub Main App" /D "%PROJECT_PATH%" cmd /k "color 0A && title AIHub Main App && "%CONDA_PATH%\Scripts\activate.bat" && conda activate aihub2.1 && python wsgi.py"

echo.
echo ========================================
echo All services have been launched!
echo ========================================
echo.
echo Each service is running in its own window:
echo - Green  : Main Application (aihub2)
echo - Cyan   : Document API Server (aihubant)
echo - Red    : Document Job Queue (aihubant)
echo - Purple : JSS Main Application (jss)
echo - Yellow : Vector API Server (aihubvector)
echo - ????? : Agent API Server (aihub2)
echo.
echo To stop a service, close its window or press Ctrl+C in it.
echo To restart all services, run this script again.
echo.
REM pause
endlocal