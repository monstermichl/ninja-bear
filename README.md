# confluent
In times of distributed systems and en vogue micro-architecture it can get quite cumbersome to keep constants that are required by several components up-to-date and in sync. It can get especially hard when these components or services are written in different languages. *confluent* targets this issue by using a language neutral YAML configuration that lets you generate language specific config files in the style of classes and structs.

## Currently supported languages
- [x] Java
- [x] JavaScript
- [x] TypeScript
- [x] Python

## Installation
```bash
python -m pip install confluent  # On Linux use python3.
```

## Configuration
For details about the configuration file, please check *example/test-config.yaml*. All possible values are described there. Basically the configuration consists of a *languages*- and a *properties*-section. The first one describes language specific properties e.g. for which language to generate, which naming convention to use for the output file or how much indent to use. The *properties*-section defines the actual values whereis the following types are supported: *bool*, *int*, *float*, *double*, *string* and *regex*. Properties can also act as helpers for other properties which don't need to be written to the final config-file. These properties can be marked as *hidden*. Acting as a helper-property means that it defines a value which other properties can use as substitute values referencing them via *${property-name}*.

## Usage
### Commandline
```bash
python3 -m confluent -c test-config.yaml -o generated
```

### Script
```python
from confluent import Generator

# Get configurations from file.
configs = Generator.read_config('test-config.yaml')

for config in configs:
    # Write config to the generated directory.
    with open(f'generated/{config.config_info.file_name_full}', 'w') as f:
        f.write(config.dump())
```

## Example

### Configuration
```yaml
languages:
  - type: java                        # Specifies the output language. Supported values are: java | javascript | typescript | python
    file_naming: pascal               # (Optional) Specifies the file naming convention. Supported values: snake | screaming_snake | camel | pascal | kebap
    property_naming: screaming_snake  # (Optional) Specifies the property naming convention. Supported values: snake | screaming_snake | camel | pascal | kebap
    indent: 4                         # (Optional) Specifies the amount of spaces before each constant.
    package: my.test.package          # (Java specific) For Java, a package name must be specified.

  - type: javascript
    file_naming: screaming_snake
    indent: 4

  - type: typescript
    file_naming: kebap
    indent: 4

  - type: python
    file_naming: snake
    property_naming: screaming_snake
    indent: 4

properties:
  - type: bool       # Specifies the constant data type. Supported values: bool | int | float | double | string | regex
    name: myBoolean  # Specifies the constant's name.
    value: true      # Specifies the constant's value.

  - type: int
    name: myInteger
    value: 142

  - type: float
    name: myFloat
    value: 322f  # Float with float specifier. However, an additional specifier (f) is not required and will be trimmed.

  - type: double
    name: myDouble
    value: 233.9

  - type: string
    name: myString
    value: Hello World
    hidden: true  # If a property should act as a helper but should not be written to the generated file, it must be marked as 'hidden'.

  - type: regex
    name: myRegex
    value: Test Reg(E|e)x
    comment: Just another RegEx.  # Variables can be described using the comment property.

  - type: string
    name: mySubstitutedString
    value: Sometimes I just want to scream ${myString}!
```

### Output
```java
package my.test.package;

public class TestConfig {
    public final static boolean MY_BOOLEAN = true;
    public final static int MY_INTEGER = 142;
    public final static float MY_FLOAT = 322.0f;
    public final static double MY_DOUBLE = 233.9d;
    public final static String MY_REGEX = "Test Reg(E|e)x"; /* Just another RegEx. */
    public final static String MY_SUBSTITUTED_STRING = "Sometimes I just want to scream Hello World!";
}
```

```javascript
export class TestConfig {
    static get myBoolean() { return true; }
    static get myInteger() { return 142; }
    static get myFloat() { return 322.0; }
    static get myDouble() { return 233.9; }
    static get myRegex() { return /Test Reg(E|e)x/; } /* Just another RegEx. */
    static get mySubstitutedString() { return 'Sometimes I just want to scream Hello World!'; }
}
```

```typescript
export class TestConfig {
    public static readonly myBoolean = true;
    public static readonly myInteger = 142;
    public static readonly myFloat = 322.0;
    public static readonly myDouble = 233.9;
    public static readonly myRegex = /Test Reg(E|e)x/; /* Just another RegEx. */
    public static readonly mySubstitutedString = 'Sometimes I just want to scream Hello World!';
}
```

```python
from enum import Enum


class TestConfig(Enum):
    MY_BOOLEAN = True
    MY_INTEGER = 142
    MY_FLOAT = 322.0
    MY_DOUBLE = 233.9
    MY_REGEX = r'Test Reg(E|e)x'  # Just another RegEx.
    MY_SUBSTITUTED_STRING = 'Sometimes I just want to scream Hello World!'
```

## How to participate
If you feel that there's a need for another language, feel free to add it. For detailed information how to add support for a new language, please refer to [README.md](https://github.com/monstermichl/confluent/misc/language_support/README.md).
