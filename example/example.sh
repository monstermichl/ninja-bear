# Make sure the script is executed in the example directory even if it's called from somewhere else.
pushd .

OUTPUT_DIR=generated

# Create output dir.
if [ ! -d ${OUTPUT_DIR} ]; then
    mkdir ${OUTPUT_DIR}
fi

# Generate Java and Typescript files from test config.
python3 -m config_generator -c test-config.yaml -o generated

# Go back to original directory.
popd
