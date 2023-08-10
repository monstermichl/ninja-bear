@echo off

rem Make sure the script is executed in the example directory even if it's called from somewhere else.
pushd %~dp0\..\..

rem Install required build packages.
python -m pip install build wheel

rem Build locally.
python setup.py sdist bdist_wheel

rem Install this module.
python -m pip install .

rem Go back to original directory.
popd
