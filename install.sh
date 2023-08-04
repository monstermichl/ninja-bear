# Make sure the script is executed in the example directory even if it's called from somewhere else.
pushd .

# Install requirements.
pip3 install -r requirements.txt

# Install this module.
pip3 install .

# Go back to original directory.
popd
