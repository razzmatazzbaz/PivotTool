"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import os
import inspect
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds


# Maya plugin initialize
def initializePlugin(obj):

    # Add the plugin path as a python module path
    toolPath = os.path.abspath(os.path.dirname(inspect.getsourcefile(lambda: 0)))
    if toolPath not in sys.path:
        sys.path.append(toolPath)

    # Add the tools script directory as a Maya source
    # This allows us to drop in custom AE scripts while keeping everything
    # contained inside the plugin
    scriptPath = os.path.join(toolPath, 'PivotTool', 'Scripts')
    currentPath = os.environ['MAYA_SCRIPT_PATH']
    if scriptPath not in currentPath:
        os.environ['MAYA_SCRIPT_PATH'] = '%s;%s' % (currentPath, scriptPath)

    # Dump path info, incase it's useful
    print '------------------------'
    print 'Pivot Tool Plugin Loaded'
    print ''
    print 'Module Path: %s' % toolPath
    print 'Script Path: %s' % scriptPath
    print '------------------------'

    # Load the module
    import PivotTool.Plugin

    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        # Run module initialization
        PivotTool.Plugin.onInitialize(plugin)
    except Exception as ex:
        print(ex)


# Maya plugin shutdown
def uninitializePlugin(obj):
    import PivotTool.Plugin

    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        # Shutdown the module
        PivotTool.Plugin.onUninitialize(plugin)
    except Exception as ex:
        print(ex)
