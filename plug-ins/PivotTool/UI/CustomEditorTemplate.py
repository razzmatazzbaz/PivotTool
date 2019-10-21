"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import maya.cmds as cmds
import maya.OpenMayaUI as ui
import maya.OpenMayaMPx as mpx
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtGui, QtCore, QtWidgets
import shiboken2

# Mapping of node types to custom template renderers
CustomTemplates = { }

# A collection of active layout widgets
# These are essential to ensure the layout doesn't go out of scope, which causes destruction
# of the  PySide objects beneath (causing sockets to break). If there is a better way of doing
# this then I'd love to know :/
ActiveWidgets = { }


#
# Custom UI Loader class to intercept widget creation
# See: https://robonobodojo.wordpress.com/2018/10/29/pyside2-widget-class-from-a-qt-designer-ui/
#
class UILoader(QUiLoader):

    def __init__(self, inTarget):
        QUiLoader.__init__(self, inTarget)
        self.mTarget = inTarget

    def createWidget(self, inClassName, inParent = None, inName = ''):
        if inParent is None and self.mTarget:
            return self.mTarget
        else:
            widget = QUiLoader.createWidget(self, inClassName, inParent, inName)
            if self.mTarget:
                setattr(self.mTarget, inName, widget)
            return widget


#
# Root widget that contains custom template implementations
#
class QEditorTemplate(QtWidgets.QWidget):

    def __init__(self, inNode, inParent = None):
        super(QEditorTemplate, self).__init__(inParent)
        self.mNode = inNode

        if self.mUIPath:
            loader = UILoader(self)
            widget = loader.load(self.mUIPath)
            QtCore.QMetaObject.connectSlotsByName(widget)

            layout = QtWidgets.QFormLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(widget)

            self.setLayout(layout)

    def setNode(self, inNode):
        self.mNode = inNode
        self.onResetUI()

    def onResetUI(self):
        pass


#
# Global command passed to 'build' phase of editorTemplate -callCustom
#
class BuildCommand(mpx.MPxCommand):
    Name = 'BuildCustomEditorTemplate'

    def __init__(self):
        mpx.MPxCommand.__init__(self)

    def doIt(self, inArgs):
        nodeName = inArgs.asString(0).rstrip('.')
        parent = cmds.setParent(q = True)

        buildEditorTemplate(parent, nodeName)

    @staticmethod
    def Creator():
        return BuildCommand()


#
# Global command passed to 'update' phase of editorTemplate -callCustom
#
class UpdateCommand(mpx.MPxCommand):
    Name = 'UpdateCustomEditorTemplate'

    def __init__(self):
        mpx.MPxCommand.__init__(self)

    def doIt(self, inArgs):
        nodeName = inArgs.asString(0).rstrip('.')
        parent = cmds.setParent(q = True)

        updateEditorTemplate(parent, nodeName)

    @staticmethod
    def Creator():
        return UpdateCommand()


# Register a template with a node type
def registerTemplate(inNodeType, inTemplate):
    global CustomTemplates

    if not issubclass(inTemplate, QEditorTemplate):
        raise Exception("Can't register custom editor template for '%s' as '%s' must inherit from QEditorTemplate!" % (inNodeType, inTemplate))

    CustomTemplates[inNodeType] = inTemplate


# Find a layout by name
def findLayout(inLayout):
    global ActiveWidgets

    asWidget = None
    if inLayout in ActiveWidgets:
        asWidget = ActiveWidgets[inLayout]
    else:
        hwidget = ui.MQtUtil.findLayout(inLayout)
        if hwidget is None:
            return (None, None)

        asWidget = shiboken2.wrapInstance(long(hwidget), QtWidgets.QWidget)
    layout = asWidget.layout()

    ActiveWidgets[inLayout] = asWidget

    # This is necessary as PySide will clean up the widget because it's a temporary? Cry.
    return (asWidget, layout)


# Find the editor template for a given node
def findTemplate(inNode):
    global CustomTemplates

    nodeType = cmds.nodeType(inNode)
    if nodeType not in CustomTemplates:
        raise Exception("Custom editor template '%s' not registered!" % nodeType)

    return CustomTemplates[nodeType]


# Implmentation of the 'build' phase of editorTemplate -callCustom
def buildEditorTemplate(inLayout, inNode):

    # Get layout/template
    layoutWidget, layout = findLayout(inLayout)
    template = findTemplate(inNode)

    # Construct and assign
    widget = template(inNode)
    layout.addWidget(widget)


# Implmentation of the 'update' phase of editorTemplate -callCustom
def updateEditorTemplate(inLayout, inNode):

    # Get layout/template
    __unused, layout = findLayout(inLayout)
    template = findTemplate(inNode)

    # Find element which corresponds to our QEditorTemplate widget and assign a node
    for c in range(layout.count()):
        widget = layout.itemAt(c).widget()
        if isinstance(widget, template):
            widget.setNode(inNode)
            break
