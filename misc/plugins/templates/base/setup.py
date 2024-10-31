from pathlib import Path
from setuptools import setup, find_packages

# Setup process taken from here: https://www.freecodecamp.org/news/build-your-first-python-package/.

DESCRIPTION = '<name-upper> <type> support for ninja-bear'
LONG_DESCRIPTION = Path(__file__).parent.absolute().joinpath('README.md').read_text('utf-8')

setup(
    name='<plugin>', 
    version='0.1.0',
    author='<author>',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    py_modules=['<module-folder>'],
    entry_points = {
        'ninja_bear_<type>_<name-lower>': ['config=<module-folder>.<module>:<class>']
    },
    install_requires=[
        <requirements>
    ],
    extras_require={
        'dev': [
            'ninja-bear>=<ninja-bear-version>',
            'wheel>=0.41.1',
            'twine>=4.0.2',
            'ruff>=0.0.47',
            'coverage>=7.2.7',
            <dev-requirements>
        ],
    },
    python_requires='>=3.10',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    url='<repository-url>',
    keywords=[
        'ninja-bear',
        'plugin',
        '<type>',
        '<name-lower>',
    ],
)
