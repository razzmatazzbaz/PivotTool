"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import maya.cmds as cmds


class TreeNode:

    def __init__(self, inNode):

        self.mNode = inNode
        self.mChildren = [ ]

        if inNode is None:
            return
        shapes = cmds.listRelatives(self.mNode, c=True, s=True, f=True)
        if shapes is None:
            self.mShapes = [ ]
        else:
            self.mShapes = shapes

    def discoverNodeChildren(self):

        # TODO:? Allow children to be ignored from hierarchy
        #        I'm not really sure if this is necessary, maybe wait for a request?
        children = cmds.listRelatives(self.mNode, c=True, s=False, f=True)
        shapes = cmds.listRelatives(self.mNode, c=True, s=True, f=True)

        if shapes is not None and children is not None:
            children = [c for c in children if c not in shapes]

        if children is None:
            return

        for child in children:
            node = TreeNode(child)
            node.discoverNodeChildren()
            self.mChildren.append(node)

    # Filter the tree by the given shape type.
    #   Branches without any children that match are culled
    def filterByShape(self, inTypes):

        hasTargetType = False
        newSelf = TreeNode(self.mNode)

        shapes = cmds.listRelatives(self.mNode, shapes=True, f=True)
        shapes = shapes if shapes is not None else []
        for shape in shapes:
            hasTargetType = cmds.nodeType(shape) in inTypes or hasTargetType

        for c in self.mChildren:
            newChild = c.filterByShape(inTypes)

            if newChild is not None:
                hasTargetType = True
                newSelf.mChildren.append(newChild)

        return newSelf if hasTargetType else None

    # Iterate over the tree, calling inFn on each node
    def iterate(self, inFn):
        self._iterate(None, inFn)

    def _iterate(self, inParent, inFn):
        if self.mNode is not None:
            inFn(self, inParent)

        for c in self.mChildren:
            c._iterate(self, inFn)


# Build a hierarchy of TreeNodes from the given node name
def getMeshHierarchy(inNode):

    root = TreeNode(inNode)
    root.discoverNodeChildren()

    return root
