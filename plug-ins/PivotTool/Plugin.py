"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import Menu
import Nodes.PivotNodes
import UI.CustomEditorTemplate
import UI.PivotNodeTemplate

# Custom Templates
Templates = {
    'PivotNode': UI.PivotNodeTemplate.PivotNodeTemplate,
    'PivotOutputNode': UI.PivotNodeTemplate.PivotNodeTemplate
}

# Custom Commands
Commands = [
    UI.CustomEditorTemplate.BuildCommand,
    UI.CustomEditorTemplate.UpdateCommand
]

# Custom Transform Nodes
TransformNodes = [
    [ Nodes.PivotNodes.PivotNode, Nodes.PivotNodes.PivotTransformMatrix ],
    [ Nodes.PivotNodes.PivotOutputNode, Nodes.PivotNodes.PivotTransformMatrix ],
    [ Nodes.PivotNodes.PivotPreviewNode, Nodes.PivotNodes.PivotTransformMatrix ]
]


# Plugin Startup
def onInitialize(inPlugin):

    # Register custom templates
    for nodeType, template in Templates.iteritems():
        UI.CustomEditorTemplate.registerTemplate(nodeType, template)

    # Register custom commands
    for type in Commands:
        inPlugin.registerCommand(type.Name, type.Creator)

    # Register custom transform nodes
    for node in TransformNodes:
        inPlugin.registerTransform(node[0].Name, node[0].ID, node[0].Creator, node[0].Initialize, node[1].Creator, node[1].ID)

    # Add to build in Maya UIs
    Menu.registerMenu()


# Plugin Shutdown
def onUninitialize(inPlugin):

    # Deregister custom transform nodes
    for node in TransformNodes:
        inPlugin.deregisterNode(node[0].ID)

    # Deregister custom commands
    for type in Commands:
        inPlugin.deregisterCommand(type.Name)

    # Clean up menus
    Menu.unregisterMenu()
