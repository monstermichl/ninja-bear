@echo off

rem Make sure the script is executed in the example directory even if it's called from somewhere else.
pushd %~dp0\..\..

rem Install required build packages.
python -m pip install build wheel || call :_exit -1

rem Build locally.
python setup.py sdist bdist_wheel || call :_exit -2

rem Install this module.
python -m pip install . || call :_exit -3

rem Exit script successfully.
call :_exit 0

:_exit
    popd
    exit /B %1
