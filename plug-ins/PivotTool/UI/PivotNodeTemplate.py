"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import inspect
import os
import maya.cmds as cmds
import maya.OpenMayaUI as ui
from PySide2 import QtGui, QtCore, QtWidgets

import CustomEditorTemplate
from OutputTextureTemplate import *
import PivotNodeView


#
# Attribute editor UI for a pivot node
#
class PivotNodeTemplate(CustomEditorTemplate.QEditorTemplate):

    def __init__(self, inNode, inParent=None):
        self.mUIPath = os.path.join(os.path.abspath(os.path.dirname(inspect.getsourcefile(lambda: 0))), 'PivotNodeTemplate.ui')

        super(PivotNodeTemplate, self).__init__(inNode, inParent)

        self.mAddTextureButton.setIcon(QtGui.QPixmap(':addClip.png'))
        self.mPreviewRadio.setVisible(False)

        self.mInputRadio.clicked.connect(self.previewTypeClicked)
        self.mPreviewRadio.clicked.connect(self.previewTypeClicked)
        self.mOutputRadio.clicked.connect(self.previewTypeClicked)
        self.mRegenerateButton.clicked.connect(self.regenerateButtonClicked)
        self.mAddTextureButton.clicked.connect(self.addTextureButtonClicked)
        self.mExportButton.clicked.connect(self.exportButtonClicked)
        self.mExportAsButton.clicked.connect(self.exportAsButtonClicked)

        self.onResetUI()

    def onResetUI(self):
        while self.mTextureFrame.count() > 0:
            item = self.mTextureFrame.itemAt(0).widget()
            self.mTextureFrame.removeWidget(item)
            item.setParent(None)

        self.mView = PivotNodeView.fromNode(self.mNode)
        if self.mView is None:
            return

        self.mInputRadio.setChecked(self.mView.getInputVisible())
        self.mPreviewRadio.setChecked(self.mView.getPreviewVisible())
        self.mOutputRadio.setChecked(self.mView.getOutputVisible())

        for item in self.mView.mTextures:
            widget = OutputTextureTemplate(self.mNode, item, self.mTextureFrame.parentWidget())
            widget.setParentTemplate(self)
            self.mTextureFrame.addWidget(widget)

    def previewTypeClicked(self):
        if self.mView is None:
            return

        activePreview = PivotNodeView.PivotNodeType.Input
        activePreview = PivotNodeView.PivotNodeType.Preview if self.mPreviewRadio.isChecked() else activePreview
        activePreview = PivotNodeView.PivotNodeType.Output if self.mOutputRadio.isChecked() else activePreview

        self.mView.setCurrentVisibleNode(activePreview)

    def regenerateButtonClicked(self):
        if self.mView is not None:
            self.mView.regenerateOutput()

    def addTextureButtonClicked(self):
        if self.mView is None:
            return

        self.mView.addTextureOutput()
        self.onResetUI()

    def exportButtonClicked(self):
        if self.mView is not None:
            self.mView.exportTextures()

    def exportAsButtonClicked(self):
        if self.mView is not None:
            self.mView.exportTexturesAs()
