"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import maya.cmds as cmds
from RenderType import *
from Texture import Texture


#
# Container for a single static mesh
#
class StaticMeshData:
    def __init__(self, inNode, inParentIndex, inIndex, inDepth):
        self.mNode = inNode
        self.mParentIndex = inParentIndex
        self.mIndex = inIndex
        self.mDepth = inDepth

    def getParentIndex(self):
        return self.mParentIndex

    def getIndex(self):
        return self.mIndex

    def getDepth(self):
        return self.mDepth

    def getNode(self):
        return self.mNode


#
# Builder for static mesh objects, has a single StaticMeshData
#
class StaticMeshDataBuilder:

    def __init__(self, inNode, inParentIndex, inStartIndex, inParentDepth):
        self.mNode = inNode
        self.mParentIndex = inParentIndex
        self.mIndex = inStartIndex
        self.mDepth = inParentDepth + 1
        self.mData = StaticMeshData(inNode.mNode, self.mParentIndex, self.mIndex, self.mDepth)

    def getRootIndex(self):
        return self.mIndex

    def getMaxDepth(self):
        return self.mDepth

    def getIndexCount(self):
        return 1

    # Perform UV layout
    def layoutUVs(self, inBuilder, inNode):

        # Don't layout any non-geometry objects
        if inNode.mNode is None or len(inNode.mShapes) == 0:
            return

        # Add a UV set to the mesh, if necessary
        inBuilder.tryMakeUVSet(inNode, inBuilder.mView.getAdvancedView().getUVSetName())

        # Get coordinate from index
        ucoord, vcoord = inBuilder.getUVCoordinate(self.mData.getIndex())

        # Move UVs
        uvCount = cmds.polyEvaluate(inNode.mNode, uv=True)
        cmds.polyEditUV('%s.map[0:%i]' % (inNode.mNode, uvCount), r=False, u=ucoord, v=vcoord)

    # Render texture data
    def renderTextures(self, inBuilder, inNode):

        if self.mData.getIndex() < 0:
            return

        for texture in inBuilder.mTextures:
            for source in [texture.getRGBSource(), texture.getASource()]:
                renderType = RenderType.fromType(source)
                renderType.call(self.mData, inBuilder, texture.getData()[self.mData.getIndex()])
