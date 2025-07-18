import sys
import maya.mel as mel

modulePath = mel.eval('getenv "MAYA_MY_SCRIPT_PATH"')
if modulePath not in sys.path:
    sys.path.append(modulePath)

import importlib
import maya.cmds as cmds
import utils
import curveGenerator

importlib.reload(utils)
importlib.reload(curveGenerator)

############# Constants
COLOR_INDEX_RED = 13
COLOR_INDEX_BLUE = 6
COLOR_INDEX_YELLOW = 17
COLOR_INDEX_SKYBLUE = 18
COLOR_INDEX_LIGHTGREEN = 14

ROOT_CTRL_NAME = 'root_ctrl'

def getCtrlColorByName(name):
    if name.startswith("l_"):
        return COLOR_INDEX_BLUE
    elif name.startswith("r_"):
        return COLOR_INDEX_RED
    else:
        return COLOR_INDEX_YELLOW
    
def setControllerColor(ctrlName: str):
    utils.setShapeColor(ctrlName, getCtrlColorByName(ctrlName))

def getLegJoints():
    selection = cmds.ls(selection=True, type='joint')

    if len(selection) != 1:
        raise Exception("Please select a root joint!")
        
    joints = cmds.listRelatives(selection[0], type='joint', allDescendents=True)[-3:]
    joints.append(selection[0])
    joints.reverse()

    return joints

def createFKControllers(legJoints: list[str], modelRelativeHorizontalAxes: str, scaleMulti=1):
    rootObjects = []

    for i, joint in enumerate(legJoints):
        ctrl = curveGenerator.circle(f'{joint}_fk_ctrl', 6 * scaleMulti)
        setControllerColor(ctrl)

        if i != len(legJoints) - 1:
            cmds.setAttr(f'{ctrl}.rotate{modelRelativeHorizontalAxes.capitalize()}', 90)
            cmds.makeIdentity(ctrl, rotate=True, apply=True)
        
        offsetGrp = cmds.group(ctrl, name=f'{ctrl}_offset')
        cmds.matchTransform(offsetGrp, joint, position=True, rotation=True)

        if i > 0:
            cmds.parent(offsetGrp, f'{legJoints[i - 1]}_fk_ctrl')
        else:
            rootObjects.append(offsetGrp)
    
    return rootObjects

def createIKControllers(legJoints: list[str], isRear: bool, scaleMulti=1) -> list[str]:
    rootObjects = []

    direction = legJoints[0][0]
    ctrlPrefix = f"{direction}_leg_{'rear' if isRear else 'front'}"

    # leg IK controller
    footJoint = legJoints[len(legJoints) - 1]

    ikCtrl = curveGenerator.circle(f'{ctrlPrefix}_ik_ctrl', 6 * scaleMulti)
    setControllerColor(ikCtrl)
    cmds.matchTransform(ikCtrl, footJoint, position=True)
    cmds.setAttr(f'{ikCtrl}.translateY', 0)
    
    ikCtrlOffsetGrp = cmds.group(empty=True, name=f'{ikCtrl}_offset')
    cmds.matchTransform(ikCtrlOffsetGrp, footJoint, position=True, rotation=True)

    cmds.parent(ikCtrl, ikCtrlOffsetGrp)
    cmds.makeIdentity(ikCtrl, apply=True, translate=True, rotate=True, scale=True, preserveNormals=True, normal=False)
    cmds.matchTransform(ikCtrl, ikCtrlOffsetGrp, pivots=True)

    # leg Ik Controller - attributes
    cmds.addAttr(ikCtrl, longName='Stretch_Type', attributeType='enum', enumName='Full:Stretch Only:Squash Only', keyable=True)
    cmds.addAttr(ikCtrl, longName='Stretchiness', attributeType='float', minValue=0, maxValue=1, keyable=True)

    rootObjects.append(ikCtrlOffsetGrp)

    # hock controller
    hockJoint = legJoints[len(legJoints) - 2]
    hockCtrl = curveGenerator.cube(f'{ctrlPrefix}_hock_ctrl', 6 * scaleMulti)
    setControllerColor(hockCtrl)

    hockCtrlOffsetGrp = cmds.group(hockCtrl, name=f'{hockCtrl}_offset')
    cmds.matchTransform(hockCtrlOffsetGrp, hockJoint, position=True)
    cmds.pointConstraint(ikCtrl, hockCtrlOffsetGrp, weight=1, maintainOffset=True)

    rootObjects.append(hockCtrlOffsetGrp)

    # pole vector controller
    pvCtrl = curveGenerator.pyramid(f'{ctrlPrefix}_tibia_ctrl', 4 * scaleMulti)
    cmds.setAttr(f'{pvCtrl}.rotateX', -90)
    setControllerColor(pvCtrl)

    pvCtrlOffsetGrp = cmds.group(pvCtrl, name=f'{pvCtrl}_offset')
    cmds.xform(pvCtrlOffsetGrp, centerPivots=True)
    cmds.makeIdentity(pvCtrl, apply=True, rotate=True)

    positionPoleVectorCtrl(legJoints[0:3], pvCtrlOffsetGrp)

    rootObjects.append(pvCtrlOffsetGrp)

    return rootObjects

