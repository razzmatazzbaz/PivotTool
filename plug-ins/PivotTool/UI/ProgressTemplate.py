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
# Dialog with a progressbar
#
class ProgressTemplate(QtWidgets.QDialog):

    def __init__(self, inDisplayName, inParent=None):
        self.mUIPath = os.path.join(os.path.abspath(os.path.dirname(inspect.getsourcefile(lambda: 0))), 'ProgressTemplate.ui')
        super(ProgressTemplate, self).__init__(inParent)

        if self.mUIPath:
            loader = CustomEditorTemplate.UILoader(self)
            widget = loader.load(self.mUIPath)
            QtCore.QMetaObject.connectSlotsByName(widget)

        self.setWindowTitle(inDisplayName)
        self.setProgress(0.0)
        self.setDisplayString('')

    def setProgress(self, inPercent):
        self.mProgressBar.setValue(int(inPercent))

    def setDisplayString(self, inMessage):
        self.mLabel.setText(inMessage)
