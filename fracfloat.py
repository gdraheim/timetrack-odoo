#! /usr/bin/python3
"""
implements frac formatting
"""

from typing import Any, cast, Union
import string
import re
import logging

logg = logging.getLogger("fracfloat")

norm_frac_1_4 = 0x00BC
norm_frac_1_2 = 0x00BD
norm_frac_3_4 = 0x00BE
norm_frac_1_7 = 0x2150
norm_frac_1_9 = 0x2151
norm_frac_1_10 = 0x2152
norm_frac_1_3 = 0x2153
norm_frac_2_3 = 0x2154
norm_frac_1_5 = 0x2155
norm_frac_2_5 = 0x2156
norm_frac_3_5 = 0x2157
norm_frac_4_5 = 0x2158
norm_frac_1_6 = 0x2159
norm_frac_5_6 = 0x215A
norm_frac_1_8 = 0x215B
norm_frac_3_8 = 0x215C
norm_frac_5_8 = 0x215D
norm_frac_7_8 = 0x215E
norm_frac_1_x = 0x215F
norm_frac_0_3 = 0x2189

currency_dollar = 0x024
currency_pound = 0x0A3
currency_symbol = 0x0A4  # in iso-8859-1 it shows the euro sign
currency_yen = 0x0A5
currency_euro = 0x20AC
currency_default = currency_euro

class Frac4:
    def __init__(self, value: float) -> None:
        self.value = value
        self.hours = "h"
    # @override
    def __format__(self, fmt: str) -> str:
        value = self.value
        if fmt.endswith("H"):
            base = int(value)
            frac = value - base
            f60 = frac * 60 + 0.8  # (100 / 60.) / 2 = 0.833
            if f60 >= 60:
                f60 = 0
                base += 1
            num = "{:" + fmt[:-1] + "d}"
            res = num.format(base)
            return res + ":{:02d}".format(int(f60))
        if fmt.endswith("h"):
            base = int(value)
            frac = value - base
            if frac < 0.124:
                ch = self.hours if base else "0"
            elif frac < 0.374:
                ch = chr(norm_frac_1_4)
            elif frac < 0.624:
                ch = chr(norm_frac_1_2)
            elif frac < 0.874:
                ch = chr(norm_frac_3_4)
            else:
                base += 1
                ch = self.hours if base else "0"
            num = "{:" + fmt[:-1] + "d}"
            res = num.format(base)
            if not base:
                r = res.rindex("0")
                res = res[:r] + ch + res[r + 1:] + self.hours
            else:
                res += ch
            return res
        if fmt.endswith("q"):
            base = int(value)
            frac = value - base
            if frac < 0.124:
                ch = "." if base else "0"
            elif frac < 0.374:
                ch = chr(norm_frac_1_4)
            elif frac < 0.624:
                ch = chr(norm_frac_1_2)
            elif frac < 0.874:
                ch = chr(norm_frac_3_4)
            else:
                base += 1
                ch = "." if base else "0"
            num = "{:" + fmt[:-1] + "d}"
            res = num.format(base)
            if not base:
                r = res.rindex("0")
                res = res[:r] + ch + res[r + 1:]
            else:
                res += ch
            return res
        if fmt.endswith("M"):
            val = value / (1024 * 1024)
            base = int(val)
            frac = val - base
            if frac < 0.124:
                ch = "." if base else "0"
            elif frac < 0.374:
                ch = chr(norm_frac_1_4)
            elif frac < 0.624:
                ch = chr(norm_frac_1_2)
            elif frac < 0.874:
                ch = chr(norm_frac_3_4)
            else:
                base += 1
                ch = "." if base else "0"
            num = "{:" + fmt[:-1] + "d}"
            res = num.format(base)
            if not base:
                r = res.rindex("0")
                res = res[:r] + ch + res[r + 1:]
            else:
                res += ch
            return res + "M"
        if fmt.endswith("Q"):
            base = int(value)
            frac = value - base
            if frac < 0.009:
                ch = "." if base else "0"
            elif frac < 0.299:
                ch = chr(norm_frac_1_5)
            elif frac < 0.499:
                ch = chr(norm_frac_2_5)
            elif frac < 0.699:
                ch = chr(norm_frac_3_5)
            elif frac < 0.899:
                ch = chr(norm_frac_4_5)
            else:
                base += 1
                ch = "." if base else "0"
            num = "{:" + fmt[:-1] + "d}"
            res = num.format(base)
            if not base:
                r = res.rindex("0")
                res = res[:r] + ch + res[r + 1:]
            else:
                res += ch
            return res
        if fmt.endswith("R"):
            base = int(value)
            frac = value - base
            if frac < 0.082:
                ch = "." if base else "0"
            elif frac < 0.249:
                ch = chr(norm_frac_1_6)
            elif frac < 0.415:
                ch = chr(norm_frac_1_3)
            elif frac < 0.582:
                ch = chr(norm_frac_1_2)
            elif frac < 0.749:
                ch = chr(norm_frac_2_3)
            elif frac < 0.915:
                ch = chr(norm_frac_5_6)
            else:
                base += 1
                ch = "." if base else "0"
            num = "{:" + fmt[:-1] + "d}"
            res = num.format(base)
            if not base:
                r = res.rindex("0")
                res = res[:r] + ch + res[r + 1:]
            else:
                res += ch
            return res
        if fmt.endswith("$"):
            x, symbol = 1, chr(currency_default)
            if fmt.endswith("US$"):
                x, symbol = 3, chr(currency_dollar)
            if fmt.endswith("EU$") or fmt.endswith("EC$"):
                x, symbol = 3, chr(currency_euro)
            if fmt.endswith("JP$") or fmt.endswith("CN$"):
                x, symbol = 3, chr(currency_yen)
            if fmt.endswith("BP$") or fmt.endswith("PD$"):
                x, symbol = 3, chr(currency_pound)
            base = int(value)
            frac = value - base
            num1 = "01234567899"[int(frac * 10)]
            num2 = "01234567899"[int(frac * 100) % 10]
            num = "{:" + fmt[:-x] + "n}"
            res = num.format(base)
            return res + "." + num1 + num2 + symbol
        num = "{:" + fmt + "}"
        return num.format(value)

