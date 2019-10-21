"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import RenderFunctions


#
# Enum of target render precisions
#
class RenderPrecision:

    # 16-bit floating point
    FP16 = 1

    # 8-bit uint
    U8 = 2

    # Both FP16 and U8
    Both = 3


#
# An individual renderable type
#
class RenderTypeItem:

    def __init__(self, inType, inPrecision, inFunc, inAlpha, inFilename, inDisplayName):
        self.mType = inType
        self.mPrecision = inPrecision
        self.mFunc = inFunc
        self.mAlpha = inAlpha
        self.mFilename = inFilename
        self.mDisplayName = inDisplayName

    def dbg(self):
        print '%s, %i, %s, %s' % (self.mType, self.mPrecision, self.mAlpha, self.mDisplayName)

    def getType(self):
        return self.mType

    def getPrecision(self):
        return self.mPrecision

    def call(self, inNode, inContext, outPixel):
        if self.mFunc is not None:
            self.mFunc(inNode, outPixel, inContext)

    def isAlpha(self):
        return self.mAlpha is not False

    def isRGB(self):
        return self.mAlpha is not True

    def isPrecision(self, inPrecision):
        return (self.mPrecision & inPrecision) != 0

    def isLDR(self):
        return self.isPrecision(RenderPrecision.U8)

    def isHDR(self):
        return self.isPrecision(RenderPrecision.FP16)

    def getFilename(self):
        return self.mFilename

    def getDisplayName(self):
        return self.mDisplayName


class RenderType:
    NoRender = 0
    PivotPosition = 2
    OriginPosition = 3
    OriginExtents = 4
    XVector = 5
    YVector = 6
    ZVector = 7
    ParentIndexInt = 8
    NumStepsToRoot = 9
    RandomValueHDR = 10
    BoundingBoxDiameter = 11
    # SelectionOrder = 12 # JB: Not sure how easily this can be supported, do people use it?
    HierarchyPositionHDR = 13
    XWidth = 14
    YDepth = 15
    ZHeight = 17
    ParentIndexFloat = 18
    HierarchyPositionLDR = 19
    RandomValueLDR = 20
    XExtent = 21
    YExtent = 22
    ZExtent = 23

    Items = [
        RenderTypeItem(NoRender,				RenderPrecision.Both,	None,										None,	'', 								'Nothing'),
        RenderTypeItem(PivotPosition,			RenderPrecision.FP16,	RenderFunctions.pivotPosition,				False,	'PivotPos',							'Pivot Position'),
        RenderTypeItem(OriginPosition,			RenderPrecision.FP16,	RenderFunctions.originPosition,				False,	'OriginPos',						'Origin Position'),
        RenderTypeItem(OriginExtents,			RenderPrecision.FP16,	RenderFunctions.extents,					False,	'OriginExt',						'Origin Extents'),
        RenderTypeItem(XVector,					RenderPrecision.U8,		RenderFunctions.xvector,					False,	'XVector',							'X Vector'),
        RenderTypeItem(YVector,					RenderPrecision.U8,		RenderFunctions.yvector,					False,	'YVector',							'Y Vector'),
        RenderTypeItem(ZVector,					RenderPrecision.U8,		RenderFunctions.zvector,					False,	'ZVector',							'Z Vector'),
        RenderTypeItem(ParentIndexInt,			RenderPrecision.FP16,	RenderFunctions.parentIndexInt,				True,	'ParentIndexInt',					'Parent Index (Int as Float)'),
        RenderTypeItem(NumStepsToRoot,			RenderPrecision.FP16,	RenderFunctions.stepsToRoot,				True,	'StepsToRoot',						'Number of Steps From Root'),
        RenderTypeItem(RandomValueHDR,			RenderPrecision.FP16,	RenderFunctions.random01,					True,	'Random0-1',						'Random 0-1 Value Per Element'),
        RenderTypeItem(BoundingBoxDiameter,		RenderPrecision.FP16,	RenderFunctions.boundingBoxDiameter,		True,	'BoundDiameter',					'Bounding Box Diameter'),
        # RenderTypeItem(SelectionOrder,			RenderPrecision.FP16,	None,										True,	'SelectionOrder_IntAsFloat',		'Selection Order (Int as Float)'),
        RenderTypeItem(HierarchyPositionHDR,	RenderPrecision.FP16,	RenderFunctions.normalizedStepsToRoot,		True,	'NormalizedHierPos',				'Normalized 0-1 Hierarchy Position'),
        RenderTypeItem(XWidth,					RenderPrecision.FP16,	RenderFunctions.maxBoundingBoxDistanceX,	True,	'ObjectXWidth',						'Object X Width'),
        RenderTypeItem(YDepth,					RenderPrecision.FP16,	RenderFunctions.maxBoundingBoxDistanceY,	True,	'ObjectYDepth',						'Object Y Depth'),
        RenderTypeItem(ZHeight,					RenderPrecision.FP16,	RenderFunctions.maxBoundingBoxDistanceZ,	True,	'ObjectZHeight',					'Object Z Height'),
        RenderTypeItem(ParentIndexFloat,		RenderPrecision.FP16,	RenderFunctions.parentIndexFloat,			True,	'ParentIndexFloat',					'Parent Index (Float: Max 2048)'),
        RenderTypeItem(HierarchyPositionLDR,	RenderPrecision.U8,		RenderFunctions.normalizedStepsToRoot,		True,	'NormalizedHierPos',				'Normalized 0-1 Hierarchy Position'),
        RenderTypeItem(RandomValueLDR,			RenderPrecision.U8,		RenderFunctions.random01,					True,	'Random0-1',						'Random 0-1 Value Per Element'),
        RenderTypeItem(XExtent,					RenderPrecision.U8,		RenderFunctions.maxBoundingBoxDistanceXLDR,	True,	'XExtentDividedby2048reaches2048',	'X Extent (0-2048)'),
        RenderTypeItem(YExtent,					RenderPrecision.U8,		RenderFunctions.maxBoundingBoxDistanceYLDR,	True,	'YExtentDividedby2048reaches2048',	'Y Extent (0-2048)'),
        RenderTypeItem(ZExtent,					RenderPrecision.U8,		RenderFunctions.maxBoundingBoxDistanceZLDR,	True,	'ZExtentDividedby2048reaches2048',	'Z Extent (0-2048)')
    ]

    @staticmethod
    def fromType(inType):
        filtered = [item for item in RenderType.Items if item.getType() == inType]
        return filtered[0] if len(filtered) > 0 else NoRender

    @staticmethod
    def getAlphas(inPrecision):
        return [item for item in RenderType.Items if item.isPrecision(inPrecision) and item.isAlpha()]

    @staticmethod
    def getRGBs():
        return [item for item in RenderType.Items if item.isRGB()]
