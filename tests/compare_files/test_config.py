from enum import Enum


class TestConfig(Enum):
    myBoolean = True
    myInteger = 142
    myFloat = 322.0
    myDouble = 233.9
    myRegex = r'Test Reg(E|e)x'  # Just another RegEx.
    mySubstitutedString = 'Sometimes I just want to scream Hello World!'
