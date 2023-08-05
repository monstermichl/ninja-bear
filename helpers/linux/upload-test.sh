# Make sure the script is executed from the base directory even if it's called from somewhere else.
pushd "${0%/*}/../.." # https://stackoverflow.com/a/207966

# Builds the required distribution files. If this doesn't work correctly,
# make sure wheel is installed -> python3 - m pip install wheel
python3 setup.py sdist bdist_wheel

# Upload to https://test.pypi.org.
python3 -m twine upload --repository testpypi dist/*

# Go back to original directory.
popd
