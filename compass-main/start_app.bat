@echo off 
ECHO Welcome to COMPASS!
ECHO -------------------
ECHO Checking if VENV exists....
if exist .\.venv ECHO Found .venv/
if not exist .\.venv ECHO Couldn't find VENV. Now installing via ./setup_environment.bat
if not exist .\.venv CALL .\setup_environment.bat -d all -s 1.1.15 -p pyansys-solutions 
ECHO Starting application...
call .\.venv\Scripts\saf -d src/ansys/solutions devrun compass
pause