float_with_frac = "[+-]?(\\d+([.]\\d*)?|\\d*[.%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c])[hM$%c%c%c]?$" % (  # ...
    norm_frac_1_4, norm_frac_1_2, norm_frac_3_4,  # ...
    norm_frac_1_5, norm_frac_2_5, norm_frac_3_5,  # ...
    norm_frac_4_5, norm_frac_1_8, norm_frac_3_8,  # ...
    norm_frac_5_8, norm_frac_7_8, norm_frac_1_6,  # ...
    norm_frac_5_6, norm_frac_1_3, norm_frac_2_3,  # ...
    currency_euro, currency_yen, currency_pound)  # ...
float_with_hours = "\\d*[:hH]\\d\\d$"

def is_float_with_frac(value: str) -> bool:
    if re.match(float_with_frac, value):
        return True
    if re.match(float_with_hours, value):
        return True
    return False

def fracfloat(value: str) -> float:
    if value and is_float_with_frac(value):
        if len(value) >= 3 and value[-3] in ":hH":
            numms = value[:-3]
            fracs = value[-2:]
            return float(numms) + float(fracs) / 60
        scale = 1
        if value[-1] in "h$":
            value = value[:-1]
        elif value[-1] in (chr(currency_euro), chr(currency_yen), chr(currency_pound)):
            value = value[:-1]
        elif value[-1] in "M":
            value = value[:-1]
            scale = 1024 * 1024
        frac = 0.
        if value:
            ch = ord(value[-1])
            if ch == norm_frac_1_4:
                frac = 0.25
            if ch == norm_frac_1_2:
                frac = 0.50
            if ch == norm_frac_3_4:
                frac = 0.75
            if ch == norm_frac_1_5:
                frac = 0.2
            if ch == norm_frac_2_5:
                frac = 0.4
            if ch == norm_frac_3_5:
                frac = 0.6
            if ch == norm_frac_4_5:
                frac = 0.8
            if ch == norm_frac_1_6:
                frac = 1 / 6.
            if ch == norm_frac_5_6:
                frac = 5 / 6.
            if ch == norm_frac_1_3:
                frac = 1 / 3.
            if ch == norm_frac_2_3:
                frac = 2 / 3.
            if ch == norm_frac_1_8:
                frac = 0.125
            if ch == norm_frac_3_8:
                frac = 0.375
            if ch == norm_frac_5_8:
                frac = 0.625
            if ch == norm_frac_7_8:
                frac = 0.875
            if frac:
                value = value[:-1]
            if not value:
                return frac * scale
            return (float(value) + frac) * scale
    if value and value[-1] in ('$', chr(currency_euro), chr(currency_yen), chr(currency_pound)):
        return float(value[:-1])
    return float(value)

def strHours(val: Union[int, float, str], fmt: str = 'h') -> str:
    return ("{:" + fmt + "}").format(Frac4(float(val)))
