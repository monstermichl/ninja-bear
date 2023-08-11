class TestConfig {
    static get myBoolean() { return true; }
    static get myInteger() { return 142; }
    static get myFloat() { return 322.0; }
    static get myDouble() { return 233.9; }
    static get myRegex() { return /Test Reg(E|e)x/; } /* Just another RegEx. */
    static get mySubstitutedString() { return 'Sometimes I just want to scream Hello World!'; }
}

module.exports = TestConfig
