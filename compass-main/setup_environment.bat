@echo off
:: ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

:: ====================================================================================================================
:: This program is intended for users looking for an automatic process to setup the Python environment required by the
:: package.
:: ====================================================================================================================

:: =================================================== [Functions] ====================================================

:init
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Initialize variables and set default values.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    set "__NAME=%~n0"
    set "__VERSION=0.0.dev1"
    set "__YEAR=2022"

    set "__BAT_FILE=%~0"
    set "__BAT_PATH=%~dp0"
    set "__BAT_NAME=%~nx0"

    set "OptHelp="
    set "OptVersion="
    set "OptVerbose="

    set dependencies=none
    set build_system=poetry
    set build_system_version=*
    set install_mode=default
    set private_pypi_servers=none
    set private_repositories=none

    set "authorized_dependencies=run doc tests build all"
    set "authorized_build_systems=setuptools-flit-poetry-pipenv"
    set "authorized_pypi_servers=ace pyansys solutions none"
    set "authorized_private_repositories=pyansys_report none"
    set "authorized_install_mode=default-pip"
    set clear_workspace=true

    set run_dependencies=false
    set doc_dependencies=false
    set tests_dependencies=false
    set build_dependencies=false
    set venv_name=.venv
    
:: --------------------------------------------------------------------------------------------------------------------

:parse
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Read command line arguments and assign to variables.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    :: Empty command line. No inputs.
    if "%~1"==""                           goto :validate
    :: Help command
    if /i "%~1"=="/?"                      call :header & call :usage "%~2" & goto :end
    if /i "%~1"=="-?"                      call :header & call :usage "%~2" & goto :end
    if /i "%~1"=="-h"                      call :header & call :usage "%~2" & goto :end
    if /i "%~1"=="--help"                  call :header & call :usage "%~2" & goto :end
    :: Version command
    if /i "%~1"=="/V"                      call :version      & goto :end
    if /i "%~1"=="-V"                      call :version      & goto :end
    if /i "%~1"=="--version"               call :version full & goto :end
    :: Verbose command
    if /i "%~1"=="/v"                      set "OptVerbose=yes" & shift & goto :parse
    if /i "%~1"=="-v"                      set "OptVerbose=yes" & shift & goto :parse
    if /i "%~1"=="--verbose"               set "OptVerbose=yes" & shift & goto :parse
    :: Dependencies
    if /i "%~1"=="-d"                      set "dependencies=%~2" & shift & goto :parse
    if /i "%~1"=="--dependencies"          set "dependencies=%~2" & shift & goto :parse
    :: Build system
    if /i "%~1"=="-b"                      set "build_system=%~2" & shift & shift & goto :parse
    if /i "%~1"=="--build-system"          set "build_system=%~2" & shift & shift & goto :parse
    :: Build system version
    if /i "%~1"=="-s"                      set "build_system_version=%~2" & shift & shift & goto :parse
    if /i "%~1"=="--build-system-version"  set "build_system_version=%~2" & shift & shift & goto :parse
    :: Install mode
    if /i "%~1"=="-i"                      set "install_mode=%~2" & shift & shift & goto :parse
    if /i "%~1"=="--install-mode"          set "install_mode=%~2" & shift & shift & goto :parse
    :: Private PyPI
    if /i "%~1"=="-p"                      set "private_pypi_servers=%~2" & shift & goto :parse
    if /i "%~1"=="--private-pypi"          set "private_pypi_servers=%~2" & shift & goto :parse
    :: Private GIT repository
    if /i "%~1"=="-g"                      set "private_repositories=%~2" & shift & goto :parse
    if /i "%~1"=="--private-repo"          set "private_repositories=%~2" & shift & goto :parse
    :: Do not clear the workspace
    if /i "%~1"=="-n"                      set "clear_workspace=false" & shift & goto :parse
    if /i "%~1"=="--no-clear"              set "clear_workspace=false" & shift & goto :parse
    :: Virtual environment name
    if /i "%~1"=="-e"                      set "venv_name=%~2" & shift & shift & goto :parse
    if /i "%~1"=="--venv-name"             set "venv_name=%~2" & shift & shift & goto :parse
    shift
    goto :parse
:: --------------------------------------------------------------------------------------------------------------------

:validate
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Process cases where no argument is declared. Continue with default settings.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------
    goto :main
:: --------------------------------------------------------------------------------------------------------------------

:end
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Cleanup variables and end program wwith exit code 0.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------
    call :cleanup
    cmd /k
