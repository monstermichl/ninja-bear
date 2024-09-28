// Generated with ninja-bear v0.2.0 (https://pypi.org/project/ninja-bear/).
class TestConfig {
    static get myBoolean() { return true; }
    static get myInteger() { return 142; }
    static get myFloat() { return 322.0; }
    static get myCombinedFloat() { return 45724.0; }
    static get myDouble() { return 233.9; }
    static get myRegex() { return /Test Reg(E|e)x/; } // Just another RegEx.
    static get mySubstitutedString() { return 'Sometimes I just want to scream Hello World!'; }
    static get myCombinedString() { return 'I am telling you that this string got included from test-include.yaml.'; }
}
module.exports = TestConfig
