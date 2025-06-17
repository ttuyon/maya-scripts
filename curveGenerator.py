import maya.cmds as cmds
import math

def circle(name: str, radius=1):
    cmds.circle(center=(0, 0, 0), normal=(0, 1, 0), sweep=360, tolerance=0, constructionHistory=False, name=name, radius=radius)
    return name

def cube(name: str, width=1):
    points = [
        [-width/2, width/2, -width/2],
        [ width/2, width/2, -width/2],
        [ width/2, width/2,  width/2],
        [-width/2, width/2,  width/2],
        [-width/2, width/2, -width/2],
        [-width/2, -width/2, -width/2],
        [-width/2, -width/2,  width/2],
        [ width/2, -width/2,  width/2],
        [ width/2, -width/2, -width/2],
        [-width/2, -width/2, -width/2],
        [-width/2, -width/2,  width/2],
        [-width/2, width/2,  width/2],
        [ width/2, width/2,  width/2],
        [ width/2, -width/2,  width/2],
        [ width/2, -width/2, -width/2],
        [ width/2, width/2, -width/2],
    ]
    
    cmds.curve(name=name, d=1, p=points)
    cmds.makeIdentity(name, apply=True, t=0, r=0, s=1, n=0)
    cmds.xform(name, cp=True)

    return name



def pyramid(name: str, width=1):
    half = width / 2.0
    height = math.sqrt(2.0 / 3.0) * width

    top = [0, height, 0]
    bl = [-half, 0, -half]
    br = [half, 0, -half]
    tr = [half, 0, half]
    tl = [-half, 0, half]

    points = [
        top, bl,
        top, br,
        top, tr,
        top, tl,
        bl, br,
        tr, tl,
        bl
    ]

    curve = cmds.curve(name=name, p=points, d=1)
    cmds.xform(curve, centerPivots=True)
    return curve

def text(name: str, text: str):
    curvesGrp = cmds.textCurves(text=text, font="Arial")[0]
    charParents = cmds.listRelatives(curvesGrp)

    cmds.group(empty=True, name=name)

    bbox = cmds.exactWorldBoundingBox(curvesGrp)
    centerX = (bbox[0] + bbox[3]) / 2
    centerY = (bbox[1] + bbox[4]) / 2

    cmds.move(-centerX, -centerY, 0, curvesGrp, absolute=True, worldSpace=True)

    for charParent in charParents:
        shapeParent = cmds.listRelatives(charParent)
        cmds.parent(*shapeParent, world=True)
        cmds.makeIdentity(*shapeParent, apply=True, translate=True)
        cmds.parent(*cmds.listRelatives(shapeParent), name, relative=True, shape=True)
        cmds.delete(shapeParent)

    cmds.delete(*charParents, curvesGrp)

    cmds.xform(name, centerPivots=True)
    cmds.makeIdentity(name, apply=True, translate=True, rotate=True, scale=True)
    
    return name


def twoDirArrow(name: str, shaftWidth=1, relative=False):
    shaftHeight = round((shaftWidth if relative else 1) * 0.3, 2)
    headLength = round((shaftWidth if relative else 1) * 0.4, 2)
    headHeight = round((shaftWidth if relative else 1) * 0.333, 2)

    halfShaft = shaftWidth / 2.0
    halfShaftH = shaftHeight / 2.0

    points = [
        (-halfShaft - headLength, 0, 0),
        (-halfShaft, headHeight, 0),
        (-halfShaft, halfShaftH, 0),
        (halfShaft, halfShaftH, 0),
        (halfShaft, headHeight, 0),
        (halfShaft + headLength, 0, 0),
        (halfShaft, -headHeight, 0),
        (halfShaft, -halfShaftH, 0),
        (-halfShaft, -halfShaftH, 0),
        (-halfShaft, -headHeight, 0),
        (-halfShaft - headLength, 0, 0),
    ]

    cmds.curve(name=name, d=1, p=points)
    cmds.xform(name, centerPivots=True)

    return name
