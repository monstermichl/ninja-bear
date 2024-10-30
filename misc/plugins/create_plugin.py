import datetime
import os
import re
import shutil
import sys
import pathlib

from os.path import join
from typing import Callable, List, Tuple
from fileinput import FileInput

# Add parent directory to path to be able to import from 'src' (https://www.geeksforgeeks.org/python-import-from-parent-directory/).
sys.path.append(str(pathlib.Path(os.path.dirname(__file__)).parent.parent.absolute()))

from src.ninja_bear.base.name_converter import NameConverter, NamingConventionType
from src.ninja_bear.base.info import VERSION

def create(
    type: str,
    requirements: List[str],
    dev_requirements: List[str],
    source_files: List[str],
    test_files: List[str],
    entry_point_module: str,
    entry_point_class: str,
    additional_replacements_callout: Callable[[], List[Tuple[str, str]]]=None
):
    type_capitalized = type.capitalize()
    type_lower = type.lower()
    type_name = input(f'{type_capitalized} name: ')
    type_name_lower = NameConverter.convert(type_name, NamingConventionType.SNAKE_CASE).replace('_', '').strip()
    replacements = []

    # Make sure a type name got provided.
    if not type_name:
        raise Exception('No {type_lower} name provided')

    type_name_lower_replace = input(f'{type_capitalized} name lower-case ({type_name_lower}): ').strip()
    if type_name_lower_replace:
        type_name_lower = type_name_lower_replace

    # Make sure a lowered type name got provided.
    if not type_name_lower:
        raise Exception('No lowered {type_lower} name provided')
    
    # Replace all special characters with underline.
    type_name_lower = re.sub(r'_+', '_', re.sub('[^a-z0-9]', '_', type_name_lower))
    
    if additional_replacements_callout:
        replacements.extend(additional_replacements_callout())

    author = input('Plugin author: ')

    # Make sure an author got provided.
    if not author:
        raise Exception('No name provided')

    author_real = input(f'License author ({author}): ')

    # Make sure a license author got provided.
    if not author_real:
        author_real = author

    repository_url = input('Repository URL (optional): ').strip()

    current_dir = os.path.dirname(__file__)
    plugin_name = f'ninja-bear-{type_lower}-{type_name_lower}'
    target_folder = plugin_name
    target_dir = join(current_dir, target_folder)
    src_dir = join(target_dir, 'src')
    plugin_dir = join(src_dir, 'ninja_bear_plugin')
    module_folder = NameConverter.convert(target_folder, NamingConventionType.SNAKE_CASE)
    templates_dir = join(current_dir, 'templates')
    template_files_dir = join(templates_dir, type_lower)

    # Create copy of base.
    shutil.copytree(join(templates_dir, 'base'), target_dir)

    # Copy required files.
    for file, target in [
        ('README.md', ''),
        ('test-config.yaml', 'example'),
        *map(lambda x: (x, plugin_dir), source_files),
        *map(lambda x: (x, 'tests'), test_files),
    ]:
        from_path = pathlib.Path(join(template_files_dir, file))
        to_path = join(target_dir, target);

        if from_path.is_file():
            shutil.copy(from_path, to_path)
        else:
            shutil.copytree(from_path, join(to_path, file))

    # Create requirements.txt.
    with open(join(target_dir, 'requirements.txt'), 'w') as f:
        f.writelines(requirements)

    # Helper function to create a requirements-string.
    def concat_requirements(requirements: List[str]) -> str:
        return ', '.join(map(lambda r: f'\'{r}\'', requirements))

    # Add additional replacements.
    replacements.extend([
        ('author', author),
        ('author-real', author_real),
        ('requirements', concat_requirements(requirements)),
        ('dev-requirements', concat_requirements(dev_requirements)),
        ('name-upper', type_name),
        ('name-lower', type_name_lower),
        ('plugin', plugin_name),
        ('repository-url', repository_url),
        ('module-folder', module_folder),
        ('module', entry_point_module),
        ('class', entry_point_class),
        ('type', type_lower),
        ('year', str(datetime.date.today().year)),
        ('ninja-bear-version', str(VERSION)),
    ])

    def substitute():
        # Iterate template files and replace corresponding strings (https://realpython.com/get-all-files-in-directory-python/#recursively-listing-with-rglob).
        for file_path in pathlib.Path(target_dir).rglob('*'):

            # Make sure it's actually a file.
            if file_path.is_file():
                # Replace content directly in files (https://www.geeksforgeeks.org/how-to-search-and-replace-text-in-a-file-in-python/).
                with FileInput(file_path, inplace=True) as f:
                    for line in f:
                        for replacement in replacements:
                            line = line.replace(f'<{replacement[0]}>', replacement[1])
                        print(line, end='')  # print prints to the file here (https://stackoverflow.com/a/76923807).

    # Substitute.
    substitute()

    # Rename module folder.
    os.rename(plugin_dir, join(src_dir, module_folder))


def create_language_plugin():
    def callout():
        file_extension = input('Language file extension: ').strip()

        # Make sure a file extension got provided.
        if not file_extension:
            raise Exception('No file extension provided')

        return [
            ('file-extension', file_extension),
        ]

    create(
        type='language',
        requirements=[],
        dev_requirements=[],
        source_files=['config.py', 'generator.py'],
        test_files=['test.py', 'compare_files'],
        entry_point_module='config',
        entry_point_class='Config',
        additional_replacements_callout=callout,
    )


def create_distributor_plugin():
    create(
        type='distributor',
        requirements=[],
        dev_requirements=[],
        source_files=['distributor.py'],
        test_files=['test.py'],
        entry_point_module='distributor',
        entry_point_class='Distributor',
    )


if __name__ == '__main__':
    def print_delimiter():
        print('----------------------------------------------------')

    plugins = [
        ['Language', create_language_plugin],
        ['Distributor', create_distributor_plugin],
    ]
    print_delimiter()

    for i, plugin in enumerate(plugins):
        print(f'{i + 1} - {plugin[0]}')
    selection = int(input('\nPlugin type: ')) - 1

    if selection >= len(plugins):
        print('Invalid selection')
    else:
        print()
        plugins[selection][1]()
    print_delimiter()
