from confluent import Orchestrator

# Create orchestrator instance from file.
orchestrator = Orchestrator.read_config('test-config.yaml')

# Write configs to 'generated' directory.
orchestrator.write('generated')
