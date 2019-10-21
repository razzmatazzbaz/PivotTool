"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import json
import os
import shutil
import maya.cmds as cmds

from ..Nodes.PivotNodes import PivotNode, PivotPreviewNode, PivotOutputNode
from ..Gen import BuildOutput
from ..Gen.RenderType import *


#
# Enum of possible pivot containers
#
class PivotNodeType:

    # Root pivot node and container of source geometry
    Input = 0

    # Collapsed output geometry
    Output = 1

    # Collapsed geometry with preview material applied (optional)
    Preview = 2

    Count = 3


#
# View which represents an individual output texture
#
class OutputTextureView:

    def __init__(self, inParentModel, inData):
        self.mParentModel = inParentModel
        self.mData = inData

        if self.mData is None:
            self.mData = { 'RGB': 0, 'A': 0, 'OutputPath': None }

    # Get RGB output type
    def getRGB(self):
        return self.mData['RGB']

    # Get Alpha output type
    def getA(self):
        return self.mData['A']

    # Get the path that this view was most recently written to
    def getOutputPath(self):
        return self.mData['OutputPath']

    # Gets a display string for this view
    def getDisplayName(self):
        rgbType = RenderType.fromType(self.getRGB())
        aType = RenderType.fromType(self.getA())

        return '[%s, %s]' % (rgbType.getDisplayName(), aType.getDisplayName())

    # Set RGB output type
    def setRGB(self, inRGB):
        prevRGB = self.mData['RGB']
        self.mData['RGB'] = inRGB

        prevType = RenderType.fromType(prevRGB)
        newType = RenderType.fromType(inRGB)

        if prevType.mPrecision != newType.mPrecision and newType.mPrecision != RenderPrecision.Both:
            self.mData['A'] = RenderType.NoRender

        self.mParentModel.onChanged()

    # Set Alpha output type
    def setA(self, inA):
        self.mData['A'] = inA
        self.mParentModel.onChanged()

    # Set the path to this view on disk
    def setOutputPath(self, inPath):
        self.mData['OutputPath'] = inPath
        self.mParentModel.onChanged()

    # Remove this view from its parent container
    def removeSelf(self):
        self.mParentModel.removeTextureOutput(self)


#
# View which represents a set of extra options on a pivot object
#
class AdvancedOptionsView:

    def __init__(self, inParentModel, inData):

        self.mParentModel = inParentModel
        self.mData = inData

        if self.mData is None:
            self.mData = {
                'UVSetName': 'Pivot',
                'ExportPath': None
            }

    # Get the name of the UV set for pivot data
    def getUVSetName(self):
        return self.mData['UVSetName']

    # Get the default export path (default None)
    def getExportPath(self):
        return self.mData['ExportPath']

    # Set the name of the UV set for pivot data
    def setUVSetName(self, inName):

        if inName is None or len(inName.strip()) == 0:
            return
        self.mData['UVSetName'] = inName.strip()

        self.mParentModel.onChanged()

    # Set the default export path (Usually done when 'Export As' is used)
    def setExportPath(self, inPath):
        self.mData['ExportPath'] = inPath
        self.mParentModel.onChanged()


