# confluent
In times of distributed systems and en vogue micro-architecture it can get quite cumbersome to keep constants that are required by several components up-to-date and in sync. It can get especially hard when these components or services are written in different languages. *confluent* targets this issue by using a language neutral YAML configuration that lets you generate language specific config files in the style of classes and structs.

## Currently supported languages
- [x] Java
- [x] JavaScript
- [x] TypeScript
- [x] Python
- [x] C

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
from confluent import Orchestrator

# Create Orchestrator instance from file.
orchestrator = Orchestrator.read_config('test-config.yaml')

# Write configs to 'generated' directory.
orchestrator.write('generated')
```

## Example

### Configuration
```yaml
languages:
  # --- Common properties (valid for all languages) -------------------------
  # type            (required): Specifies the output language (java | javascript | typescript | python).
  #
  # file_naming     (optional): Specifies the file naming convention (snake | screaming_snake | camel | pascal | kebap). Defaults to the file-name without the extension.
  # property_naming (optional): Specifies the property naming convention (snake | screaming_snake | camel | pascal | kebap).
  # type_naming     (optional): Specifies the naming convention for the generated type (snake | screaming_snake | camel | pascal | kebap). The default value is language specific.
  # indent          (optional): Specifies the amount of spaces before each constant. Defaults to 4.
  # -------------------------------------------------------------------------

  # --- Java specific properties --------------------------------------------
  # package (required): Specifies the Java package name.
  # -------------------------------------------------------------------------
  - type: java
    file_naming: pascal
    type_naming: pascal
    package: my.test.package

  # --- JavaScript/TypeScript specific properties ---------------------------
  # export (optional): Specifies how to export the class (esm | common_js | none). Defaults to esm.
  # -------------------------------------------------------------------------
  - type: javascript
    file_naming: screaming_snake
    indent: 4
    export: common_js

  - type: typescript
    indent: 4
    export: esm

  # -------------------------------------------------------------------------
  - type: python
    file_naming: snake
    property_naming: screaming_snake

  # -------------------------------------------------------------------------
  - type: c
    file_naming: snake
    property_naming: pascal

properties:
  # -------------------------------------------------------------------------
  # type    (required): Specifies the constant data type (bool | int | float | double | string | regex).
  # name    (required): Specifies the constant's name.
  # value   (required): Specifies the constant's value.
  #
  # comment (optional): Adds an extra comment to the constant.
  # hidden  (optional): Constants serves as helper and will not be written to the final result.
  # -------------------------------------------------------------------------

  - type: bool
    name: myBoolean
    value: true

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
#### Java
```java
package my.test.package;

// Generated with confluent v0.0.1 (https://pypi.org/project/confluent/).
public class TestConfig {
    public final static boolean myBoolean = true;
    public final static int myInteger = 142;
    public final static float myFloat = 322.0f;
    public final static double myDouble = 233.9d;
    public final static String myRegex = "Test Reg(E|e)x"; // Just another RegEx.
    public final static String mySubstitutedString = "Sometimes I just want to scream Hello World!";
}
```

#### JavaScript
```javascript
// Generated with confluent v0.0.1 (https://pypi.org/project/confluent/).
class TestConfig {
    static get myBoolean() { return true; }
    static get myInteger() { return 142; }
    static get myFloat() { return 322.0; }
    static get myDouble() { return 233.9; }
    static get myRegex() { return /Test Reg(E|e)x/; } // Just another RegEx.
    static get mySubstitutedString() { return 'Sometimes I just want to scream Hello World!'; }
}
module.exports = TestConfig
```

#### TypeScript
```typescript
// Generated with confluent v0.0.1 (https://pypi.org/project/confluent/).
export class TestConfig {
    public static readonly myBoolean = true;
    public static readonly myInteger = 142;
    public static readonly myFloat = 322.0;
    public static readonly myDouble = 233.9;
    public static readonly myRegex = /Test Reg(E|e)x/; // Just another RegEx.
    public static readonly mySubstitutedString = 'Sometimes I just want to scream Hello World!';
}
```

#### Python
```python
# Generated with confluent v0.0.1 (https://pypi.org/project/confluent/).
class TestConfig:
    MY_BOOLEAN = True
    MY_INTEGER = 142
    MY_FLOAT = 322.0
    MY_DOUBLE = 233.9
    MY_REGEX = r'Test Reg(E|e)x'  # Just another RegEx.
    MY_SUBSTITUTED_STRING = 'Sometimes I just want to scream Hello World!'
```

#### C
```c
#ifndef TEST_CONFIG_H
#define TEST_CONFIG_H

/* Generated with confluent v0.0.1 (https://pypi.org/project/confluent/). */
const struct {
    unsigned char myBoolean;
    int myInteger;
    float myFloat;
    double myDouble;
    char* myRegex; /* Just another RegEx. */
    char* mySubstitutedString;
} TestConfig = {
    1,
    142,
    322.0f,
    233.9,
    "Test Reg(E|e)x",
    "Sometimes I just want to scream Hello World!",
};

#endif  /* TEST_CONFIG_H */
```

## How to participate
If you feel that there's a need for another language, feel free to add it. For detailed information how to add support for a new language, please refer to [README.md](https://github.com/monstermichl/confluent/tree/main/misc/language_support/README.md).
