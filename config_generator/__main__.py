import argparse
from os import path

from .generator import ConfigGenerator

from .base.config import Config

_CONFIG_PARAMETER = 'config'
_OUTPUT_PARAMETER = 'output'


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', f'--{_CONFIG_PARAMETER}', help='Path to configuration file', required=True, type=str)
    parser.add_argument('-o', f'--{_OUTPUT_PARAMETER}', help='Output location', required=False, type=str)

    args = parser.parse_args()
    output_dir = f'{str(getattr(args, _OUTPUT_PARAMETER)).strip("/")}/' if hasattr(args, _OUTPUT_PARAMETER) else ''  # TODO: Might also strip backslashes.

    if output_dir and not path.isdir(output_dir):
        raise Exception(f'Output directory {output_dir} does not exist')
    
    language_configs = ConfigGenerator.read_config(getattr(args, _CONFIG_PARAMETER))
    
    for language_config in language_configs:
        generatedCode = language_config.dump()

        with open(f'{output_dir}{language_config.config_name}.{language_config.config_extension}', 'w') as f:
            f.write(generatedCode)


if __name__ == '__main__':
    main()