:: --------------------------------------------------------------------------------------------------------------------

:end_with_error
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Cleanup variables and end program wwith exit code > 0.
    ::
    :: Parameters
    :: ----------
    :: 1st argument (int): exit code.
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------
    call :cleanup
    set exit_code=%~1
    pause
    exit %exit_code%
:: --------------------------------------------------------------------------------------------------------------------

:cleanup
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Cleanup variables. Only really necessary if you are not using SETLOCAL.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    set "__NAME="
    set "__VERSION="
    set "__YEAR="

    set "__BAT_FILE="
    set "__BAT_PATH="
    set "__BAT_NAME="

    set "OptHelp="
    set "OptVersion="
    set "OptVerbose="

    set "install_mode="
    set "poetry_version="
    set "add_doc_dependencies="
    set "add_test_dependencies="
    set "add_build_dependencies="
    set "private_pypi_servers="
    set "clear_workspace="

    goto :eof
:: --------------------------------------------------------------------------------------------------------------------

:header
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Display header and exit.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------
    echo %__NAME% v%__VERSION%
    echo This batch file sets up the environment to run the project.
    echo.
    goto :eof
:: --------------------------------------------------------------------------------------------------------------------

:usage  
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Show program usage and exit.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------
    echo USAGE:
    echo   %__BAT_NAME% [flags] "optional argument" 
    echo.
    echo.  -h, --help                                 shows this help
    echo.  -V, --version                              shows the version
    echo.  -v, --verbose                              shows detailed output
    echo.  -d, --dependencies {value1-value2-value3}  list of dependencies to install {run, doc, tests, build, all}. Separate each name with dash. Avoid sapces. Case insensitive.
    echo.  -b, --build-system {build-system-name}     defines build system {setuptools, flit, poetry, pipenv}
    echo.  -s, --build-system-version {version}       sets build system version
    echo.  -i, --install-mode {pip, default}          system to install requirements. Default means that the build system is used.
    echo.  -p, --private-pypi {value1-value2-value3}  list of private PyPI servers. Separate each name with dash. Avoid sapces. Case insensitive.
    echo.  -g, --private-repo {value1-value2-value3}  list of private GIT repositories. Separate each name with dash. Avoid sapces. Case insensitive.
    echo.  -n, --no-clear                             do not clear the workspace. This assumes that a virtual environment already exists.
    echo.  -e, --venv-name                            name of the virtual environment. Default: .venv
    echo.
    echo   This program is intended to be executed at the root directory of the project repository where the build system configuration files are located. 
    echo   Also, it is assumed that the following elements exist:
    echo      - requirements                        : requirements folder
    echo      - requirements/requirements_doc.txt   : file containing doc dependencies
    echo      - requirements/requirements_tests.txt : file containing tests dependencies
    echo      - requirements/requirements_build.txt : file containing build dependencies
    echo.
    echo   In case a connection to a private PyPI source is needed, you will need to declare the source personal access token in a system environement variable.   
    echo   The authorized sources for solutions are: 
    echo      - PyAnsys private PyPI registry: create a variable named PYANSYS_PRIVATE_PYPI_PAT and set it with the right PAT. 
    echo      - Solutions private PyPI feed  : create a variable named SOLUTIONS_PRIVATE_PYPI_PAT and set it with the right PAT. 
    echo      - ACE private PyPI registry    : create a variable named ACE_PRIVATE_PYPI_PAT and set it with the right PAT. 
    echo.
    echo   In case a connection to a private GIT repository is needed, you will need to declare the source personal access token in a system environement variable.   
    echo   The authorized git repositories for solutions are: 
    echo      - PyAnsys Report repository: create a variable named PYANSYS_GITHUB_PAT and set it with the right PAT. 
    echo.
    goto :eof
:: --------------------------------------------------------------------------------------------------------------------

:version
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Show program version and exit.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------
    if "%~1"=="full" call :header & goto :eof
        echo %__BAT_NAME% version: %__VERSION%
    goto :eof
:: --------------------------------------------------------------------------------------------------------------------

