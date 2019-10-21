"""
    This module is part of the PivotToolPlugin.

    
"""

import math
import struct


#
# Component based representation of a 32-bit float
#
class FP32():
    def __init__(self):
        self.mMantissa = 0
        self.mExponent = 0
        self.mSign = 0

    def ToSingle(self):
        fp32 = (self.mSign << 31) | (self.mExponent << 23) | self.mMantissa
        return struct.unpack('f', struct.pack('I', fp32))[0]

    # Break a 32-bit float down to its' components
    @staticmethod
    def FromSingle(inSingle):
        fp32 = struct.unpack('I', struct.pack('f', inSingle))[0]

        op = FP32()
        op.mMantissa = (fp32 & 0x007fffff)
        op.mExponent = (fp32 & 0x7f800000) >> 23
        op.mSign = (fp32 >> 31)

        return op


#
# Component based representation of a 16-bit float
#
class FP16():
    def __init__(self):
        self.mMantissa = 0
        self.mExponent = 0
        self.mSign = 0

    # Compile components to an integer representing a 16-bit float
    def ToHalf(self):
        return ((self.mSign << 15) | (self.mExponent << 10) | self.mMantissa)

    def ToSingle(self):
        op = FP32()
        op.mSign = self.mSign

        if self.mExponent == 0:
            if self.mMantissa == 0:
                op.mExponent = 0
                op.mMantissa = 0
            else:
                shift = 10 - int(math.log(self.mMantissa, 2))
                op.mExponent = 127 - (15 - 1) - shift
                op.mMantissa = self.mMantissa << (shift + 23 - 10)
        elif self.mExponent == 31:
            op.mExponent = 142
            op.mMantissa = 8380416
        else:
            op.mExponent = self.mExponent - 15 + 127
            op.mMantissa = self.mMantissa << 13

        return op.ToSingle()

    # Break a 32-bit float down to 16-bit half components
    @staticmethod
    def FromSingle(inSingle):
        fp32 = FP32.FromSingle(inSingle)
        op = FP16()

        op.mSign = fp32.mSign

        if fp32.mExponent <= 112:  # Too small value
            op.mExponent = 0
            op.mMantissa = 0
        elif fp32.mExponent >= 143:  # Too large value
            op.mExponent = 30
            op.mMantissa = 1023
        else:
            op.mExponent = (fp32.mExponent - 127 + 15)
            op.mMantissa = (fp32.mMantissa >> 13)

        return op

    @staticmethod
    def FromHalf(inHalf):
        op = FP16()

        op.mMantissa = inHalf & 0x3ff
        op.mExponent = (inHalf >> 10) & 0x1f
        op.mSign = (inHalf >> 15) & 0x1

        return op


# Get a 16-bit float (as an integer) from a 32-bit float value
def GetHalf(inFloat):
    return FP16.FromSingle(inFloat).ToHalf()


def ToSingle(inHalf):
    return FP16.FromHalf(inHalf).ToSingle()
