# Make sure the script is executed from the base directory even if it's called from somewhere else.
pushd "${0%/*}/../.." # https://stackoverflow.com/a/207966

# Run unit tests.
python3 -m unittest discover tests

# Go back to original directory.
popd
