#ifndef TEST_CONFIG_H
#define TEST_CONFIG_H

/* Generated with confluent v0.0.1 (https://pypi.org/project/confluent/). */
const struct {
    unsigned char MyBoolean;
    int MyInteger;
    float MyFloat;
    double MyDouble;
    char* MyRegex; /* Just another RegEx. */
    char* MySubstitutedString;
} TestConfig = {
    1,
    142,
    322.0f,
    233.9,
    "Test Reg(E|e)x",
    "Sometimes I just want to scream Hello World!",
};

#endif /* TEST_CONFIG_H */
