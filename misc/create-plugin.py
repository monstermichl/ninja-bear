import inspect
import os
import sys
import pathlib
from typing import Callable, List, Tuple
from zipfile import ZipFile
from fileinput import FileInput

# Add parent directory to path to be able to import from 'src' (https://www.geeksforgeeks.org/python-import-from-parent-directory/).
sys.path.append(str(pathlib.Path(os.path.dirname(__file__)).parent.absolute()))

from src.ninja_bear.base.name_converter import NameConverter, NamingConventionType

def create(type: str, additional_replacements_callout: Callable[[], List[Tuple[str, str]]]=None):
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
    
    if additional_replacements_callout:
        replacements.extend(additional_replacements_callout())

    repository_url = input('Repository URL (optional): ').strip()

    dir_name = os.path.dirname(__file__)
    target_folder = f'ninja-bear-{type_lower}-{type_name_lower}'
    target_dir = os.path.join(dir_name, target_folder)
    src_dir = os.path.join(target_dir, 'src')
    module_folder = NameConverter.convert(target_folder, NamingConventionType.SNAKE_CASE)

    # Extract template.
    with ZipFile(os.path.join(dir_name, f'{type_lower}-template.zip')) as zip:
        zip.extractall(target_dir)

    # Add additional replacements.
    replacements.extend([
        (f'{type_lower}-upper', type_name),
        (f'{type_lower}-lower', type_name_lower),
        ('repository-url', repository_url),
        ('module-folder', module_folder),
    ])

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

    # Rename module folder.
    os.rename(os.path.join(src_dir, f'ninja_bear_{type_lower}'), os.path.join(src_dir, module_folder))


def create_language_plugin():
    def callout():
        file_extension = input('Language file extension: ').strip()

        # Make sure a file extension got provided.
        if not file_extension:
            raise Exception('No file extension provided')

        return [
            ('file-extension', file_extension),
        ]

    create('language', callout)


def create_distributor_plugin():
    create('distributor')


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
