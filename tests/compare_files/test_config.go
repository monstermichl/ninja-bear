package myconfig

// Generated with confluent v0.1.1 (https://pypi.org/project/confluent/).
var TestConfig = struct {
    myBoolean           bool
    myInteger           int
    myFloat             float64
    myCombinedFloat     float64
    myDouble            float64
    myRegex             string // Just another RegEx.
    mySubstitutedString string
    myCombinedString    string
    myIncludedString    string
}{
    myBoolean:           true,
    myInteger:           142,
    myFloat:             322.0,
    myCombinedFloat:     45724.0,
    myDouble:            233.9,
    myRegex:             "Test Reg(E|e)x",
    mySubstitutedString: "Sometimes I just want to scream Hello Mars!",
    myCombinedString:    "I am telling you that this string got included from test-include.yaml.",
    myIncludedString:    "this string got included from test-include.yaml",
}
