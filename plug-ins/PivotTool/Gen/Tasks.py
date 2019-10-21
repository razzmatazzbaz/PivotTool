"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import traceback
import maya.cmds as cmds
from ..UI.ProgressTemplate import ProgressTemplate


#
# Root task object
#
class Task:

    def __init__(self):
        pass

    def run(self, inState):
        pass

    def getDisplayString(self):
        return 'Default Task'

    def getTimeImpact(self):
        return 1.0


#
# Task processor
#
class TaskManager:

    def __init__(self):
        pass

    # Execute the array of input tasks
    @staticmethod
    def runTasks(inTasks, inDisplayName, inState, onSuccess = None, onFail = None):

        if len(inTasks) == 0:
            return

        # Determine a time scale for progressbar updates
        totalTime = 0.0
        for task in inTasks:
            totalTime = totalTime + max(0.001, task.getTimeImpact())
        timeScale = 1.0 / totalTime

        # Create progress dialog
        dialog = ProgressTemplate(inDisplayName)
        dialog.show()

        progress = 0
        taskNum = 1

        for task in inTasks:
            # Update the UI
            dialog.setProgress(progress)
            dialog.setDisplayString(task.getDisplayString())
            print '[%i/%i] %s' % (taskNum, len(inTasks), task.getDisplayString())
            cmds.refresh()

            # Run!
            try:
                task.run(inState)
            except:
                error = traceback.format_exc()
                dialog.close()

                print error
                if onFail is not None:
                    onFail(inState, error)
                return

            # Update progress
            progress = min(100.0, progress + (task.getTimeImpact() * timeScale * 100.0))
            taskNum = taskNum + 1

        dialog.close()

        print 'Tasks Complete!'
        if onSuccess is not None:
            onSuccess(inState)
