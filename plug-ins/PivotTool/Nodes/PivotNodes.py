"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds


#
# Simple matrix for a custom node
#
class PivotTransformMatrix(OpenMayaMPx.MPxTransformationMatrix):
    Name = 'PivotTransformMatrix'
    ID = OpenMaya.MTypeId(0xCCB1)

    def __init__(self):
        OpenMayaMPx.MPxTransformationMatrix.__init__(self)

    @staticmethod
    def Creator():
        return PivotTransformMatrix()


#
# Base of the various node types
#
class PivotNodeBase(OpenMayaMPx.MPxTransform):

    def __init__(self):
        OpenMayaMPx.MPxTransform.__init__(self)

    def compute(self, inPlug, inDataBlock):
        pass


#
# Primary 'input' node
#
class PivotNode(PivotNodeBase):
    Name = 'PivotNode'
    ID = OpenMaya.MTypeId(0xCCA1)

    OutputNodeAttribute = OpenMaya.MObject()
    PreviewNodeAttribute = OpenMaya.MObject()
    NodeDataAttribute = OpenMaya.MObject()

    def __init__(self):
        PivotNodeBase.__init__(self)

    def compute(self, inPlug, inDataBlock):
        pass

    @staticmethod
    def Creator():
        return PivotNode()

    @classmethod
    def Initialize(inClass):

        messageAttribute = OpenMaya.MFnMessageAttribute()
        stringAttribute = OpenMaya.MFnTypedAttribute()

        # Output Node
        inClass.OutputNodeAttribute = messageAttribute.create('outputPivotNode', 'opvn')
        inClass.addAttribute(inClass.OutputNodeAttribute)

        # Preview Node
        inClass.PreviewNodeAttribute = messageAttribute.create('previewPivotNode', 'ppvn')
        inClass.addAttribute(inClass.PreviewNodeAttribute)

        # Node Data
        inClass.NodeDataAttribute = stringAttribute.create('nodeData', 'nd', OpenMaya.MFnData.kString)
        inClass.addAttribute(inClass.NodeDataAttribute)


#
# Intermediate output node (not currently used)
#
class PivotPreviewNode(PivotNodeBase):
    Name = 'PivotPreviewNode'
    ID = OpenMaya.MTypeId(0xCCA2)

    InputNodeAttribute = OpenMaya.MObject()
    OutputNodeAttribute = OpenMaya.MObject()

    def __init__(self):
        PivotNodeBase.__init__(self)

    def compute(self, inPlug, inDataBlock):
        pass

    @staticmethod
    def Creator():
        return PivotPreviewNode()

    @classmethod
    def Initialize(inClass):

        messageAttribute = OpenMaya.MFnMessageAttribute()

        # Input Node
        inClass.InputNodeAttribute = messageAttribute.create('inputPivotNode', 'ipvn')
        inClass.addAttribute(inClass.InputNodeAttribute)

        # Output Node
        inClass.OutputNodeAttribute = messageAttribute.create('outputPivotNode', 'opvn')
        inClass.addAttribute(inClass.OutputNodeAttribute)


#
# Output node containing collapsed data
#
class PivotOutputNode(PivotNodeBase):
    Name = 'PivotOutputNode'
    ID = OpenMaya.MTypeId(0xCCA3)

    InputNodeAttribute = OpenMaya.MObject()
    PreviewNodeAttribute = OpenMaya.MObject()
    OutputMeshAttribute = OpenMaya.MObject()

    def __init__(self):
        PivotNodeBase.__init__(self)

    def compute(self, inPlug, inDataBlock):
        pass

    @staticmethod
    def Creator():
        return PivotOutputNode()

    @classmethod
    def Initialize(inClass):

        messageAttribute = OpenMaya.MFnMessageAttribute()

        # Input Node
        inClass.InputNodeAttribute = messageAttribute.create('inputPivotNode', 'ipvn')
        inClass.addAttribute(inClass.InputNodeAttribute)

        # Preview Node
        inClass.PreviewNodeAttribute = messageAttribute.create('previewPivotNode', 'ppvn')
        inClass.addAttribute(inClass.PreviewNodeAttribute)

        # Output Mesh
        inClass.OutputMeshAttribute = messageAttribute.create('outputMesh', 'popm')
        inClass.addAttribute(inClass.OutputMeshAttribute)
