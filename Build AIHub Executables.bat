@echo off
echo Starting build process for all AI Hub applications...

:: Set the path to the Anaconda/Miniconda installation
SET "CONDA_PATH=C:\Users\james\miniconda3"

:: Set the project folder path
SET "PROJECT_PATH=C:\src\aihub-client"

echo Building app.spec with aihub2 environment...
:: Initialize Conda and activate aihub2 environment
CALL "%CONDA_PATH%\Scripts\activate.bat"
CALL conda activate aihub2
:: Navigate to the project folder
cd /d %PROJECT_PATH%
:: Run PyInstaller for the first spec file
pyinstaller app.spec
:: Deactivate the environment
CALL conda deactivate

echo Building wsgi_doc_api.spec with aihubant environment...
:: Activate aihubant environment
CALL conda activate aihubant
:: Navigate to the project folder (in case it changed)
cd /d %PROJECT_PATH%
:: Run PyInstaller for the second spec file
pyinstaller wsgi_doc_api.spec
:: Deactivate the environment
CALL conda deactivate

echo Building app_doc_job_q.spec with aihubant environment...
:: Activate aihubant environment
CALL conda activate aihubant
:: Navigate to the project folder (in case it changed)
cd /d %PROJECT_PATH%
:: Run PyInstaller for the second spec file
pyinstaller app_doc_job_q.spec
:: Deactivate the environment
CALL conda deactivate

echo Building app_jss_main.spec with jss environment...
:: Activate jss environment
CALL conda activate jss
:: Navigate to the project folder (in case it changed)
cd /d %PROJECT_PATH%
:: Run PyInstaller for the third spec file
pyinstaller app_jss_main.spec
:: Deactivate the environment
CALL conda deactivate

::echo Skipping building wsgi_vector_api.spec, this must be built with Nuitka on the build machine...
echo Building wsgi_vector_api.spec with aihubvector environment...
:: Activate aihubvector2 environment
CALL conda activate aihubvector2
:: Navigate to the project folder (in case it changed)
cd /d %PROJECT_PATH%
:: Run PyInstaller for the fourth spec file
pyinstaller wsgi_vector_api.spec
:: Deactivate the environment
CALL conda deactivate

::echo Skipping building wsgi_agent_api.spec, this must be built with Nuitka on the build machine...
echo Building wsgi_agent_api.spec with aihub2 environment...
:: Activate aihub2 environment
CALL conda activate aihub2
:: Navigate to the project folder (in case it changed)
cd /d %PROJECT_PATH%
:: Run PyInstaller for the fifth spec file
pyinstaller wsgi_agent_api.spec
:: Deactivate the environment
CALL conda deactivate

echo Building wsgi_knowledge_api.spec with aihub2 environment...
:: Activate aihub2 environment
CALL conda activate aihub2
:: Navigate to the project folder (in case it changed)
cd /d %PROJECT_PATH%
:: Run PyInstaller for the fifth spec file
pyinstaller wsgi_knowledge_api.spec
:: Deactivate the environment
CALL conda deactivate

echo All builds completed successfully!
pause
