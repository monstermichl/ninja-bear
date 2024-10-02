import os
from zipfile import ZipFile
from fileinput import FileInput
from ninja_bear.base.name_converter import NameConverter, NamingConventionType

language_name = input('Language name: ')
language_name_lower = NameConverter.convert(language_name, NamingConventionType.SNAKE_CASE).replace('_', '').strip()

# Make sure a language name got provided.
if not language_name:
    raise Exception('No language name provided')

language_name_lower_replace = input(f'Language name lower-case ({language_name_lower}): ').strip()
if language_name_lower_replace:
    language_name_lower = language_name_lower_replace

# Make sure a lowered language name got provided.
if not language_name_lower:
    raise Exception('No lowered language name provided')

file_extension = input('File extension: ').strip()

# Make sure a file extension got provided.
if not file_extension:
    raise Exception('No file extension provided')

repository_url = input('Repository URL (optinal): ').strip()

dir_name = os.path.dirname(__file__)
target_folder = f'ninja-bear-language-{language_name_lower}'
target_dir = os.path.join(dir_name, target_folder)
src_dir = os.path.join(target_dir, 'src')
module_folder = NameConverter.convert(target_folder, NamingConventionType.SNAKE_CASE)

# Extract template.
with ZipFile(os.path.join(dir_name, 'template.zip')) as zip:
    zip.extractall(target_dir)

# Start modifying scripts with corresponding settings.
replacements = [
    ['language-upper', language_name],
    ['language-lower', language_name_lower],
    ['file-extension', file_extension],
    ['repository-url', repository_url],
    ['module-folder', module_folder],
]
files = [
    ['setup.py'],
    ['src', 'ninja_bear_language', 'config.py'],
    ['src', 'ninja_bear_language', 'generator.py'],
    ['example', 'test-config.yaml'],
    ['tests', 'test.py'],
    ['README.md'],
]

# Iterate template files and replace corresponding strings.
for path in files:
    file_path = os.path.join(target_dir, *path)

    # Replace content directly in files (https://www.geeksforgeeks.org/how-to-search-and-replace-text-in-a-file-in-python/).
    if os.path.exists(file_path):
        with FileInput(file_path, inplace=True) as f:
            for line in f:
                for replacement in replacements:
                    line = line.replace(f'<{replacement[0]}>', replacement[1])
                print(line, end='')  # print prints to the file here (https://stackoverflow.com/a/76923807).

# Rename module folder.
os.rename(os.path.join(src_dir, 'ninja_bear_language'), os.path.join(src_dir, module_folder))