def positionPoleVectorCtrl(joints: list[str], ctrlOffsetGrp: str):
    if len(joints) != 3:
        raise Exception("Error occured during get pole vector position")
    
    cmds.matchTransform(ctrlOffsetGrp, joints[1], position=True)

    positions = [cmds.xform(jnt, query=True, worldSpace=True, translation=True) for jnt in joints]
    tempTriangle = cmds.polyCreateFacet(p=positions, name=f'{ctrlOffsetGrp}_pv_temp_tri')[0]
    tempConstraint = cmds.normalConstraint(f'{tempTriangle}.vtx[1]', ctrlOffsetGrp)[0]

    cmds.delete(tempConstraint, tempTriangle)


def createFKIKSwitchController(legJoints: list[str], fkRootObjs: list[str], ikRootObjs: list[str], isRear: bool, scaleMulti=1):
    direction = legJoints[0][0]
    ctrlPrefix = f"{direction}_leg_{'rear' if isRear else 'front'}"

    # create controller
    fkLabel = curveGenerator.text(f'{ctrlPrefix}_fk_label', 'FK')
    ikLabel = curveGenerator.text(f'{ctrlPrefix}_ik_label', 'IK')
    utils.overrideDisplayTypeToReference(fkLabel)
    utils.overrideDisplayTypeToReference(ikLabel)
    
    labelWidth = utils.getWidthInWorld(fkLabel)
    labelHeight = utils.getHeightInWorld(fkLabel)

    switchCtrl = curveGenerator.twoDirArrow(f'{ctrlPrefix}_ctrl', labelWidth * 1.2)
    utils.setShapeColor(switchCtrl, COLOR_INDEX_SKYBLUE)
    cmds.rotate('90deg', 0, 0, switchCtrl)
    cmds.makeIdentity(switchCtrl, apply=True, rotate=True)

    switchCtrlHeight = utils.getHeightInWorld(switchCtrl)

    labelOffsetY = labelHeight / 2 + switchCtrlHeight / 2

    cmds.setAttr(f'{fkLabel}.translateY', labelOffsetY * 1.1)
    cmds.setAttr(f'{ikLabel}.translateY', labelOffsetY * 1.1)
    cmds.parent(fkLabel, ikLabel, switchCtrl)
    
    scale = 1.5 * 3 * scaleMulti
    cmds.scale(scale, scale, 1, switchCtrl)
    
    footJoint = legJoints[len(legJoints) - 1]
    cmds.matchTransform(switchCtrl, footJoint, position=True)
    cmds.move(10 * scaleMulti * (1 if direction == 'l' else -1), 10 * scaleMulti, -5 * scaleMulti, switchCtrl, relative=True)
    cmds.makeIdentity(switchCtrl, apply=True, translate=True, scale=True)

    # add attribute - FK_IK_Switch
    attrName = 'FK_IK_Switch'
    cmds.addAttr(switchCtrl, longName=attrName, attributeType='float', minValue=0, maxValue=1, keyable=True)
    for ikRootObj in ikRootObjs:
        cmds.connectAttr(f'{switchCtrl}.{attrName}', f'{ikRootObj}.visibility')
    cmds.connectAttr(f'{switchCtrl}.{attrName}', f'{ikLabel}.visibility')
    
    reverseNode = f'{ctrlPrefix}_fkik_reverse'
    cmds.shadingNode('reverse', asUtility=True, name=reverseNode)
    cmds.connectAttr(f'{switchCtrl}.{attrName}', f'{reverseNode}.inputX')
    for fkRootObj in fkRootObjs:
        cmds.connectAttr(f'{reverseNode}.outputX', f'{fkRootObj}.visibility')
    cmds.connectAttr(f'{reverseNode}.outputX', f'{fkLabel}.visibility')

    # add attribute - volume offset
    cmds.addAttr(switchCtrl, longName='Volume_Offset', attributeType='float', minValue=-0.5, maxValue=3.0, keyable=True, defaultValue=-0.5)

    return [switchCtrl]

