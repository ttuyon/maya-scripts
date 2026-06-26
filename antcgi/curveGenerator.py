import maya.cmds as cmds
import math

def circle(name: str, radius=1):
    return cmds.circle(center=(0, 0, 0), normal=(0, 1, 0), sweep=360, tolerance=0, constructionHistory=False, name=name, radius=radius)[0]

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
    
    curve = cmds.curve(name=name, d=1, p=points)
    cmds.makeIdentity(curve, apply=True, t=0, r=0, s=1, n=0)
    cmds.xform(curve, cp=True)

    return curve

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

    rootCurve = cmds.group(empty=True, name=name)

    bbox = cmds.exactWorldBoundingBox(curvesGrp)
    centerX = (bbox[0] + bbox[3]) / 2
    centerY = (bbox[1] + bbox[4]) / 2

    cmds.move(-centerX, -centerY, 0, curvesGrp, absolute=True, worldSpace=True)

    for charParent in charParents:
        shapeParent = cmds.listRelatives(charParent)
        cmds.parent(*shapeParent, world=True)
        cmds.makeIdentity(*shapeParent, apply=True, translate=True)
        cmds.parent(*cmds.listRelatives(shapeParent), rootCurve, relative=True, shape=True)
        cmds.delete(shapeParent)

    cmds.delete(*charParents, curvesGrp)

    cmds.xform(rootCurve, centerPivots=True)
    cmds.makeIdentity(rootCurve, apply=True, translate=True, rotate=True, scale=True)
    
    return rootCurve

def arrow(name: str, shaftWidth=1.0, shaftHeight:float|None=None, headWidth:float|None=None, headHeight:float|None=None):
    shaftHeight = shaftHeight or round(shaftWidth * 0.5, 2)
    headWidth = headWidth or round(shaftWidth * 0.8, 2)
    headHeight = headHeight or round(shaftWidth * 1, 2)

    totalWidth = shaftWidth + headWidth
    zOffset = totalWidth / 2.0

    halfShaftH = shaftHeight / 2.0
    halfHeadH = headHeight / 2.0

    points = [
        (-halfShaftH, 0, -zOffset),
        (-halfShaftH, 0, shaftWidth - zOffset),
        (-halfHeadH, 0, shaftWidth - zOffset),
        (0, 0, shaftWidth + headWidth - zOffset),
        (halfHeadH, 0, shaftWidth - zOffset),
        (halfShaftH, 0, shaftWidth - zOffset),
        (halfShaftH, 0, -zOffset),
        (-halfShaftH, 0, -zOffset)
    ]

    return cmds.curve(name=name, d=1, p=points)

def twoDirArrow(name: str, shaftWidth:float=1, shaftHeight:float|None=None, headWidth:float|None=None, headHeight:float|None=None):
    shaftHeight = shaftHeight or round(shaftWidth * 0.3, 2)
    headWidth = headWidth or round(shaftWidth * 0.4, 2)
    headHeight = headHeight or round(shaftWidth * 0.6, 2)

    halfShaft = shaftWidth / 2.0
    halfShaftH = shaftHeight / 2.0
    halfHeadH = headHeight / 2.0

    points = [
        (-halfShaft - headWidth, 0, 0),
        (-halfShaft, 0, halfHeadH),
        (-halfShaft, 0, halfShaftH),
        (halfShaft, 0, halfShaftH),
        (halfShaft, 0, halfHeadH),
        (halfShaft + headWidth, 0, 0),
        (halfShaft, 0, -halfHeadH),
        (halfShaft, 0, -halfShaftH),
        (-halfShaft, 0, -halfShaftH),
        (-halfShaft, 0, -halfHeadH),
        (-halfShaft - headWidth, 0, 0),
    ]

    curve = cmds.curve(name=name, d=1, p=points)
    cmds.xform(curve, centerPivots=True)

    return curve