:check_inputs
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: heck input values and ensure consistency with expected values.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    :: Check if run dependencies are requested
    call :check_if_string_contains_text %dependencies% run is_declared
    set run_dependencies=%is_declared%
    :: Check if doc dependencies are requested
    call :check_if_string_contains_text %dependencies% doc is_declared
    set doc_dependencies=%is_declared%
    :: Check if tests dependencies are requested
    call :check_if_string_contains_text %dependencies% tests is_declared
    set tests_dependencies=%is_declared%
    :: Check if build dependencies are requested
    call :check_if_string_contains_text %dependencies% build is_declared
    set build_dependencies=%is_declared%
    :: Check if all dependencies are requested
    call :check_if_string_contains_text %dependencies% all is_declared
    if %is_declared% == true (
        set run_dependencies=true
        set doc_dependencies=true
        set tests_dependencies=true
        set build_dependencies=true
    )
    :: Check if the dependency types declared exist
    setlocal EnableDelayedExpansion
    if not [%dependencies%] == none (
        set n=1
        set "dependencies[!n!]=%dependencies:-=" & set /A n+=1 & set "dependencies[!n!]=%"
        for /l %%i in (1,1,%n%) do (
            set exists=false
            for %%a in (%authorized_dependencies%) do (
                if "%%a" == "!dependencies[%%i]!" (
                    set exists=true
                    if "%%a" == "doc" (
                        set doc_dependencies=true
                    )
                )
            )
            if not [%dependencies%]==[] ( 
                if not !exists! == true (
                    call :exit_with_error_message "unknown dependency type !dependencies[%%i]!" 1
                )
            )
        )
    )
    endlocal
    :: Check if pyproject.toml exists when run dependencies are requested
    setlocal enabledelayedexpansion
    if not [%dependencies%] == none (
        call :check_if_string_contains_text %dependencies% run is_declared 
        if !is_declared! == true (
            if not exist pyproject.toml (
                call :exit_with_error_message "Run dependencies are requested but there are no pyproject.toml at the root directory." 1
            )
        )
    )
    endlocal
    :: Check if the build system declared exist 
    setlocal EnableDelayedExpansion
    set exists=false
    set n=1
    set "authorized_build_systems[!n!]=%authorized_build_systems:-=" & set /A n+=1 & set "authorized_build_systems[!n!]=%"
    for /l %%i in (1,1,%n%) do (
        if !authorized_build_systems[%%i]! == %build_system% (
            set exists=true
        )
    )
    if %exists% == false (
        call :exit_with_error_message "unknown build system %build_system%." 1
    )
    endlocal
    :: Check if the private PyPI servers declared exist and if the associated PAT have been properly set
    setlocal EnableDelayedExpansion
    set n=1
    set "private_pypi_servers[!n!]=%private_pypi_servers:-=" & set /A n+=1 & set "private_pypi_servers[!n!]=%"
    for /l %%i in (1,1,%n%) do (
        set exists=false
        for %%a in (%authorized_pypi_servers%) do (
            if "%%a" == "!private_pypi_servers[%%i]!" (
                set exists=true
                if "!private_pypi_servers[%%i]!" == "ace" (
                    if "%ACE_PRIVATE_PYPI_PAT%"=="" (
                        call :exit_with_error_message "environment variable ACE_PRIVATE_PYPI_PAT is not defined." 1
                    ) 
                )
                if "!private_pypi_servers[%%i]!" == "pyansys" (
                    if "%PYANSYS_PRIVATE_PYPI_PAT%"=="" (
                        call :exit_with_error_message "environment variable PYANSYS_PRIVATE_PYPI_PAT is not defined." 1
                    ) 
                )
                if "!private_pypi_servers[%%i]!" == "solutions" (
                    if "%SOLUTIONS_PRIVATE_PYPI_PAT%"=="" (
                        call :exit_with_error_message "environment variable SOLUTIONS_PRIVATE_PYPI_PAT is not defined." 1
                    ) 
                )
            )
        )
        if not [%private_pypi_servers%]==[] ( 
            if not !exists! == true (
                call :exit_with_error_message "unknown PyPI server !private_pypi_servers[%%i]!" 1
            )
        )
    )
    endlocal
    :: Check if the installaton mode declared exist
    setlocal EnableDelayedExpansion
    set exists=false
    set n=1
    set "authorized_install_mode[!n!]=%authorized_install_mode:-=" & set /A n+=1 & set "authorized_install_mode[!n!]=%"
    for /l %%i in (1,1,%n%) do (
        if !authorized_install_mode[%%i]! == %install_mode% (
            set exists=true
        )
    )
    if %exists% == false (
        call :exit_with_error_message "unknown installation mode %install_mode%." 1
    )
    endlocal

    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:cleanup_workspace
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Remove existing virtual environement and files such as lock and requirements.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    if %clear_workspace% == true (
        if exist %venv_name% (
            echo Delete existing virtual environment
            rmdir /Q /S %venv_name%
        )
        if %build_system% == poetry (
            if exist poetry.lock (
                echo Delete existing poetry lock file
                del poetry.lock
            )
        )
        if exist requirements.txt (
            echo Delete existing requirements.txt
            del requirements.txt
        )
    )
    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:configure_build_system
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Configure build system.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    :: Set virtual environment location
    if %build_system% == flit (
        call :exit_with_error_message "not implemented for flit yet!" 1
    )
    if %build_system% == pipenv (
        @REM setx PIPENV_VENV_IN_PROJECT true
        call :exit_with_error_message "not implemented for pipenv yet!" 1
    )
    if %build_system% == poetry (
        call %venv_name%\Scripts\poetry config virtualenvs.in-project true
    )
    if %build_system% == setuptools (
        call :exit_with_error_message "not implemented for setuptools yet!" 1
    )
    :: Declare credentials to private sources (PyPI servers, GitHub repositories)
    call :setup_private_sources

    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:setup_private_sources
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Configure Poetry to connect to private PyPI servers such as PyAnsys, ACE and Solutions.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    setlocal EnableDelayedExpansion
    if %build_system% == flit (
        call :exit_with_error_message "not implemented for flit yet!" 1
    )
    if %build_system% == pipenv (
        call :exit_with_error_message "not implemented for pipenv yet!" 1
    )
    if %build_system% == poetry (
        :: Configure ACE private PyPI server
        call :check_if_string_contains_text %private_pypi_servers% ace is_declared
        if !is_declared! == true (
            echo Set ACE private PyPI credentials
            call %venv_name%\Scripts\poetry config repositories.ace-private-pypi https://pkgs.dev.azure.com/ysommer/_packaging/Internal_pypi/pypi/simple/
            call %venv_name%\Scripts\poetry config http-basic.ace-private-pypi PAT %ACE_PRIVATE_PYPI_PAT% 
        ) else (
            call :remove_private_source ace-private-pypi
        )
        :: Configure PYANSYS private PyPI server
        call :check_if_string_contains_text %private_pypi_servers% pyansys is_declared
        if !is_declared! == true (
            echo Set Pyansys private PyPI credentials
            call %venv_name%\Scripts\poetry config repositories.pyansys-private-pypi https://pkgs.dev.azure.com/pyansys/_packaging/pyansys/pypi/simple/
            call %venv_name%\Scripts\poetry config http-basic.pyansys-private-pypi PAT %PYANSYS_PRIVATE_PYPI_PAT% 
        ) else (
            call :remove_private_source pyansys-private-pypi
        )
        :: Configure SOLUTIONS private PyPI server
        call :check_if_string_contains_text %private_pypi_servers% solutions is_declared
        if !is_declared! == true (
            echo Set Solutions private PyPI credentials
            call %venv_name%\Scripts\poetry config repositories.solutions-private-pypi https://pkgs.dev.azure.com/pyansys/_packaging/ansys-solutions/pypi/simple/
            call %venv_name%\Scripts\poetry config http-basic.solutions-private-pypi PAT %SOLUTIONS_PRIVATE_PYPI_PAT% 
        ) else (
            call :remove_private_source solutions-private-pypi
        )
        :: Configure PyAnsys Report private repository
        call :check_if_string_contains_text %private_repositories% pyansys_report is_declared
        if !is_declared! == true (
            echo Set PyAnsys Report private repository credentials
            call %venv_name%\Scripts\poetry config repositories.pyansys-report https://github.com/pyansys/pyansys-report-pdf
            call %venv_name%\Scripts\poetry config http-basic.pyansys-report iazehaf %PYANSYS_GITHUB_PAT% 
        ) else (
            call :remove_private_source pyansys-report
        )
    )
    if %build_system% == setuptools (
        call :exit_with_error_message "not implemented for setuptools yet!" 1
    )
    endlocal

    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:remove_private_source
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Remove private source from build system.
    ::
    :: Parameters
    :: ----------
    :: 1ST argument (string): Name of the source to be removed.
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    set source_name=%~1

    :: Remove unused private sources
    if %build_system% == flit (
        call :exit_with_error_message "not implemented for flit yet!" 1
    )
    if %build_system% == pipenv (
        call :exit_with_error_message "not implemented for pipenv yet!" 1
    )
    if %build_system% == poetry (
        for /f %%i in ('.venv\Scripts\poetry config --list') do (
            if %%i == repositories.%source_name%.url (
                echo Remove %source_name% from source
                call %venv_name%\Scripts\poetry config --unset repositories.%source_name%
            )
        )
    )
    if %build_system% == setuptools (
        call :exit_with_error_message "not implemented for setuptools yet!" 1
    )

    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:install_run_dependencies
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Install run dependencies.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    :: Check if run dependencies are declared in the command line arguments.
    setlocal enabledelayedexpansion
    if %build_system% == flit (
        call :exit_with_error_message "not yet implemented for %build_system%!" 1
    )
    if %build_system% == pipenv (
        call :exit_with_error_message "not yet implemented for %build_system%!" 1
    )
    if %build_system% == poetry (
        if %install_mode% == default (
            call %venv_name%\Scripts\poetry install -vvv || ( echo Process ended with error & goto :end_with_error 1 )
        )
        if %install_mode% == pip (
            call %venv_name%\Scripts\poetry export -f requirements.txt --output requirements.txt --without-hashes --with-credentials -vvv || ( echo Process ended with error & goto :end_with_error 1 )
            call %venv_name%\Scripts\python -m pip install -r requirements.txt --verbose || ( echo Process ended with error & goto :end_with_error 1 )
        )
    )
    if %build_system% == setuptools (
        call :exit_with_error_message "not yet implemented for %build_system%!" 1
    )
    endlocal
    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:install_doc_dependencies
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Install doc dependencies.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    :: Check if doc dependencies are declared in the command line arguments.
    setlocal enabledelayedexpansion
    if exist requirements/requirements_doc.txt (
        call %venv_name%\Scripts\python -m pip install -r requirements/requirements_doc.txt || ( echo Process ended with error & goto :end_with_error 1 )
    ) else (
        call :exit_with_error_message "doc dependencies are missing (requirements/requirements_doc.txt)" 1
    )
    endlocal
    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:install_tests_dependencies
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Install tests dependencies.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------
    :: Check if tests dependencies are declared in the command line arguments.
    setlocal enabledelayedexpansion
    if exist requirements/requirements_tests.txt (
        call %venv_name%\Scripts\python -m pip install -r requirements/requirements_tests.txt || ( echo Process ended with error & goto :end_with_error 1 )
    ) else (
        call :exit_with_error_message "tests dependencies are missing (requirements/requirements_tests.txt)" 1
    )
    endlocal
    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:install_build_dependencies
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Install build dependencies.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    :: Check if build dependencies are declared in the command line arguments.
    setlocal enabledelayedexpansion
    if exist requirements/requirements_build.txt (
        call %venv_name%\Scripts\python -m pip install -r requirements/requirements_build.txt || ( echo Process ended with error & goto :end_with_error 1 )
    ) else (
        call :exit_with_error_message "tests dependencies are missing (requirements/requirements_build.txt)" 1
    )
    endlocal
    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:install_package
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Install package.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    setlocal EnableDelayedExpansion
    if %build_system% == flit (
        call :exit_with_error_message "not yer implemented for %build_system%!" 1
    )
    if %build_system% == pipenv (
        call :exit_with_error_message "not yer implemented for %build_system%!" 1
    )
    if %build_system% == poetry (
        if %install_mode% == pip (
            call %venv_name%\Scripts\python -m pip install build
            call %venv_name%\Scripts\python -m build || ( echo Process ended with error & goto :end_with_error 1 )
            for /f "tokens=*" %%g in ('dir /s /b dist\*.whl') do (set wheel=%%g)
            call %venv_name%\Scripts\python -m pip install !wheel! --extra-index-url https://%SOLUTIONS_PRIVATE_PYPI_PAT%@pkgs.dev.azure.com/pyansys/_packaging/ansys-solutions/pypi/simple/ || ( echo Process ended with error & goto :end_with_error 1 )
        )
    )
    if %build_system% == setuptools (
        call :exit_with_error_message "not yer implemented for %build_system%!" 1
    )
    endlocal
    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:check_if_string_contains_text
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Check if a string contains a substring.
    ::
    :: Parameters
    :: ----------
    :: 1st argument (string): String to search in.
    :: 2nd argument (string): Patterb to find in the string.
    ::
    :: Return
    :: ------
    :: result (boolean): returns true if the pattern exists in the string. False otherwise. 
    ::
    :: --------------------------------------------------------------
    set result=false
    set string=%~1
    set pattern=%~2
    call :reset_error
    echo "%string%" | find /i "%pattern%" > nul
    if %errorlevel% equ 0 (
        set result=true
    )
    set %3=%result%
    exit /b
