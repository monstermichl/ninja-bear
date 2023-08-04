@echo off

rem Make sure the script is executed in the example directory even if it's called from somewhere else.
pushd %~dp0

rem Install requirements.
python -m pip install -r requirements.txt

rem Install this module.
python -m pip install .

rem Go back to original directory.
popd
