"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import maya.cmds as cmds

import Trees


#
# Functionality which builds a tree from a skeleton root and prunes irrelivant nodes
#
class SkeletonBuilder:

    def __init__(self, inClusterNodes):
        self.mNodes = inClusterNodes
        self.mSkeleton = None

    def build(self):
        base = findCommonBase(self.mNodes)

        self.mSkeleton = Trees.getMeshHierarchy(base)
        self._markNode(self.mSkeleton)
        self._removeNodes(self.mSkeleton)

    # Recursively mark nodes with relevance
    def _markNode(self, inNode):
        for child in inNode.mChildren:
            self._markNode(child)

        inNode.mIsRelevant = inNode.mNode in self.mNodes
        inNode.mHasRelevantChildren = len([True for child in inNode.mChildren if child.mIsRelevant or child.mHasRelevantChildren]) > 0

    # Remove nodes which have no relevance leaving a compacted tree of important nodes
    def _removeNodes(self, inNode):

        inNode.mChildren = [child for child in inNode.mChildren if child.mHasRelevantChildren or child.mIsRelevant]

        for child in inNode.mChildren:
            self._removeNodes(child)

        children = [ ]
        for child in inNode.mChildren:
            if child.mIsRelevant:
                children.append(child)
                continue

            children = children + child.mChildren

        inNode.mChildren = children


# Convert a node name reference to a full path (if necessary)
# TODO:? Move this to Util
#        Can do if necessary, but it's not used anywhere else in this application
def getFullPath(inNode):
    nodeName = inNode.split('|')[-1]
    parents = cmds.listRelatives(inNode, allParents=True, fullPath=True)
    if parents is None or len(parents) == 0:
        return '|%s' % nodeName

    allChildren = [cmds.listRelatives(node, children=True, fullPath=True) for node in parents]
    allChildren = [child for sublist in allChildren for child in sublist]
    filtered = [child for child in allChildren if child.split('|')[-1] == nodeName]

    if len(filtered) == 0:
        raise Exception("Filtered child list shouldn't have 0 members??")

    return filtered[0]


# Get influcing nodes from a skin cluster
def getInfluenceNodes(inSkinCluster):
    return [getFullPath(node) for node in cmds.skinCluster(inSkinCluster, q=True, inf=True)]


# Get an array which contains the path to the new from it's root
def getAllParents(inNode):
    parents = cmds.listRelatives(inNode, allParents=True, fullPath=True)
    if parents is None or len(parents) == 0:
        return [ inNode ]
    else:
        return getAllParents(parents[0]) + [ inNode ]


# Find the lowest common ancestor in a given array of nodes
def findCommonBase(inNodes):

    allParents = [getAllParents(node) for node in inNodes]
    if len(allParents) == 0:
        return None

    depth = 0
    while True:
        if len(allParents[0]) <= depth:
            break

        needle = allParents[0][depth]
        if len([True for parents in allParents if needle not in parents or parents.index(needle) != depth]) > 0:
            break

        depth = depth + 1

    if depth == 0:
        return None
    return allParents[0][depth - 1]


# Get a skeleton hierarchy from a skincluster node
def fromSkinCluster(inSkinCluster):
    nodes = getInfluenceNodes(inSkinCluster)

    builder = SkeletonBuilder(nodes)
    builder.build()

    return builder.mSkeleton
