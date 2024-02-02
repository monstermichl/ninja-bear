import argparse
from os import path

from .base.orchestrator import Orchestrator

_CONFIG_PARAMETER = 'config'
_OUTPUT_PARAMETER = 'output'
_DISTRIBUTE_PARAMETER = 'distribute'


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', f'--{_CONFIG_PARAMETER}', help='Path to configuration file', required=True, type=str)
    parser.add_argument('-o', f'--{_OUTPUT_PARAMETER}', help='Output location', required=False, type=str, default='.')
    parser.add_argument('-d', f'--{_DISTRIBUTE_PARAMETER}',
        help='Distribute the generated configs to the specified locations', required=False, action='store_true')

    args = parser.parse_args()

    # TODO: Might also strip backslashes.
    output_dir = f'{str(getattr(args, _OUTPUT_PARAMETER)).strip("/")}/' if hasattr(args, _OUTPUT_PARAMETER) else ''

    if output_dir and not path.isdir(output_dir):
        raise Exception(f'Output directory {output_dir} does not exist')
    
    config = Orchestrator.read_config(getattr(args, _CONFIG_PARAMETER))
    config.write(output_dir)

    if getattr(args, _DISTRIBUTE_PARAMETER):
        config.distribute()


if __name__ == '__main__':
    main()
