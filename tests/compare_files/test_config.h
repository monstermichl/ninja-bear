#ifndef TEST_CONFIG_H
#define TEST_CONFIG_H

/* Generated with confluent v0.1.1 (https://pypi.org/project/confluent/). */
const struct {
    unsigned char MyBoolean;
    int MyInteger;
    float MyFloat;
    float MyCombinedFloat;
    double MyDouble;
    char* MySubstitutedString;
    char* MyRegex; /* Just another RegEx. */
} TestConfig = {
    1,
    142,
    322.0f,
    45724.0f,
    233.9,
    "Sometimes I just want to scream Hello World!",
    "Test Reg(E|e)x",
};

#endif /* TEST_CONFIG_H */
