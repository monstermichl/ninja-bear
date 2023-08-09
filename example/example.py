from confluent import Generator

# Get configurations from file.
configs = Generator.read_config('test-config.yaml')

for config in configs:
    # Write config to the generated directory.
    with open(f'generated/{config.config_info.file_name_full}', 'w') as f:
        f.write(config.dump())
