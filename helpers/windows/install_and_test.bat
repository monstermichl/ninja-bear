rem Make sure the script is executed from the current directory even if it's called from somewhere else.
pushd %~dp0

install.bat
test.bat

rem Go back to original directory.
popd
