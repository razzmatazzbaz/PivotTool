"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import io
import math
import struct

import Half


#
# Direct Draw Surface Flags
#
class DDSD():
    Caps = 0x1
    Height = 0x2
    Width = 0x4
    Pitch = 0x8
    PixelFormat = 0x1000
    MipMapCount = 0x20000
    LinearSize = 0x80000
    Depth = 0x800000


#
# Direct Draw Pixel Format Flags
#
class DDPF():
    AlphaPixels = 0x1
    Alpha = 0x2
    FourCC = 0x4
    RGB = 0x40
    YUV = 0x200
    Luminance = 0x20000


#
# Data types available for conversion
#
class DataFormat():
    Unknown = 0
    UInt8 = 1
    SInt8 = 2
    UInt8_UNorm = 3
    SInt16 = 4
    UInt16 = 5
    UInt16_UNorm = 6
    SInt32 = 7
    UInt32 = 8
    UInt32_UNorm = 9
    Float32 = 10
    Float16 = 11


#
# DXGI Format Enum
#
class DXGIFormat():
    Unknown = 0
    R32G32B32A32_Typeless = 1
    R32G32B32A32_Float = 2
    R32G32B32A32_UInt = 3
    R32G32B32A32_SInt = 4
    R32G32B32_Typeless = 5
    R32G32B32_Float = 6
    R32G32B32_UInt = 7
    R32G32B32_SInt = 8
    R16G16B16A16_Typeless = 9
    R16G16B16A16_Float = 10
    R16G16B16A16_UNorm = 11
    R16G16B16A16_UInt = 12
    R16G16B16A16_SNorm = 13
    R16G16B16A16_SInt = 14
    R32G32_Typeless = 15
    R32G32_Float = 16
    R32G32_UInt = 17
    R32G32_SInt = 18
    R32G8X24_Typeless = 19
    D32_Float_S8X24_UInt = 20
    R32_Float_X8X24_Typeless = 21
    X32_Typeless_G8X24_UInt = 22
    R10G10B10A2_Typeless = 23
    R10G10B10A2_UNorm = 24
    R10G10B10A2_UInt = 25
    R11G11B10_Float = 26
    R8G8B8A8_Typeless = 27
    R8G8B8A8_UNorm = 28
    R8G8B8A8_UNorm_sRGB = 29
    R8G8B8A8_UInt = 30
    R8G8B8A8_SNorm = 31
    R8G8B8A8_SInt = 32
    R16G16_Typeless = 33
    R16G16_Float = 34
    R16G16_UNorm = 35
    R16G16_UInt = 36
    R16G16_SNorm = 37
    R16G16_SInt = 38
    R32_Typeless = 39
    D32_Float = 40
    R32_Float = 41
    R32_UInt = 42
    R32_SInt = 43
    R24G8_Typeless = 44
    D24_UNorm_S8_UInt = 45
    R24_UNorm_X8_Typeless = 46
    X24_Typeless_G8_UInt = 47
    R8G8_Typeless = 48
    R8G8_UNorm = 49
    R8G8_UInt = 50
    R8G8_SNorm = 51
    R8G8_SInt = 52
    R16_Typeless = 53
    R16_Float = 54
    D16_UNorm = 55
    R16_UNorm = 56
    R16_UInt = 57
    R16_SNorm = 58
    R16_SInt = 59
    R8_Typeless = 60
    R8_UNorm = 61
    R8_UInt = 62
    R8_SNorm = 63
    R8_SInt = 64
    A8_UNorm = 65
    R1_UNorm = 66
    R9G9B9E5_SharedExp = 67
    R8G8_B8G8_UNorm = 68
    G8R8_G8B8_UNorm = 69
    BC1_Typeless = 70
    BC1_UNorm = 71
    BC1_UNorm_sRGB = 72
    BC2_Typeless = 73
    BC2_UNorm = 74
    BC2_UNorm_sRGB = 75
    BC3_Typeless = 76
    BC3_UNorm = 77
    BC3_UNorm_sRGB = 78
    BC4_Typeless = 79
    BC4_UNorm = 80
    BC4_SNorm = 81
    BC5_Typeless = 82
    BC5_UNorm = 83
    BC5_SNorm = 84
    B5G6R5_UNorm = 85
    B5G5R5A1_UNorm = 86
    B8G8R8A8_UNorm = 87
    B8G8R8X8_UNorm = 88
    R10G10B10_XR_Bias_A2_UNorm = 89
    B8G8R8A8_Typeless = 90
    B8G8R8A8_UNorm_sRGB = 91
    B8G8R8X8_Typeless = 92
    B8G8R8X8_UNorm_sRGB = 93
    BC6H_Typeless = 94
    BC6H_UF16 = 95
    BC6H_SF16 = 96
    BC7_Typeless = 97
    BC7_UNorm = 98
    BC7_UNorm_sRGB = 99
    AYUV = 100
    Y410 = 101
    Y416 = 102
    NV12 = 103
    P010 = 104
    P016 = 105
    YUV420_Opaque = 106
    YUY2 = 107
    Y210 = 108
    Y216 = 109
    NV11 = 110
    AI44 = 111
    IA44 = 112
    P8 = 113
    A8P8 = 114
    B4G4R4A4_UNorm = 115
    P208 = 116
    V208 = 117
    V408 = 118

    # Number of bytes per pixel (for pitch)
    BytesPP = [
        0,
        16, 16, 16, 16,  # RGBA32
        12, 12, 12, 12,  # RGB32
        8, 8, 8, 8, 8, 8,  # RGBA16
        8, 8, 8, 8,  # RG32
        8, 8, 8, 8,  # R32G8X24 -> X32_G8X24
        4, 4, 4, 4,  # RGBA10 -> RG11B10
        4, 4, 4, 4, 4, 4,  # RGBA8
        4, 4, 4, 4, 4, 4,  # RG16
        4, 4, 4, 4, 4, 4, 4, 4, 4,  # R32 -> X24G8
        2, 2, 2, 2, 2,  # RG8
        2, 2, 2, 2, 2, 2, 2,  # R16
        1, 1, 1, 1, 1, 1,  # R8
        0,  # R1?
        0,  # SharedExp
        0, 0,  # R8G8, B8G8
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # BCn
        2, 2,  # B5G6R5, BGR5A1
        4, 4, 4, 4, 4, 4, 4,  # BGRA8
        0, 0, 0, 0, 0, 0,  # BCn
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # YUV
        0, 0, 0, 0, 0, 0, 0, 0, 0,  # YUV
    ]

    # Intended format type (for automatic conversion of data)
    ConvertDataFormat = [
        DataFormat.Unknown, DataFormat.Unknown, DataFormat.Float32, DataFormat.UInt32, DataFormat.SInt32, DataFormat.Unknown, DataFormat.Float32, DataFormat.UInt32, DataFormat.SInt32, DataFormat.Unknown,
        DataFormat.Float16, DataFormat.UInt16_UNorm, DataFormat.UInt16, DataFormat.Unknown, DataFormat.SInt16, DataFormat.Unknown, DataFormat.Float32, DataFormat.UInt32, DataFormat.SInt32, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown,
        DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.UInt8_UNorm, DataFormat.UInt8_UNorm, DataFormat.UInt8, DataFormat.Unknown, DataFormat.SInt8, DataFormat.Unknown, DataFormat.Float16, DataFormat.UInt16_UNorm, DataFormat.UInt16,
        DataFormat.Unknown, DataFormat.SInt16, DataFormat.Unknown, DataFormat.Float32, DataFormat.Float32, DataFormat.UInt32, DataFormat.SInt32, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.UInt8_UNorm, DataFormat.UInt8,
        DataFormat.Unknown, DataFormat.SInt8, DataFormat.Unknown, DataFormat.Float16, DataFormat.UInt16_UNorm, DataFormat.UInt16_UNorm, DataFormat.UInt16, DataFormat.Unknown, DataFormat.SInt16, DataFormat.Unknown, DataFormat.UInt8_UNorm, DataFormat.UInt8, DataFormat.Unknown, DataFormat.SInt8,
        DataFormat.UInt8_UNorm, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown,
        DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.UInt8_UNorm, DataFormat.UInt8_UNorm, DataFormat.Unknown, DataFormat.Unknown, DataFormat.UInt8_UNorm,
        DataFormat.Unknown, DataFormat.UInt8_UNorm, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown,
        DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.UInt8, DataFormat.UInt8, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown, DataFormat.Unknown,
    ]

    # Get format size
    @staticmethod
    def GetBytesPerPixel(inFormat):
        return DXGIFormat.BytesPP[inFormat]

    # Get target format type
    @staticmethod
    def GetDataFormat(inFormat):
        return DXGIFormat.ConvertDataFormat[inFormat]


