"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import maya.cmds as cmds

import Builder
import Tasks
import Trees
from RenderType import *


# Container for builder context actions
class BuildOutputState():
    def __init__(self, inView):
        self.mView = inView
        self.mBuilder = None
        self.mCachedHierarchy = None

    def getView(self):
        return self.mView

    def getBuilder(self):
        return self.mBuilder

    def getHierarchy(self):
        return self.mCachedHierarchy


# Task to clean the pivot output node
class CleanOutputTask(Tasks.Task):
    def __init__(self):
        pass

    def run(self, inState):

        # If we've previously generated an output then cache it's name since we can preserve it
        outputs = cmds.listConnections('%s.outputMesh' % inState.getView().getOutputNode())
        output = outputs[0] if outputs is not None and len(outputs) > 0 else None
        inState.mOutputName = output

        children = cmds.listRelatives(inState.getView().getOutputNode(), f=True)
        if children is not None:
            for child in children:
                cmds.delete(child)

    def getDisplayString(self):
        return 'Cleaning Output...'

    def getTimeImpact(self):
        return 5.0


# Task to copy the mesh hierarchy from the input to the output
class CopyHierarchyTask(Tasks.Task):
    def __init__(self):
        pass

    def run(self, inState):

        # JB: duplicate -un copies the root nodes, which is annoying
        existingNodes = cmds.ls(type='PivotNode')

        children = cmds.listRelatives(inState.getView().getRootNode(), f=True)
        children = cmds.duplicate(children, un=True, rr=True, rc=True)
        children = cmds.parent(children, inState.getView().getOutputNode())

        # Clean up the extra nodes
        newNodes = list(set(cmds.ls(type='PivotNode')) - set(existingNodes))
        if newNodes is not None and len(newNodes) > 0:
            cmds.delete(newNodes)

    def getDisplayString(self):
        return 'Copy Inputs...'

    def getTimeImpact(self):
        return 10.0


# Task to build the cached hierarchy and fill relevant information
class BuildHierarchyTask(Tasks.Task):
    def __init__(self):
        pass

    def _printHierarchy(self, inNode, inParent):

        inNode.mDbgDepth = inParent.mDbgDepth + 1 if inParent is not None else 0

        pad = ''
        for i in range(0, inNode.mDbgDepth):
            pad = pad + '    '
        
        print '%s%s' % (pad, inNode.mNode)

    def run(self, inState):
        inState.mBuilder = Builder.Builder(inState.getView())

        hierarchy = Trees.getMeshHierarchy(inState.getView().getOutputNode())
        hierarchy = hierarchy.filterByShape(['mesh'])
        if hierarchy is None:
            raise Exception('Filtered hierarchy contains no valid mesh elements!')

        hierarchy.mDataBuilder = None

        # The pivot root isn't always going to be the primary root of the object, so ensure it's invalidated
        if len(hierarchy.mChildren) <= 1:
            hierarchy.mChildren[0].iterate(inState.getBuilder().fillHierarchyInfo)
        else:
            hierarchy.iterate(inState.getBuilder().fillHierarchyInfo)

        inState.mCachedHierarchy = hierarchy

        # Debug print the hierarchy
        # hierarchy.iterate(self._printHierarchy)

    def getDisplayString(self):
        return 'Build Hierarchy...'

    def getTimeImpact(self):
        return 5.0


# Task to setup builder textures
class GenerateTextureInfoTask(Tasks.Task):
    def __init__(self):
        pass

    def run(self, inState):
        inState.getBuilder().generateTextureInfo()

    def getDisplayString(self):
        return 'Update Texture Info...'

    def getTimeImpact(self):
        return 5.0


# Task to perform UV positioning
class LayoutUVsTask(Tasks.Task):
    def __init__(self):
        pass

    def run(self, inState):
        inState.getHierarchy().iterate(inState.getBuilder().layoutUVs)

    def getDisplayString(self):
        return 'Layout UVs...'

    def getTimeImpact(self):
        return 30.0


# Task to fill texture data
class RenderTexturesTask(Tasks.Task):
    def __init__(self):
        pass

    def run(self, inState):
        inState.getHierarchy().iterate(inState.getBuilder().renderTextures)

    def getDisplayString(self):
        return 'Render Textures...'

    def getTimeImpact(self):
        return 30.0


# Task to write textures to disk
class WriteTexturesTask(Tasks.Task):
    def __init__(self):
        pass

    def run(self, inState):
        inState.getBuilder().writeTextures()

    def getDisplayString(self):
        return 'Write Textures...'

    def getTimeImpact(self):
        return 20.0


# Task to merge output geometry and clean up the results
class CombineOutputsTask(Tasks.Task):
    def __init__(self):
        pass

    def _canMerge(self, inNodeName):
        if cmds.objectType(inNodeName) == 'mesh':
            return True

        shapes = cmds.listRelatives(inNodeName, s=True, typ='mesh')
        if shapes is not None and len(shapes) > 0:
            return True

        return False

    def run(self, inState):
        # Merge all child meshes under the output mode
        children = cmds.listRelatives(inState.getView().getOutputNode(), f=True)
        children = [child for child in children if self._canMerge(child)]
        united = children
        
        if len(children) > 0:
            try:
                # You could have a single object which is a root of many child objects
                # I could check for that...
                united = cmds.polyUnite(children, ch=True, mergeUVSets=True, centerPivot=True)
            except:
                pass

        # Clean the construction history
        cmds.select(united[0], r=True)
        cmds.delete(ch=True)

        # Ensure the output is correctly parented
        finalName = united[0]
        try:
            finalName = cmds.parent(united[0], inState.getView().getOutputNode())[0]
        except:
            pass

        # Add a link from the output node so we can track it in the future
        cmds.addAttr(ln='pivotParent', at='message')
        cmds.connectAttr('%s.outputMesh' % inState.getView().getOutputNode(), '%s.pivotParent' % finalName)

        # If there is an output name then use it since polySurfaceN is boring!
        if inState.mOutputName is not None:
            finalName = cmds.rename(finalName, inState.mOutputName.split('|')[-1])

        # Filter out any non-merged nodes
        # These could be joints, lights or anything else attached to the objects
        children = cmds.listRelatives(inState.getView().getOutputNode(), f=True)
        children = [child for child in children if child.split('|')[-1] != finalName.split('|')[-1]]
        for child in children:
            cmds.delete(child)

    def getDisplayString(self):
        return 'Combine Outputs...'

    def getTimeImpact(self):
        return 10.0


# Construct pivot geometry and textures based upon an input view
def runTasks(inView):

    state = BuildOutputState(inView)
    if not state.getView().isValidForBuild():
        raise Exception("Can't build object because it's missing an input ('%s') or output ('%s')!" % (state.getView().getRootNode(), state.getView().getOutputNode()))

    # Cache selection
    selection = cmds.ls(sl=True)

    tasks = [
        CleanOutputTask(),
        CopyHierarchyTask(),
        BuildHierarchyTask(),
        GenerateTextureInfoTask(),
        LayoutUVsTask(),
        RenderTexturesTask(),
        CombineOutputsTask(),
        WriteTexturesTask()
    ]

    Tasks.TaskManager.runTasks(tasks, 'Generating Output...', state)

    # Restore selection
    cmds.select(selection, r=True)
