from ninja_bear import Orchestrator

# Create orchestrator instance from file.
orchestrator = Orchestrator.read_config('test-config.yaml')

# Write constants to 'generated' directory.
orchestrator.write('generated')