def createRootController(scaleMulti: int) -> str:
    # base group structure
    rigGrp = cmds.group(empty=True, name='rig_grp')

    doNotTouchGrp = cmds.group(empty=True, name='DO_NOT_TOUCH')
    cmds.parent(doNotTouchGrp, rigGrp)

    geometryGrp = cmds.group(empty=True, name='geometry')
    cmds.parent(geometryGrp, doNotTouchGrp)

    animGeometryGrp = cmds.group(empty=True, name='anim_geometry')
    blendshapesGrp = cmds.group(empty=True, name='blendshapes')
    cmds.parent(animGeometryGrp, blendshapesGrp, geometryGrp)

    rigDeformersGrp = cmds.group(empty=True, name='rig_deformers')
    cmds.parent(rigDeformersGrp, doNotTouchGrp)
    rigSystemsGrp = cmds.group(empty=True, name='rig_systems')
    cmds.parent(rigSystemsGrp, doNotTouchGrp)

    visualAidsGrp = cmds.group(empty=True, name='visual_aids')
    cmds.parent(visualAidsGrp, doNotTouchGrp)

    connectionLinesGrp = cmds.group(empty=True, name='connection_lines')
    cmds.parent(connectionLinesGrp, visualAidsGrp)
    
    exportSkeletonGrp = cmds.group(empty=True, name='export_skeleton')
    cmds.parent(exportSkeletonGrp, doNotTouchGrp)

    # root controller
    rootCtrl = curveGenerator.radialArrow(ROOT_CTRL_NAME, 40 * scaleMulti)
    utils.setShapeColor(rootCtrl, COLOR_INDEX_LIGHTGREEN)

    rootCtrlGrp = cmds.group(rootCtrl, name='root_grp')

    # root controller - attributes
    utils.addSeparatorAttribute(rootCtrl, 'TWEAK')
    for attr in ['Body_Tweak', 'Front_Leg_Tweak', 'Rear_Leg_Tweak']:
        cmds.addAttr(rootCtrl, longName=attr, attributeType='enum', enumName='Hide:Show')
        cmds.setAttr(f'{rootCtrl}.{attr}', edit=True, channelBox=True)
    
    utils.addSeparatorAttribute(rootCtrl, 'VISIBILITY')
    for attr in ['Body_Controls', 'Face_Controls', 'Geometry', 'Blendshapes']:
        cmds.addAttr(rootCtrl, longName=attr, attributeType='enum', enumName='Hide:Show')
        cmds.setAttr(f'{rootCtrl}.{attr}', edit=True, channelBox=True)
    
    utils.addSeparatorAttribute(rootCtrl, 'LOCK')
    cmds.addAttr(rootCtrl, longName='Models', attributeType='enum', enumName='Unlocked:Wireframe:Locked')
    cmds.setAttr(f'{rootCtrl}.Models', edit=True, channelBox=True)

    utils.addSeparatorAttribute(rootCtrl, 'DEBUG')
    for attr in ['Rig_Systems', 'Rig_Deformers', 'Skeleton']:
        cmds.addAttr(rootCtrl, longName=attr, attributeType='enum', enumName='Hide:Show')
        cmds.setAttr(f'{rootCtrl}.{attr}', edit=True, channelBox=True)

    # root controller - attributes - connect
    cmds.connectAttr(f'{rootCtrl}.Geometry', f'{animGeometryGrp}.visibility')
    cmds.connectAttr(f'{rootCtrl}.Blendshapes', f'{blendshapesGrp}.visibility')
    cmds.connectAttr(f'{rootCtrl}.Rig_Systems', f'{rigSystemsGrp}.visibility')
    cmds.connectAttr(f'{rootCtrl}.Rig_Deformers', f'{rigDeformersGrp}.visibility')
    cmds.connectAttr(f'{rootCtrl}.Skeleton', f'{exportSkeletonGrp}.visibility')

    # scene direction curve
    sceneDirCurve = curveGenerator.arrow('scene_direction', 50 * scaleMulti, 50 * scaleMulti, 80 * scaleMulti, 90 * scaleMulti)
    utils.overrideDisplayTypeToReference(sceneDirCurve)

    # controls group
    controlsGrp = cmds.group(rootCtrlGrp, sceneDirCurve, name='controls')
    cmds.parent(controlsGrp, rigGrp)

    return rootCtrl

def createControllers(modelRelativeHorizontalAxes: str, isRear: bool, scaleMulti=1):
    legJoints = getLegJoints()

    rootGroup = ROOT_CTRL_NAME
    if not cmds.ls(rootGroup, type='transform'):
        rootGroup = createRootController(scaleMulti)

    fkRoots = createFKControllers(legJoints, modelRelativeHorizontalAxes, scaleMulti)
    ikRoots = createIKControllers(legJoints, isRear, scaleMulti)
    switchRoots = createFKIKSwitchController(legJoints, fkRoots, ikRoots, isRear, scaleMulti)

    cmds.parent(*fkRoots, *ikRoots, *switchRoots, rootGroup)

createControllers('z', False)