#
# DX10 Resource Dimension
#
class ResourceDimension():
    Unknown = 0
    Buffer = 1
    Texture1D = 2
    Texture2D = 3
    Texture3D = 4


#
# DXT10 DDS Header Structure
#
class DDS_HEADER_DXT10():
    def __init__(self):
        self.mStruct = struct.Struct('IIIII')

        self.mDXGIFormat = DXGIFormat.Unknown
        self.mResourceDimension = ResourceDimension.Unknown
        self.mMiscFlag = 0
        self.mArraySize = 1
        self.mMiscFlags2 = 0

    # Serialize to bytearray
    def Serialize(self):
        return self.mStruct.pack(self.mDXGIFormat, self.mResourceDimension, self.mMiscFlag, self.mArraySize, self.mMiscFlags2)


#
# DDS Pixel Format Structure
#
class DDS_PIXELFORMAT():
    def __init__(self):
        self.mStruct = struct.Struct('IIIIIIII')
        self.mSize = self.mStruct.size
        self.mFlags = 0
        self.mFourCC = 0
        self.mRGBBitCount = 0
        self.mRBitMask = 0
        self.mGBitMask = 0
        self.mBBitMask = 0
        self.mABitMask = 0

    # Serialize to bytearray
    def Serialize(self):
        return self.mStruct.pack(self.mSize, self.mFlags, self.mFourCC, self.mRGBBitCount, self.mRBitMask, self.mGBitMask, self.mBBitMask, self.mABitMask)


