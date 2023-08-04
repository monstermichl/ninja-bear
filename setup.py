from pathlib import Path
from setuptools import setup, find_packages

# Setup process taken from here: https://www.freecodecamp.org/news/build-your-first-python-package/.

VERSION = '0.0.1' 
DESCRIPTION = 'Generator to build config files in the style of classes for different languages.'
LONG_DESCRIPTION = Path(__file__).parent.absolute().joinpath('README.md').read_text()

setup(
        name='config-generator', 
        version=VERSION,
        author='Michel Vouillarmet',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        python_requires='>=3.10',
        classifiers= [
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ]
)
