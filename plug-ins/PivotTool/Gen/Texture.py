"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import os
import tempfile
from RenderType import *
from ..Util import LwDDS


#
# Single texture pixel
#
class Pixel:
    def __init__(self):
        self.mR = 0
        self.mG = 0
        self.mB = 0
        self.mA = 0

    def setRGB(self, inVec):
        self.mR = inVec[0]
        self.mG = inVec[1]
        self.mB = inVec[2]

    def setA(self, inA):
        self.mA = inA

    def getA(self):
        return self.mA

    def getRGB(self):
        return [ self.mR, self.mG, self.mB ]

    def getRGBA(self):
        return [ self.mR, self.mG, self.mB, self.mA ]

    def getBGRA(self):
        return [ self.mB, self.mG, self.mR, self.mA ]


#
# Rendered texture container
#
class Texture:
    def __init__(self, inWidth, inHeight, inRootView, inTextureView):
        self.mWidth = inWidth
        self.mHeight = inHeight
        self.mData = [Pixel() for i in range(0, self.mWidth * self.mHeight)]

        self.mView = inTextureView
        self.mRootView = inRootView

    def getWidth(self):
        return self.mWidth

    def getHeight(self):
        return self.mHeight

    def getRGBSource(self):
        return self.mView.getRGB()

    def getASource(self):
        return self.mView.getA()

    def getData(self):
        return self.mData

    def write(self):
        rgb = RenderType.fromType(self.getRGBSource())
        alpha = RenderType.fromType(self.getASource())

        # Get extractor function
        format = LwDDS.DXGIFormat.B8G8R8A8_UNorm
        func = Pixel.getBGRA
        if rgb.isHDR():
            format = LwDDS.DXGIFormat.R16G16B16A16_Float
            func = Pixel.getRGBA

        # Build a suitable filename
        name = '%s_rgb_%s_a_%s_UV_%s.dds' % (self.mRootView.getRootNode(), rgb.getFilename(), alpha.getFilename(), self.mRootView.getAdvancedView().getUVSetName())
        targetPath = os.path.join(tempfile.gettempdir(), name)
        self.mView.setOutputPath(targetPath)

        # Flatten the pixels into a giant float array
        flat = []
        for px in self.getData():
            flat = flat + func(px)

        # Write the texture
        LwDDS.WriteTexture2D(targetPath, self.mWidth, self.mHeight, format, 1, flat, LwDDS.DataFormat.Float32)