#
# DDS Header Structure
#
class DDS_HEADER():
    def __init__(self):
        self.mPixelFormat = DDS_PIXELFORMAT()
        self.mStruct = struct.Struct('IIIIIIIIIIIIIIIIII{}sIIIII'.format(self.mPixelFormat.mStruct.size))

        self.mSize = self.mStruct.size
        self.mFlags = 0
        self.mHeight = 0
        self.mWidth = 0
        self.mPitchOrLinearSize = 0
        self.mDepth = 0
        self.mMipMapCount = 0
        self.mReserved1_0 = 0
        self.mReserved1_1 = 0
        self.mReserved1_2 = 0
        self.mReserved1_3 = 0
        self.mReserved1_4 = 0
        self.mReserved1_5 = 0
        self.mReserved1_6 = 0
        self.mReserved1_7 = 0
        self.mReserved1_8 = 0
        self.mReserved1_9 = 0
        self.mReserved1_10 = 0
        self.mCaps = 0
        self.mCaps2 = 0
        self.mCaps3 = 0
        self.mCaps4 = 0
        self.mReserved2 = 0

    # Serialize to bytearray
    def Serialize(self):
        return self.mStruct.pack(
            self.mSize, self.mFlags, self.mHeight, self.mWidth, self.mPitchOrLinearSize, self.mDepth, self.mMipMapCount,
            self.mReserved1_0, self.mReserved1_1, self.mReserved1_2, self.mReserved1_3, self.mReserved1_4, self.mReserved1_5, self.mReserved1_6, self.mReserved1_7, self.mReserved1_8, self.mReserved1_9, self.mReserved1_10,
            self.mPixelFormat.Serialize(),
            self.mCaps, self.mCaps2, self.mCaps3, self.mCaps4, self.mReserved2
        )


# Wrapper structure for serializing an entire DDS file header
class DDSFile():
    def __init__(self):
        self.mHeader = DDS_HEADER()
        self.mHeaderDX10 = DDS_HEADER_DXT10()
        self.mStructBase = struct.Struct('I{}s'.format(self.mHeader.mStruct.size))
        self.mStructDX10 = struct.Struct('I{}s{}s'.format(self.mHeader.mStruct.size, self.mHeaderDX10.mStruct.size))

    # Serialize to bytearray
    def Serialize(self):
        if self.mHeader.mPixelFormat.mFourCC == 0x30315844:
            return self.mStructDX10.pack(0x20534444, self.mHeader.Serialize(), self.mHeaderDX10.Serialize())
        else:
            return self.mStructBase.pack(0x20534444, self.mHeader.Serialize())