def radialArrow(name: str, centerRadius=2.0):
    numArrows=8
    arrowLength=round(centerRadius * 0.6, 2)
    arrowHeadWidth=round(centerRadius * 0.15, 2)
    arrowThickness=round(centerRadius * 0.08, 2)
    circleArrowGap=round(centerRadius * 0.1, 2)
    
    centerCircle = cmds.circle(name='centerCircle', radius=centerRadius, sections=16, normal=(0, 1, 0))[0]
    
    arrowCurves = []
    
    angleStep = 360.0 / numArrows
    
    for i in range(numArrows):
        currentAngle = math.radians(i * angleStep)
        
        # 화살표 시작점
        startDistance = centerRadius + circleArrowGap
        startX = startDistance * math.cos(currentAngle)
        startZ = startDistance * math.sin(currentAngle)
        
        # 화살표 끝점
        endDistance = startDistance + arrowLength
        endX = endDistance * math.cos(currentAngle)
        endZ = endDistance * math.sin(currentAngle)
        
        # 화살표 몸통의 두께를 위한 수직 벡터
        perpAngle = currentAngle + math.radians(90)
        thickX = arrowThickness * 0.5 * math.cos(perpAngle)
        thickZ = arrowThickness * 0.5 * math.sin(perpAngle)
        
        # 화살표 머리를 위한 넓은 부분 시작점 계산
        headStartDistance = endDistance - arrowHeadWidth * 0.7
        headStartX = headStartDistance * math.cos(currentAngle)
        headStartZ = headStartDistance * math.sin(currentAngle)
        
        # 화살표 머리의 너비 계산
        headThickness = arrowHeadWidth
        headThickX = headThickness * 0.5 * math.cos(perpAngle)
        headThickZ = headThickness * 0.5 * math.sin(perpAngle)
        
        # 몸통 두께를 위한 포인트들
        bodyStartX1 = startX + thickX
        bodyStartZ1 = startZ + thickZ
        bodyStartX2 = startX - thickX
        bodyStartZ2 = startZ - thickZ
        
        bodyEndX1 = headStartX + thickX
        bodyEndZ1 = headStartZ + thickZ
        bodyEndX2 = headStartX - thickX
        bodyEndZ2 = headStartZ - thickZ
        
        # 화살표 머리 부분 포인트들
        headWideX1 = headStartX + headThickX
        headWideZ1 = headStartZ + headThickZ
        headWideX2 = headStartX - headThickX
        headWideZ2 = headStartZ - headThickZ
        
        # 화살표 커브 포인트들
        arrowPoints = [
            (bodyStartX1, 0, bodyStartZ1),  # 몸통 시작 위쪽
            (bodyEndX1, 0, bodyEndZ1),      # 몸통 끝 위쪽
            (headWideX1, 0, headWideZ1),    # 화살표 머리 넓은 부분 위쪽
            (endX, 0, endZ),                # 화살표 끝점
            (headWideX2, 0, headWideZ2),    # 화살표 머리 넓은 부분 아래쪽
            (bodyEndX2, 0, bodyEndZ2),      # 몸통 끝 아래쪽
            (bodyStartX2, 0, bodyStartZ2),  # 몸통 시작 아래쪽
            (bodyStartX1, 0, bodyStartZ1)   # 시작점으로 닫기
        ]
        
        arrowCurve = cmds.curve(
            point=arrowPoints,
            degree=1,
            name=f'arrow_{i+1:02d}'
        )
        
        arrowCurves.append(arrowCurve)
    
    allCurves = [centerCircle] + arrowCurves
    
    mainCurve = allCurves[0]
    otherCurves = allCurves[1:]
    
    for curve in otherCurves:
        curveShape = cmds.listRelatives(curve, shapes=True)[0]
        cmds.parent(curveShape, mainCurve, relative=True, shape=True)
        cmds.delete(curve)
    
    return cmds.rename(mainCurve, name)