:: --------------------------------------------------------------------------------------------------------------------

:reset_error
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Reset error.
    ::
    :: Parameters
    :: ----------
    :: None
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------
    exit /b 0
:: --------------------------------------------------------------------------------------------------------------------

:exit_with_error_message
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Show error message in terminal and exit with error code.
    ::
    :: Parameters
    :: ----------
    :: 1st argument (string): error message to display in double quotes.
    :: 2nd argument (int)   : exit code.
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    set error_message=%~1
    set exit_code=%~2

    echo.
    echo Error: %error_message% 
    echo Program fails with exit code %exit_code%.
    echo.
    goto :end_with_error

:: --------------------------------------------------------------------------------------------------------------------

:display_warning
    :: --------------------------------------------------------------
    :: Usage
    :: ----------
    :: Show warning message in terminal and continue the process.
    ::
    :: Parameters
    :: ----------
    :: 1st argument (string): warning message to display in double quotes.
    ::
    :: Return
    :: ------
    :: None
    ::
    :: --------------------------------------------------------------

    set warning_message=%~1

    echo.
    echo Warning: %warning_message%
    echo.
    exit /b 

:: --------------------------------------------------------------------------------------------------------------------

:: ================================================= [Initialization] =================================================

goto :init

goto :parse

:: ==================================================== [Execution] ===================================================

