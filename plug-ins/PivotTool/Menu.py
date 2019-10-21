"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import maya.cmds as cmds
import maya.mel as mel

MenuItems = [ ]


# Handle creation of a pivot set
def _createPivotSet(*args):

    # Grab selection to reparent
    selection = cmds.ls(sl=True)

    # Create pivot nodes and link them
    inputNode = cmds.createNode('PivotNode')
    outputNode = cmds.createNode('PivotOutputNode')
    cmds.connectAttr('%s.outputPivotNode' % inputNode, '%s.inputPivotNode' % outputNode)

    cmds.setAttr('%s.visibility' % outputNode, False)

    # Apply parenting and select the target node
    if selection is not None and len(selection) > 0:
        cmds.parent(selection, inputNode)
    cmds.select(inputNode, r=True)


# Custom menu implementation
def registerMenu():
    global MenuItems

    menuRegionName = 'Razzle Dazzle'

    # Force creation of 'create' menu
    mel.eval('ModCreateMenu $gMainCreateMenu')

    # Get existing menu and items
    createMenu = mel.eval('$temp = $gMainCreateMenu')
    createItems = cmds.menu(createMenu, q=True, ia=True)

    # Find out if our menu area exists, if not add it
    hasExtra = [item for item in createItems if cmds.menuItem(item, q=True, l=True) == menuRegionName]

    if len(hasExtra) == 0:
        MenuItems.append(cmds.menuItem(parent=createMenu, l=menuRegionName, d=True))

        # Functionality to create a pivot set
        MenuItems.append(cmds.menuItem(parent=createMenu, l='Create Pivot Set', c=_createPivotSet))


# Clean up custom menus
def unregisterMenu():
    global MenuItems

    for item in MenuItems:
        cmds.deleteUI(item)

    MenuItems = [ ]
