from enum import Enum
import re


class NamingConventionType(Enum):
    SNAKE_CASE = 0
    SCREAMING_SNAKE_CASE = 1
    CAMEL_CASE = 2
    PASCAL_CASE = 3
    KEBAP_CASE = 4


class NameConverter:

    @staticmethod
    def convert(name: str, type: NamingConventionType) -> str:
        UNDERLINE = '_'

        # Handle Camel- or Pascal-cased strings by replacing uppercase letters with
        # lowercase and add an underline in front.
        name = re.sub(r'[A-Z]', lambda match: f'{UNDERLINE}{match.group(0).lower()}', name).lstrip(UNDERLINE)

        # Replace all special characters by underline for easier further processing.
        name = re.sub(r'\W+', UNDERLINE, name)

        match type:
            case NamingConventionType.SNAKE_CASE:
                name = name.lower()
            case NamingConventionType.SCREAMING_SNAKE_CASE:
                name = name.upper()
            case NamingConventionType.CAMEL_CASE | NamingConventionType.PASCAL_CASE:
                # Replace all special characters followed by a letter by the uppercase version of the letter.
                compare_name = ''
                while compare_name != name:
                    compare_name = name
                    name = re.sub(rf'{UNDERLINE}+([a-zA-Z0-9])', lambda match: match.group(1).upper(), name)  # Thanks for the hint: https://stackoverflow.com/a/8934655.

                # If Pascal-case, uppercase the first letter.
                if type == NamingConventionType.PASCAL_CASE:
                    name = f'{name[0].upper()}{name[1:]}'
            case NamingConventionType.KEBAP_CASE:
                name = re.sub(rf'{UNDERLINE}+', '-', name)
            case _:
                raise Exception('Unknown naming type')
            
        return name
