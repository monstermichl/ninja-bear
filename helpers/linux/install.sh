# Make sure the script is executed in the example directory even if it's called from somewhere else.
pushd "${0%/*}/../.." # https://stackoverflow.com/a/207966

# Build locally.
python3 setup.py sdist bdist_wheel

# Install via pip.
python3 -m pip install .

# Go back to original directory.
popd
