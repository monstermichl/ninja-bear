# ninja-bear 🥷🐻
In times of distributed systems and en vogue micro-architecture it can get quite cumbersome to keep constants that are required by several components up-to-date and in sync. It can get especially hard when these components or services are written in different languages. ninja-bear targets this issue by using a language neutral YAML configuration that lets you generate language specific constants-files.

## Concept
ninja-bear uses a plugin-based approach in which each language and distributor is an independend Python module. This gives developers a high amount of flexibility by letting them define and publish their own languages and distributors without the need to modify ninja-bear directly.

## Installation
```bash
pip install ninja-bear
```

## Example
Lets have a look at a simple example to see what *ninja-bear* can do for you.

The example YAML file contains a property named *greeting* with the value "Hello World". Config files shall be generated for [TypeScript](https://pypi.org/project/ninja-bear-language-typescript/), [Python](https://pypi.org/project/ninja-bear-language-python/) and [C](https://pypi.org/project/ninja-bear-language-c/) (using the corresponding plugins). In case of *C*, the value shall be changed to *"Hello Mars"* and the file shall be distributed to Git using the [ninja-bear-distributor-git](https://pypi.org/project/ninja-bear-distributor-git/) plugin.

For detailed configuration information, please check [test-config.yaml](https://github.com/monstermichl/ninja-bear/blob/main/example/test-config.yaml). All possible values are described there.

### Input (readme-config.yaml)
```yaml
# -----------------------------------------------------------------------------
# This section defines languages and properties which are usually the settings
# that you'll use the most.
# -----------------------------------------------------------------------------
languages:
  - language: typescript
    property_naming: screaming-snake
    export: esm

  - language: python
    file_naming: snake
    property_naming: screaming-snake

  - language: c
    file_naming: snake
    property_naming: pascal

    transformers:
      - mars-transformer

    distributors:
      - git-distributor

properties:
  - type: string
    name: greeting
    value: Hello World

# -----------------------------------------------------------------------------
# This sections defines the available transformers and distributors. They are
# are used if property values need to be transformed before they get written
# or if specific language constants shall be distributed. To use a transformer
# and/or a distributor, its alias needs to be used in the language section
# (refer to c-example).
# -----------------------------------------------------------------------------
transformers:
  - transformer: |
      value = 'Hello Mars'
    as: mars-transformer

distributors:
  - distributor: git
    as: git-distributor
```

### Execute ninja-bear
```bash
# -d is used to distribute the C-file to Git.
ninja-bear -c readme-config.yaml -d
```

### Output (readme-config.ts)
```typescript
export const ReadmeConfig = {
    GREETING: 'Hello World',
} as const;
```

### Output (readme_config.py)
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ReadmeConfig:
    GREETING = 'Hello World'
```

### Output (readme_config.h)
```c
#ifndef README_CONFIG_H
#define README_CONFIG_H

const struct {
    char Greeting[11];
} ReadmeConfig = {
    "Hello Mars",
};

#endif /* README_CONFIG_H */
```

## Usage
### Commandline
```bash
ninja-bear -c test-config.yaml -o generated
```

### Script
```python
from ninja_bear import Orchestrator

# Create Orchestrator instance from file.
orchestrator = Orchestrator.read_config('test-config.yaml')

# Write constants to 'generated' directory.
orchestrator.write('generated')

# Distribute constants (if required).
orchestrator.distribute()
```

## Create a plugin
To create a new plugin, clone the repository, run the [create_plugin.py](https://github.com/monstermichl/ninja-bear/blob/main/misc/plugins/create_plugin.py) script and select the corresponding plugin type. The script guides you through the required steps and creates a new folder (e.g. ninja-bear-language-examplescript), which contains all necessary files to get started. All files that require some implementation contain the comment **"TODO: Implement"**. The method comments contain information about what to implement. To install and test the plugin, scripts can be found in the *helpers* directory.