:main

    echo.
    echo ==============================================================================================
    echo Environment Setup
    echo ==============================================================================================
    echo.

    echo Start %DATE% %TIME%

    echo.
    echo Setup session --------------------------------------------------------------------------------
    echo.

    echo Virtual environement : %venv_name%
    echo Dependencies         : %dependencies%
    echo Build system         : %build_system%
    echo Build system version : %build_system_version%
    echo Install mode         : %install_mode%
    echo Private PyPI servers : %private_pypi_servers%
    echo Private repositories : %private_repositories%
    echo Clear workspace      : %clear_workspace%

    call :check_inputs

    echo Run dependencies     : %run_dependencies%
    echo Doc dependencies     : %doc_dependencies%
    echo Tests dependencies   : %tests_dependencies%
    echo Build dependencies   : %build_dependencies%

    if not %build_system_version% == * (
        set build_system_version===%build_system_version%
    ) else (
        set build_system_version=""
    )

    echo.
    echo Clean-up workspace ---------------------------------------------------------------------------
    echo.
    if %clear_workspace% == true (
        call :cleanup_workspace
    ) else (
        echo Skipped
    )

    echo.
    echo Create virtual environment -------------------------------------------------------------------
    echo.
    call python -m venv %venv_name%

    echo.
    echo Upgrade to latest pip version ----------------------------------------------------------------
    echo.
    call %venv_name%\Scripts\python -m pip install --upgrade pip

    echo.
    echo Install build system and tox -----------------------------------------------------------------
    echo.

    call %venv_name%\Scripts\python -m pip install --upgrade %build_system%%build_system_version% tox

    echo.
    echo Configure build system -----------------------------------------------------------------------
    echo.
    call :configure_build_system

    echo.
    echo Install dependencies -------------------------------------------------------------------------
    echo.
    if %run_dependencies% == true (
        call :install_run_dependencies
    ) else (
        echo Skipped
    )

    echo.
    echo Install doc dependencies ---------------------------------------------------------------------
    echo.
    if %doc_dependencies% == true (
        call :install_doc_dependencies
    ) else (
        echo Skipped
    )

    echo.
    echo Install tests dependencies -------------------------------------------------------------------
    echo.
    if %tests_dependencies% == true (
        call :install_tests_dependencies
    ) else (
        echo Skipped
    )

    echo.
    echo Install build dependencies -------------------------------------------------------------------
    echo.
    if %build_dependencies% == true (
        call :install_build_dependencies
    ) else (
        echo Skipped
    )

    echo.
    echo Install package ------------------------------------------------------------------------------
    echo.
    if %run_dependencies% == true (
        call :install_package
    ) else (
        echo Skipped
    )
    
    echo.
    echo You are all set! 
    echo Activate your environment with one these commands:
    echo    - For Windows CMD       : %venv_name%\Scripts\activate.bat
    echo    - For Windows Powershell: %venv_name%\Scripts\Activate.ps1
    echo Enjoy!
    echo.
    echo End %DATE% %TIME%
    echo.

    goto :end
:: --------------------------------------------------------------------------------------------------------------------
