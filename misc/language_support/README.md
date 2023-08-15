# How to add support for a new language
So there's a language you use which is not yet supported and you want to add it yourself? Alright, lets dive right into it. Here are the steps you need to take to add support for a new language.

## Fork the project
First of all, fork the project. This makes sure that there's no messing around on the main branch. Did that? Lets move on.

## Add a new language type
Open up *src/confluent/base/language_type.py* and add the language you want to support.

```python
class LanguageType(IntEnum):
    """
    Enum of all supported languages.
    """
    JAVA = 1
    JAVASCRIPT = auto()
    TYPESCRIPT = auto()
    PYTHON = auto()
    .
    .
    .
    MY_LANGUAGE = auto()  # The auto() function makes sure that all entries have a unique value.
```

## Add a new language generator
Create a new generator class within *src/confluent/generators* (e.g., *my_language_generator.py*) which inherits from [*GeneratorBase*](https://github.com/monstermichl/confluent/blob/main/src/confluent/base/generator_base.py) and implements the required **abstract** methods (a template can be found under [*misc/language_support/templates*](https://github.com/monstermichl/confluent/tree/main/misc/language_support/templates). (Hopefully I don't have to mention that you should not name it "my_language..." ;) ). This class is the actual generator which holds the information how the class/struct and the properties will look like. **HINT:** If special handling for specific properties is required (e.g., see 'package' in JavaGenerator), implement it in the constructor, not in the methods responsible for the dump (abstract methods).

```python
class MyLanguageGenerator(GeneratorBase):
    """
    MyLanguage specific generator. For more information about the generator methods, refer to GeneratorBase.
    """

    def _default_type_naming_convention(self) -> NamingConventionType:
        return NamingConventionType.PASCAL_CASE

    def _before_type(self) -> str:
        return f'comment: My langauge specific struct, bruh.\n\n'

    def _property_before_type(self, property: Property) -> str:
        return ''

    def _start_type(self, type_name: str) -> str:
        return f'class_start {type_name}'

    def _property_in_type(self, property: Property) -> str:
        match property.type:
            case PropertyType.BOOL:
                type = 'boolean'
                value = 1 if property.value else 0
            case PropertyType.INT:
            case PropertyType.FLOAT:
            case PropertyType.DOUBLE:
                value = property.value
            case PropertyType.STRING | PropertyType.REGEX:
                type = 'String'
                value = property.value.replace('\\', '\\\\')
                value = f'"{value}"'  # Wrap in quotes.
            case _:
                raise Exception('Unknown type')

        return f'const {property.name}: {type} = {value};'

    def _property_comment(self, comment: str) -> str:
        return f' comment: {comment}'

    def _end_type(self) -> str:
        return 'class_end'

    def _property_after_type(self, property: Property) -> str:
        return ''

    def _after_type(self) -> str:
        return ''
```

## Add a new language config
Create a new config class within *src/confluent/language_configs* (e.g., *my_language_configs.py*) which inherits from [*LanguageConfigBase*](https://github.com/monstermichl/confluent/blob/main/src/confluent/base/language_config_base.py) and implements the required **abstract** methods (a template can be found under [*misc/language_support/templates*](https://github.com/monstermichl/confluent/tree/main/misc/language_support/templates)). The language config encapsulates all the necessary information to create a config file (e.g., the language type,the config extension, which generator to use, ...).

```python
class MyLanguageConfig(LanguageConfigBase):
    """
    MyLanguage specific config. For more information about the config methods, refer to LanguageConfigBase.
    """

    def __init__(
        self,
        config_name: str,
        properties: List[Property],
        indent: int = None,
        naming_conventions: LanguageConfigNamingConventions = None,
        additional_props = {},
    ):
        super().__init__(
            config_name,
            LanguageType.MY_LANGUAGE,  # Use the language type (LanguageType) set up two steps before.
            'ml',
            MyLanguageGenerator,  # Use the generator class created in the previous step.
            properties,
            indent,
            naming_conventions,
            additional_props,
        )
```

## Glue everything together
At this point all required classes are setup and implemented. We now need to tell the [Config class](https://github.com/monstermichl/confluent/blob/main/src/confluent/base/config.py) that there's a new language in town. Open up *src/confluent/base/config_language_mapping.py* and add your newly created language components to the list returned by *get_mappings*.

```python
@staticmethod
def get_mappings() -> List[ConfigLanguageMapping]:
    """
    Returns a list of all valid language mappings. IMPORTANT: This is where all the mappings for
    supported languages go. If it's not included here, it's not being supported by the Config class.

    :return: List of supported languages.
    :rtype:  List[ConfigLanguageMapping]
    """
    return [
        ConfigLanguageMapping('java', LanguageType.JAVA, JavaConfig),
        ConfigLanguageMapping('javascript', LanguageType.JAVASCRIPT, JavascriptConfig),
        ConfigLanguageMapping('typescript', LanguageType.TYPESCRIPT, TypescriptConfig),
        ConfigLanguageMapping('python', LanguageType.PYTHON, PythonConfig),
        ConfigLanguageMapping('my_language', LanguageType.MY_LANGUAGE, MyLanguageConfig),
    ]
```

## Wrap up
That's it! You successfully added support for a new language. Now here is where it gets tedious but yes, this stuff has also to be done.

### Add your language to test-config.yaml
As test-config.yaml serves as the documentation for what's supported, make sure your language is added to it (as an example and under common language properties' type, where the supported languages are listed).

```yaml
languages:
  # --- Common properties (valid for all languages) -------------------------
  # type            (required): Specifies the output language (java | javascript | typescript | python | c | go).
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

  .
  .
  .

  # --- MyLanguage specific properties --------------------------------------
  # fun_factor (optional): Define how much fun the generated config shall be.
  # -------------------------------------------------------------------------
  - type: my_language  # IMPORTANT: Also add my_language to the list of supported languages (see Common properties -> type).
    file_naming: camel
    indent: 4
    fun_factor: 5
```

Afterwards, install *confluent* from the local project to test if your implementation works as expected (you might need to uninstall your current installation of *confluent* first). This can either be done by building and running the project manually or by running the *install.sh/bat* script from the *helpers* directory. If you want to setup everything manually, please have a look into the *install.sh/bat* script how it's done there.

If the installation passed successfully, run your prefered version of the example script from the *example* folder to generate the example config files from *test-config.yaml* with your freshly added language.

If your desired config file was created, CONGRATULATIONS! your implementation was successful :) If it wasn't, usually an error gets thrown which provides a clear description where the generation process went wrong. Just recapitulate the steps how to create support for a new language. If you're still having troubles getting it to work, feel free to open an issue at https://github.com/monstermichl/confluent/issues.

### Add your language to the unit tests
If everything went well so far, copy the generated example config for your language from *example* to *tests/compare_files*. This serves as the blueprint for testing your language. Therefore, **please make absolutely sure, that this is how you want your language output to look like.** Then open up *tests/test_generator.py* and add your language validation to the *_evaluate_configs* function.

```python
def _evaluate_configs(self, configs: List[LanguageConfigBase]):
    checks = [
        # Check Java config.
        [self._evaluate_java_properties, 'TestConfig'],

        # Check JavaScript config.
        [self._evaluate_javascript_properties, 'TEST_CONFIG'],

        # Check TypeScript config.
        [self._evaluate_typescript_properties, 'test-config'],

        # Check Python config.
        [self._evaluate_python_properties, 'test_config'],

        .
        .
        .

        # Check MyLanguage config.
        [self._evaluate_my_language_properties, 'testConfig'],
    ]

.
.
.

def _evaluate_my_language_properties(self, config: MyLanguageConfig, name: str):
    self._evaluate_common_properties(config, 'ml', name, LanguageType.MY_LANGUAGE, MyLanguageConfig)
```

Run *test.sh/bat* from the *helpers* directory and make sure all tests pass and the coverage is over 90%.

## Add your language to README.md
Make sure users know that the language is supported by adding it to the list of supported languages, updating the test-config and adding the example output to the README.md file (have a look how it's done for other languages).

## Create a Pull-Request
Merge the main branch into your branch, resolve possibly arising merge conflicts and create a pull-request on Github.