#
# View which represents the pivot editor
#
class PivotNodeView:

    def __init__(self, inRootNode, inOutputNode, inPreviewNode):
        self.mNodes = [ inRootNode, inOutputNode, inPreviewNode ]
        self.mData = { }
        self.mTextures = [ ]
        self.mAdvancedView = AdvancedOptionsView(self, None)

        self.load()

    # Ensure the root node is valid (the system will fail if it's removed)
    def _validateRootNode(self):
        if not self._isNodeValid(PivotNodeType.Input):
            raise Exception("Node '%s' no longer exists!" % self.getRootNode())

    # Get whether a given node type exists
    def _isNodeValid(self, inNodeType):
        if self.mNodes[inNodeType] is None or not cmds.objExists(self.mNodes[inNodeType]):
            return False
        return True

    # Get whether this view is valid for building
    def isValidForBuild(self):
        return self._isNodeValid(PivotNodeType.Input) and self._isNodeValid(PivotNodeType.Output)

    # Get the root node
    def getRootNode(self):
        return self.mNodes[PivotNodeType.Input]

    # Get the output node
    def getOutputNode(self):
        return self.mNodes[PivotNodeType.Output]

    # Get the preview node
    def getPreviewNode(self):
        return self.mNodes[PivotNodeType.Preview]

    # Load view data from the root node
    def load(self):
        self._validateRootNode()

        # The data is serialized as JSON in an attribute
        str = cmds.getAttr('%s.nodeData' % self.getRootNode())
        str = str if str is not None else '{}'
        self.mData = json.loads(str)

        if self.mData is None:
            self.mData = { }

        # Expand textures into views
        if 'Textures' in self.mData:
            self.mTextures = [ ]
            textureData = self.mData['Textures']

            for data in textureData:
                self.mTextures.append(OutputTextureView(self, data))

        # Advanced options
        self.mAdvancedView = AdvancedOptionsView(self, self.mData['Advanced'] if 'Advanced' in self.mData else None)

    # Save view data into the root node
    def save(self):
        self._validateRootNode()

        # Collapse texture views back to data
        textureData = [ ]
        for model in self.mTextures:
            textureData.append(model.mData)
        self.mData['Textures'] = textureData

        # Advanced options
        self.mData['Advanced'] = self.mAdvancedView.mData

        str = json.dumps(self.mData)
        cmds.setAttr('%s.nodeData' % self.getRootNode(), str, type='string')

    # Notification of a UI event which dirties the view
    def onChanged(self):
        self.save()

    # Get index of the most valid visible node
    def _getCurrentVisibleNode(self):

        for type in range(0, PivotNodeType.Count):
            if self._isNodeValid(type) and cmds.getAttr('%s.visibility' % self.mNodes[type]):
                return type
        return PivotNodeType.Input

    # Gets whether the 'input' node is visible
    def getInputVisible(self):
        return self._getCurrentVisibleNode() == PivotNodeType.Input

    # Gets whether the 'output' node is visible
    def getOutputVisible(self):
        return self._getCurrentVisibleNode() == PivotNodeType.Output

    # Gets whether the 'preview; node is visible
    def getPreviewVisible(self):
        return self._getCurrentVisibleNode() == PivotNodeType.Preview

    # Set which node should be visible
    def setCurrentVisibleNode(self, inNode):
        for type in range(0, PivotNodeType.Count):
            if self._isNodeValid(type):
                cmds.setAttr('%s.visibility' % self.mNodes[type], inNode == type)

    # Get the advanced options view
    def getAdvancedView(self):
        return self.mAdvancedView

    # Get the texture views
    def getTextureViews(self):
        return self.mTextures

    # Trigger regeneration of the output geometry
    def regenerateOutput(self):
        BuildOutput.runTasks(self)

    # Perform a default export of textures
    def exportTextures(self):
        exportPath = self.getAdvancedView().getExportPath()
        if exportPath is None or not os.path.exists(exportPath):
            self.exportTexturesAs()
        else:
            self._exportTextures()

    # Perform an export of textures, but prompt for target directory first
    def exportTexturesAs(self):
        exportPath = self.getAdvancedView().getExportPath()
        exportPath = cmds.fileDialog2(fm=3, dir=exportPath if exportPath is not None and os.path.exists(exportPath) else None)

        exportPath = exportPath[0] if exportPath is not None and len(exportPath) > 0 else None
        if exportPath is None:
            return

        self.getAdvancedView().setExportPath(exportPath)
        self._exportTextures()

    def _exportTextures(self):
        exportPath = self.getAdvancedView().getExportPath()

        # Things an easily go wrong here
        success = []
        fail = []

        for texture in self.getTextureViews():
            destPath = ''
            try:
                # Validate state of the generated texture
                sourcePath = texture.getOutputPath()
                if sourcePath is None:
                    raise Exception("Can't export %s, you need to regenerate outputs first! [ExpNone]" % texture.getDisplayName())
                if not os.path.exists(sourcePath):
                    raise Exception("Can't export %s, you need to regenerate outputs first! [ExpExist]" % texture.getDisplayName())

                # Copy the generated texture to the export directory
                destPath = os.path.join(exportPath, os.path.split(sourcePath)[-1])
                shutil.copyfile(sourcePath, destPath)

            except Exception as ex:
                fail.append(str(ex))
            else:
                success.append('Exported texture: %s' % destPath)

        resultMessage = '\n'.join(fail + success)

        # Show an error dialog if things broke
        if len(fail) > 0:
            cmds.confirmDialog(title='Export Errors', message=resultMessage, icon='critical')
        print resultMessage

    # Add an output texture to the UI
    def addTextureOutput(self):
        view = OutputTextureView(self, None)
        self.mTextures.append(view)

        self.onChanged()

        return view

    # Remove an output texture from the UI
    def removeTextureOutput(self, inView):
        self.mTextures = [view for view in self.mTextures if view != inView]
        self.onChanged()


# Find the 'root' pivot node from a given selected node
def _findRootNode(inNode):

    type = cmds.nodeType(inNode)
    if type == PivotNode.Name:
        return inNode

    if type != PivotOutputNode.Name and type != PivotPreviewNode.Name:
        return None

    inputs = cmds.listConnections('%s.inputPivotNode' % inNode)
    if inputs:
        input = inputs[0]
        if cmds.nodeType(input) == PivotNode.Name:
            return input

        raise Exception('Traversed inputPivotNode link and found \'%s\' which isn\'t correct?' % input)

    return None


# Get a PivotNodeView from a given selected node
def fromNode(inNode):

    root = _findRootNode(inNode)
    if root is None:
        return None

    outputs = cmds.listConnections('%s.outputPivotNode' % root)
    previews = cmds.listConnections('%s.previewPivotNode' % root)

    output = outputs[0] if outputs is not None and len(outputs) > 0 else None
    preview = previews[0] if previews is not None and len(previews) > 0 else None

    return PivotNodeView(root, output, preview)
