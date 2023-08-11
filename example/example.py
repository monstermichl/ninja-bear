from confluent import Arranger

# Create arranger instance from file.
arranger = Arranger.read_config('test-config.yaml')

# Write configs to 'generated* directory.
arranger.write('generated')
