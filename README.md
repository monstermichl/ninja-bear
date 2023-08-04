# config-generator
Generator to build config files in the style of classes for different languages.

## Currently supported languages
- [x] TypeScript
- [x] Java

## Usage
config-generator can either be used via the commandline or called from within Python and depends on the configuration passed to it.

### Commandline
```bash
python3 -m config-generator -c example/test-config.yaml -o example
```

## Configuration
For details about the configuration file, please check *example/test-config.yaml*. All possible values are described there. Basically the configuration consists of a *languages*- and a *properties*-section. The first one describes language specific properties e.g. for which language to generate, which naming convention to use for the output file or how much indent to use. The *properties*-section defines the actual values whereis the following types are supported: *bool*, *int*, *float*, *double*, *string* and *regex*. Properties can also act as helpers for other properties which don't need to be written to the final config-file. These properties can be marked as *hidden*. Acting as a helper-property means that it defines a value which other properties can use as substitute values referencing them via *${property-name}*.

### Example

```yaml
languages:
  - type: typescript
    file_naming: kebap
    indent: 4

properties:
  - type: string
    name: myString
    value: Hello World
    hidden: true

  - type: string
    name: mySubstitutedString
    value: Sometimes I just want to scream ${myString}!
```

```typescript
export class TestConfig {
    public static readonly mySubstitutedString = 'Sometimes I just want to scream Hello World!';
}
```
