@echo off
ECHO Set PyAnsys PyPI *token* to environment. 
set /p token=Please enter the PyAnsys token to be saved as PYANSYS_PRIVATE_PYPI_PAT:
setx PYANSYS_PRIVATE_PYPI_PAT %token%
ECHO Set Solutions PyPI *token* to environment. 
set /p token=Please enter the Solutions token to be saved as SOLUTIONS_PRIVATE_PYPI_PAT:
setx SOLUTIONS_PRIVATE_PYPI_PAT %token%
ECHO You may now use this variable to install dependencies via install helpers scripts
ECHO But first, you must again initalize your environment variables 
pause


