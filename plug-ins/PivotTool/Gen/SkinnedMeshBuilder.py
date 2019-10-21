"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import maya.cmds as cmds
from RenderType import *
from Texture import Texture
import Skeleton


#
# Container for a single joint in a skinned mesh
#
class SkinnedMeshData:
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
class SkinnedMeshDataBuilder:

    def __init__(self, inNode, inParentIndex, inStartIndex, inParentDepth):
        self.mNode = inNode
        self.mParentIndex = inParentIndex
        self.mIndex = inStartIndex
        self.mDepth = inParentDepth + 1
        self.mMaxDepth = self.mDepth
        self.mData = [ ]

        # Get a compacted skeleton for this skin cluster
        self.mSkinCluster = SkinnedMeshDataBuilder.getSkinCluster(inNode)
        self.mSkeleton = Skeleton.fromSkinCluster(self.mSkinCluster)

        self.mSkeleton.mIndex = self.mIndex
        self.mSkeleton.mParentIndex = inParentIndex
        self.mSkeleton.mDepth = self.mDepth
        self.mSkeletonIndex = self.mIndex

        # Assign influence values and create data objects
        self.mSkeleton.iterate(self._assignSkeletonData)

        self.mIndexCount = self.mSkeletonIndex - self.mIndex

    def getRootIndex(self):
        return self.mIndex

    def getMaxDepth(self):
        return self.mMaxDepth

    def getIndexCount(self):
        return self.mIndexCount

    # Tree iterator to assign indices and metadata to skeletal joints
    def _assignSkeletonData(self, inNode, inParent):

        if inParent is not None:
            inNode.mDepth = inParent.mDepth + 1
            inNode.mParentIndex = inParent.mIndex

        inNode.mIndex = self.mSkeletonIndex
        self.mSkeletonIndex = self.mSkeletonIndex + 1

        self.mData.append(SkinnedMeshData(inNode.mNode, inNode.mParentIndex, inNode.mIndex, inNode.mDepth))
        self.mMaxDepth = max(self.mMaxDepth, inNode.mDepth)

    # Perform UV layout
    def layoutUVs(self, inBuilder, inNode):

        # Don't layout any non-geometry objects
        if inNode.mNode is None or len(inNode.mShapes) == 0:
            return

        # Add a UV set to the mesh, if necessary
        inBuilder.tryMakeUVSet(inNode, inBuilder.mView.getAdvancedView().getUVSetName())

        # Get data objects ordered by influence
        influences = Skeleton.getInfluenceNodes(self.mSkinCluster)
        influences = [[data for data in self.mData if data.mNode == influence][0] for influence in influences]

        uvCount = cmds.polyEvaluate(self.mNode.mNode, uv=True)
        for uv in range(0, uvCount):

            # Get primary influence
            weights = cmds.skinPercent(self.mSkinCluster, '%s.map[%i]' % (self.mNode.mNode, uv), q=True, v=True)
            index = weights.index(max(weights))
            data = influences[index]

            # Get coordinate from index
            ucoord, vcoord = inBuilder.getUVCoordinate(data.getIndex())

            # Move UVs
            cmds.polyEditUV('%s.map[%i]' % (self.mNode.mNode, uv), r=False, u=ucoord, v=vcoord)

    # Render texture data
    def renderTextures(self, inBuilder, inNode):

        for texture in inBuilder.mTextures:
            for source in [texture.getRGBSource(), texture.getASource()]:
                renderType = RenderType.fromType(source)

                for data in self.mData:
                    if data.getIndex() < 0:
                        continue
                    renderType.call(data, inBuilder, texture.getData()[data.getIndex()])

    @staticmethod
    def getSkinCluster(inNode):

        shapes = cmds.listRelatives(inNode.mNode, s=True, typ='mesh')
        hasMeshes = shapes is not None and len(shapes) > 0

        if not hasMeshes:
            return None

        inputs = cmds.listConnections('%s.inMesh' % inNode.mNode, d=False, s=True)
        
        if inputs is None:
            return None
        clusters = [node for node in inputs if cmds.nodeType(node) == 'skinCluster']
        return clusters[0] if len(clusters) > 0 else None
