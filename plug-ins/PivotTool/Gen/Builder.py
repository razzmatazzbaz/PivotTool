"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import math
import maya.cmds as cmds

from RenderType import *
from Texture import Texture
from StaticMeshBuilder import StaticMeshDataBuilder
from SkinnedMeshBuilder import SkinnedMeshDataBuilder


# Context for building and rendering pivot information
class Builder:

    def __init__(self, inView):
        self.mView = inView
        self.mTotalIndices = 0
        self.mMaxDepth = 0

    # Prepare the hierarchy by determining pivot indices
    def fillHierarchyInfo(self, inNode, inParent):

        parentIndex = -1
        depth = 0

        parentBuilder = None if inParent is None else inParent.mDataBuilder
        if parentBuilder is not None:
            parentIndex = parentBuilder.getRootIndex()
            depth = parentBuilder.getMaxDepth()

        if SkinnedMeshDataBuilder.getSkinCluster(inNode) is not None:
            inNode.mDataBuilder = SkinnedMeshDataBuilder(inNode, parentIndex, self.mTotalIndices, depth)
        else:
            inNode.mDataBuilder = StaticMeshDataBuilder(inNode, parentIndex, self.mTotalIndices, depth)
        self.mTotalIndices = self.mTotalIndices + inNode.mDataBuilder.getIndexCount()

        if inParent is not None:
            self.mMaxDepth = max(self.mMaxDepth, inNode.mDataBuilder.getMaxDepth())

    # Setup texture destinations for rendering
    def generateTextureInfo(self):

        # Figure out texture size
        self.mTextureWidth, self.mTextureHeight = self.getTextureDimension(self.mTotalIndices)

        # Initialize an array of target textures based upon the chosen settings
        self.mTextures = [Texture(self.mTextureWidth, self.mTextureHeight, self.mView, view) for view in self.mView.getTextureViews()]

    # Layout UVs based upon pivot indices
    def layoutUVs(self, inNode, inParent):

        if inNode.mNode is None or inNode.mDataBuilder is None:
            return

        # Have the databuilder do the layout, since it'll account for different object types
        inNode.mDataBuilder.layoutUVs(self, inNode)

    # Fill textures with required data
    def renderTextures(self, inNode, inParent):

        if inNode.mDataBuilder is None:
            return

        inNode.mDataBuilder.renderTextures(self, inNode)

    # Output textures to disk
    def writeTextures(self):

        for texture in self.mTextures:
            texture.write()

    # Get the required texture width/height to fit inObjectCount
    def getTextureDimension(self, inObjectCount):

        validSizes = [4, 8, 16, 32, 64, 128, 256, 512, 1024]

        width = (math.ceil(math.pow(inObjectCount, 0.5)))
        for size in validSizes:
            if width <= size:
                width = size
                break

        height = math.ceil(inObjectCount / width)
        for size in validSizes:
            if height <= size:
                height = size
                break

        return (width, height)

    # Add a UV set if necesary
    def tryMakeUVSet(self, inNode, inName):

        sets = cmds.polyUVSet(inNode.mNode, q=True, auv=True)

        # We need a source UV set to copy from
        if sets is None:
            raise Exception('%s has no sets' % inNode.mNode)

        if inName not in sets:
            cmds.polyUVSet(inNode.mNode, create=True, uvSet=inName)
        
        cmds.polyCopyUV(inNode.mNode, uvi=sets[0], uvs=inName)

    # Get coordinate from index
    def getUVCoordinate(self, inIndex):

        ucoord = (inIndex % self.mTextureWidth) * (1.0 / self.mTextureWidth) + (0.5 / self.mTextureWidth)
        vcoord = 1.0 - ((inIndex / self.mTextureWidth) * (1.0 / self.mTextureHeight) + (0.5 / self.mTextureHeight))

        return ucoord, vcoord
