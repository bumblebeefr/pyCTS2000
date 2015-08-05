LF = "\x0A"
CR = "\x0D"
FF = "\x0C"
ESC = "\x1B"
CAN = "\x18"
SP = "\x20"
GS = "\x1D"
BS = '\x1E'
NULL = chr(0)


class CHARTABLE():
    PC437 = 0
    KATAKANA = 1
    PC850 = 2
    PC860 = 3
    PC863 = 4
    PC865 = 5
    PC852 = 6
    PC866 = 7
    PC857 = 8
    WPC1252 = 9
    PC858 = 19
    THAI_CODE_18 = 26
    PC864 = 40
    USER = 255


ENCODINGS = {
    CHARTABLE.PC437: "cp437",
    CHARTABLE.PC850: "cp850",
    CHARTABLE.PC860: "cp860",
    CHARTABLE.PC863: "cp863",
    CHARTABLE.PC865: "cp865",
    CHARTABLE.PC852: "cp852",
    CHARTABLE.PC866: "cp866",
    CHARTABLE.PC857: "cp857",
    CHARTABLE.PC858: "cp858",
    CHARTABLE.PC864: "cp864",
}


class FONT():
    A_12x24 = 0
    B_9x24 = 1
    C_8x16 = 2


class CHARSET():
    USA = 0
    FRANCE = 1
    GERMANY = 2
    UK = 3
    DENMARK_I = 4
    SWEDEN = 5
    ITALY = 6
    SPAIN_I = 7
    JAPAN = 8
    NARWAY = 9
    DENMARK_II = 10
    SPAIN_II = 11
    LATIN_AMERICA = 12
    KOREA = 13
    CROATIA = 14
    CHINA = 15
