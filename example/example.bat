@echo off

rem Make sure the script is executed in the example directory even if it's called from somewhere else.
pushd %~dp0

rem Create output dir.
set OUTPUT_DIR=generated
if not exist %OUTPUT_DIR% (
    mkdir %OUTPUT_DIR%
)

rem Generate Java and Typescript files from test config.
python -m config-generator -c test-config.yaml -o generated

rem Go back to original directory.
popd
