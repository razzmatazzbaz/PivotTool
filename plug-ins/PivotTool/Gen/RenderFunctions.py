"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""


import math
import random
import maya.cmds as cmds

from ..Util import Half
from ..Util import Vector


# Clamp a value between a min and max
def clamp(inV, inMin, inMax):
    return min(inMax, max(inMin, inV))


# Convert an int16 to an fp16 compatible value
def int16ToHalf(inValue):
    # +1024 ensures exp is at least 1 (or the value will be zeroed)
    return Half.ToSingle(int(inValue) + 1024)


def pivotPosition(inNode, outPixel, inContext):
    outPixel.setRGB(cmds.xform(inNode.getNode(), q=True, ws=True, rp=True))


def originPosition(inNode, outPixel, inContext):
    # JB: The Max script uses object.center, I don't know if the BB center is actually equivalent,
    #     since the function refers to the origin? Check Max docs when you get a chance!
    bb = cmds.xform(inNode.getNode(), q=True, ws=True, bb=True)
    outPixel.setRGB(Vector.sub(bb[3:6], bb[0:3]))


def extents(inNode, outPixel, inContext):
    t = outPixel
    a = outPixel.getA()
    v = [0, 0, 0]
    maxBoundingBoxDistanceX(inNode, t, inContext)
    v[0] = t.getA()
    maxBoundingBoxDistanceY(inNode, t, inContext)
    v[1] = t.getA()
    maxBoundingBoxDistanceZ(inNode, t, inContext)
    v[2] = t.getA()
    outPixel.setRGB(v)
    outPixel.setA(a)


def parentIndexInt(inNode, outPixel, inContext):
    index = inNode.getParentIndex()

    if index < 0:
        index = inNode.getIndex()
    outPixel.setA(int16ToHalf(index))


def parentIndexFloat(inNode, outPixel, inContext):
    index = inNode.getParentIndex()

    if index < 0:
        index = inNode.getIndex()
    outPixel.setA(float(index))


def xvector(inNode, outPixel, inContext):
    m = cmds.xform(inNode.getNode(), q=True, ws=True, m=True)
    v = Vector.toTextureSpace(Vector.normalize(m[0:3]))
    outPixel.setRGB(v)


def yvector(inNode, outPixel, inContext):
    m = cmds.xform(inNode.getNode(), q=True, ws=True, m=True)
    v = Vector.toTextureSpace(Vector.normalize(m[4:7]))
    outPixel.setRGB(v)


def zvector(inNode, outPixel, inContext):
    m = cmds.xform(inNode.getNode(), q=True, ws=True, m=True)
    v = Vector.toTextureSpace(Vector.normalize(m[8:11]))
    outPixel.setRGB(v)


def maxBoundingBoxDistanceX(inNode, outPixel, inContext):
    bb = cmds.xform(inNode.getNode(), q=True, bb=True)
    vec = Vector.normalize(cmds.xform(inNode.getNode(), q=True, ws=True, m=True)[0:3])
    outPixel.setA(Vector.dotAbs(Vector.sub(bb[3:6], bb[0:3]), vec))


def maxBoundingBoxDistanceY(inNode, outPixel, inContext):
    bb = cmds.xform(inNode.getNode(), q=True, bb=True)
    vec = Vector.normalize(cmds.xform(inNode.getNode(), q=True, ws=True, m=True)[4:7])
    outPixel.setA(Vector.dotAbs(Vector.sub(bb[3:6], bb[0:3]), vec))


def maxBoundingBoxDistanceZ(inNode, outPixel, inContext):
    bb = cmds.xform(inNode.getNode(), q=True, bb=True)
    vec = Vector.normalize(cmds.xform(inNode.getNode(), q=True, ws=True, m=True)[8:11])
    outPixel.setA(Vector.dotAbs(Vector.sub(bb[3:6], bb[0:3]), vec))


def boundingBoxDiameter(inNode, outPixel, inContext):
    bb = cmds.xform(inNode.getNode(), q=True, bb=True)
    d = Vector.sub(bb[3:5], bb[0:3])
    outPixel.setA(math.sqrt(Vector.dot(d, d)))


def maxBoundingBoxDistanceXLDR(inNode, outPixel, inContext):
    maxBoundingBoxDistanceX(inNode, outPixel, inContext)
    outPixel.setA(clamp(math.ceil(outPixel.getA() / 8.0), 1.0, 256.0) / 256.0)


def maxBoundingBoxDistanceYLDR(inNode, outPixel, inContext):
    maxBoundingBoxDistanceY(inNode, outPixel, inContext)
    outPixel.setA(clamp(math.ceil(outPixel.getA() / 8.0), 1.0, 256.0) / 256.0)


def maxBoundingBoxDistanceZLDR(inNode, outPixel, inContext):
    maxBoundingBoxDistanceZ(inNode, outPixel, inContext)
    outPixel.setA(clamp(math.ceil(outPixel.getA() / 8.0), 1.0, 256.0) / 256.0)


def stepsToRoot(inNode, outPixel, inContext):
    outPixel.setA(float(inNode.getDepth()))


def normalizedStepsToRoot(inNode, outPixel, inContext):
    outPixel.setA(inNode.mDepth / inContext.mMaxDepth)


def random01(inNode, outPixel, inContext):
    outPixel.setA(random.random())
