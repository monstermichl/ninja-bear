rem Make sure the script is executed from the base directory even if it's called from somewhere else.
pushd %~dp0\..\..

rem Install required test packages.
python -m pip install coverage

rem Run unit tests.
python -m coverage run -m unittest || goto :_exit -1

rem Generate coverage report.
python -m coverage report

rem Go back to original directory.
_exit 0

:_exit
    popd    
    exit %1
