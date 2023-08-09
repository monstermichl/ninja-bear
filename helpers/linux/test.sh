# Make sure the script is executed from the base directory even if it's called from somewhere else.
pushd "${0%/*}/../.." # https://stackoverflow.com/a/207966

function _exit() {
    popd
    exit $1
}

# Run unit tests.
python3 -m coverage run -m unittest || _exit -1

# Generate coverage report.
python3 -m coverage html

# Go back to original directory.
_exit 0
