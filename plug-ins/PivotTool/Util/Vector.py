"""
    This module is part of the PivotToolPlugin.

    For license details please check: PivotTool-License.txt
"""

import math

#
# Just some handy vector ops
#


# Add components of two vectors
def add(inA, inB):
    return [inA[i] + inB[i] for i in range(min(len(inA), len(inB)))]


# Subtract components of inB from inA
def sub(inA, inB):
    return [inA[i] - inB[i] for i in range(min(len(inA), len(inB)))]


# Multiply the components of inA and inB
def mul(inA, inB):
    return [inA[i] * inB[i] for i in range(min(len(inA), len(inB)))]


# Get the dot product of inA and inB
def dot(inA, inB):
    return sum(mul(inA, inB))


# Get the abs()'d dot of inA and inB
def dotAbs(inA, inB):
    return abs(dot(inA, inB))


# Get a normalized version of inVec
def normalize(inVec):
    mag = math.sqrt(abs(sum(inVec)))
    return [c / mag for c in inVec]


# Scale and bias the vector from [-1, 1] to [0, 1] space
def toTextureSpace(inVec):
    return [c * 0.5 + 0.5 for c in inVec]
