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
from ..Gen.RenderType import *


#
# UI widget for an output texture
#
class OutputTextureTemplate(CustomEditorTemplate.QEditorTemplate):

    def __init__(self, inNode, inView, inParent=None):
        self.mUIPath = os.path.join(os.path.abspath(os.path.dirname(inspect.getsourcefile(lambda: 0))), 'OutputTextureTemplate.ui')
        self.mView = inView
        self.mParentTemplate = None
        super(OutputTextureTemplate, self).__init__(inNode, inParent)

        self.mRemoveButton.setIcon(QtGui.QPixmap(':closeTabButton.png'))

        # Build RGB List
        rgbIndex = 0
        rgbItems = RenderType.getRGBs()
        for item in rgbItems:
            self.mRGBCombo.addItem(item.getDisplayName(), item)

            if item.getType() == self.mView.getRGB():
                rgbIndex = self.mRGBCombo.count() - 1

        # Update selected item and add bindings
        self.mRGBCombo.setCurrentIndex(rgbIndex)
        self.mRGBCombo.currentIndexChanged.connect(self.rgbComboIndexChanged)

        # Build alpha combobox
        self.mAlphaCombo.currentIndexChanged.connect(self.alphaComboIndexChanged)
        self.rebuildAlphaCombo()

        # Remove button
        self.mRemoveButton.clicked.connect(self.removeButtonClicked)

    def setParentTemplate(self, inParent):
        self.mParentTemplate = inParent

    def rebuildAlphaCombo(self):
        if self.mView is None:
            return

        # Alpha items are based on RGB precision
        currentRGB = self.mView.getRGB()
        currentRGBItem = RenderType.fromType(currentRGB)
        currentA = self.mView.getA()
        aIndex = 0

        # Clear existing items
        while self.mAlphaCombo.count() > 0:
            self.mAlphaCombo.removeItem(0)

        # Build list
        alphaItems = RenderType.getAlphas(currentRGBItem.getPrecision())
        for item in alphaItems:
            self.mAlphaCombo.addItem(item.getDisplayName(), item)

            if item.getType() == currentA:
                aIndex = self.mAlphaCombo.count() - 1

        # Forcibly set index, this will call setA() again
        self.mAlphaCombo.setCurrentIndex(aIndex)

    def alphaComboIndexChanged(self, inIndex):
        item = self.mAlphaCombo.itemData(inIndex)
        if item is not None:
            self.mView.setA(item.getType())

    def rgbComboIndexChanged(self, inIndex):
        item = self.mRGBCombo.itemData(inIndex)

        # Monitor for changes to the alpha channel, since a precision change will invalidate the alpha selection
        currentA = self.mView.getA()
        self.mView.setRGB(item.getType())
        newA = self.mView.getA()

        # If the alpha changed, then rebuild the combo
        if currentA != newA or newA == RenderType.NoRender:
            self.rebuildAlphaCombo()

    def removeButtonClicked(self):
        if self.mView is None:
            return

        self.mView.removeSelf()
        self.mParentTemplate.onResetUI()
