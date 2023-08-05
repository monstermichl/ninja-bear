# Make sure the script is executed in the example directory even if it's called from somewhere else.
pushd "${0%/*}" # https://stackoverflow.com/a/207966

# Install this module.
python3 -m pip install .

# Go back to original directory.
popd