# Handy data format converter, so people don't have to worry about manipulating data into the right space for saving
class SequenceConverter:

    @staticmethod
    def Clamp(inV, inMin, inMax):
        if inV < inMin:
            return inMin
        if inV > inMax:
            return inMax
        return inV

    @staticmethod
    def I32ToI8_UNorm(inSource):
        converted = [SequenceConverter.Clamp(c, 0, 255) for c in inSource]
        return struct.pack('{}B'.format(len(inSource)), *converted)

    @staticmethod
    def F32ToI8_UNorm(inSource):
        converted = [SequenceConverter.Clamp(math.floor(c * 255), 0, 255) for c in inSource]
        return struct.pack('{}B'.format(len(converted)), *converted)

    @staticmethod
    def F32ToF32_Float(inSource):
        return struct.pack('{}f'.format(len(inSource)), *inSource)

    @staticmethod
    def F32ToF16_Float(inSource):
        converted = [Half.GetHalf(c) for c in inSource]
        return struct.pack('{}H'.format(len(converted)), *converted)

    @staticmethod
    def GetConverters():
        # Automatic conversion types resolved to functions
        return {
            DataFormat.Float32: {
                DataFormat.UInt8_UNorm: SequenceConverter.F32ToI8_UNorm,
                DataFormat.Float32: SequenceConverter.F32ToF32_Float,
                DataFormat.Float16: SequenceConverter.F32ToF16_Float
            },
            DataFormat.SInt32: {
                DataFormat.UInt8_UNorm: SequenceConverter.I32ToI8_UNorm,
                DataFormat.UInt8: SequenceConverter.I32ToI8_UNorm  # JB: I don't think there is any specific normalization required for this??
            },
            DataFormat.UInt8_UNorm: {
                DataFormat.UInt8_UNorm: SequenceConverter.I32ToI8_UNorm,
                DataFormat.UInt8: SequenceConverter.I32ToI8_UNorm  # JB: I don't think there is any specific normalization required for this??
            }
        }

    @staticmethod
    def GetBytes(inSource, inSourceFormat, inTargetFormat):
        converters = SequenceConverter.GetConverters()
        if inSourceFormat not in converters:
            raise Exception("Can't find format '%s' in Converters" % inSourceFormat)
        source = converters[inSourceFormat]
        if inTargetFormat not in source:
            raise Exception("Can't find format '%s' in target converter" % inTargetFormat)

        return source[inTargetFormat](inSource)


#
# Write a 2D texture to disk
#
def WriteTexture2D(inPath, inWidth, inHeight, inFormat, inMipCount, inData, inSourceFormat):
    dds = DDSFile()

    dds.mHeader = DDS_HEADER()
    dds.mHeader.mFlags = DDSD.Caps | DDSD.Height | DDSD.Width | DDSD.PixelFormat
    dds.mHeader.mHeight = inHeight
    dds.mHeader.mWidth = inWidth
    dds.mHeader.mPitchOrLinearSize = inWidth * DXGIFormat.GetBytesPerPixel(inFormat)  # NOTE: This won't work with compressed formats!
    dds.mHeader.mDepth = 1
    dds.mHeader.mMipMapCount = inMipCount
    dds.mHeader.Caps = 0x1000  # DDSCAPS_TEXTURE

    # JB: Epic doesn't support modern DDS files, resort to legacy :/
    # dds.mHeader.mPixelFormat.mFlags = DDPF.FourCC
    # dds.mHeader.mPixelFormat.mFourCC = 0x30315844 # DX10

    if inFormat == DXGIFormat.R16G16B16A16_Float:
        dds.mHeader.mPixelFormat.mFlags = DDPF.FourCC
        dds.mHeader.mPixelFormat.mFourCC = 0x71
    elif inFormat == DXGIFormat.B8G8R8A8_UNorm:
        dds.mHeader.mPixelFormat.mFlags = DDPF.RGB | DDPF.Alpha
        dds.mHeader.mPixelFormat.mFourCC = 0
        dds.mHeader.mPixelFormat.mRGBBitCount = 32
        dds.mHeader.mPixelFormat.mRBitMask = 0x00ff0000
        dds.mHeader.mPixelFormat.mGBitMask = 0x0000ff00
        dds.mHeader.mPixelFormat.mBBitMask = 0x000000ff
        dds.mHeader.mPixelFormat.mABitMask = 0xff000000
    else:
        raise Exception("Can't save to legacy format: %s" % inFormat)
    dds.mHeaderDX10.mDXGIFormat = inFormat
    dds.mHeaderDX10.mResourceDimension = ResourceDimension.Texture2D

    with open(inPath, 'w+b') as fp:
        fp.write(dds.Serialize())
        fp.write(SequenceConverter.GetBytes(inData, inSourceFormat, DXGIFormat.GetDataFormat(inFormat)))
