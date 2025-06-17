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
    rootObject = None

    for i, joint in enumerate(legJoints):
        ctrl = curveGenerator.circle(f'{joint}_fk_ctrl', 6 * scaleMulti)
        setControllerColor(ctrl)

        if i != len(legJoints) - 1:
            cmds.setAttr(f'{ctrl}.rotate{modelRelativeHorizontalAxes.capitalize()}', 90)
            cmds.makeIdentity(ctrl, rotate=True, apply=True)
        
        offsetGrp = f'{ctrl}_offset'
        cmds.group(ctrl, name=offsetGrp)
        cmds.matchTransform(offsetGrp, joint, position=True, rotation=True)

        if i > 0:
            cmds.parent(offsetGrp, f'{legJoints[i - 1]}_fk_ctrl')
        else:
            rootObject = offsetGrp
    
    return rootObject

def createIKControllers(legJoints: list[str], isRear: bool, scaleMulti=1):
    direction = legJoints[0][0]
    ctrlPrefix = f"{direction}_leg_{'rear' if isRear else 'front'}"

    # leg IK controller
    footJoint = legJoints[len(legJoints) - 1]
    ikCtrl = f'{ctrlPrefix}_ik_ctrl'

    ikCtrlOffsetGrp = f'{ikCtrl}_offset'
    cmds.group(empty=True, name=ikCtrlOffsetGrp)
    cmds.matchTransform(ikCtrlOffsetGrp, footJoint, position=True, rotation=True)
 
    curveGenerator.circle(ikCtrl, 6 * scaleMulti)
    setControllerColor(ikCtrl)
    cmds.matchTransform(ikCtrl, footJoint, position=True)
    cmds.setAttr(f'{ikCtrl}.translateY', 0)

    cmds.parent(ikCtrl, ikCtrlOffsetGrp)
    cmds.makeIdentity(ikCtrl, apply=True, translate=True, rotate=True, scale=True, preserveNormals=True, normal=False)
    cmds.matchTransform(ikCtrl, ikCtrlOffsetGrp, pivots=True)

    # leg Ik Controller - attributes
    cmds.addAttr(ikCtrl, longName='Stretch_Type', attributeType='enum', enumName='Full:Stretch Only:Squash Only', keyable=True)
    cmds.addAttr(ikCtrl, longName='Stretchiness', attributeType='float', minValue=0, maxValue=1, keyable=True)

    # hock controller
    hockJoint = legJoints[len(legJoints) - 2]
    hockCtrl = f'{ctrlPrefix}_hock_ctrl'

    curveGenerator.cube(hockCtrl, 6 * scaleMulti)
    setControllerColor(hockCtrl)

    hockCtrlOffsetGrp = f'{hockCtrl}_offset'
    cmds.group(hockCtrl, name=hockCtrlOffsetGrp)
    cmds.matchTransform(hockCtrlOffsetGrp, hockJoint, position=True)

    cmds.parent(hockCtrlOffsetGrp, ikCtrl)

    # pole vector controller
    pvCtrl = f'{ctrlPrefix}_tibia_ctrl'
    curveGenerator.pyramid(pvCtrl, 4 * scaleMulti)
    cmds.setAttr(f'{pvCtrl}.rotateX', -90)
    setControllerColor(pvCtrl)

    pvCtrlOffsetGrp = f'{pvCtrl}_offset'
    cmds.group(pvCtrl, name=pvCtrlOffsetGrp)
    cmds.xform(pvCtrlOffsetGrp, centerPivots=True)
    cmds.makeIdentity(pvCtrl, apply=True, rotate=True)

    positionPoleVectorCtrl(legJoints[0:3], pvCtrlOffsetGrp)

    cmds.parent(pvCtrlOffsetGrp, ikCtrl)

    return ikCtrlOffsetGrp

def positionPoleVectorCtrl(joints: list[str], ctrlOffsetGrp: str):
    if len(joints) != 3:
        raise Exception("Error occured during get pole vector position")
    
    cmds.matchTransform(ctrlOffsetGrp, joints[1], position=True)

    positions = [cmds.xform(jnt, query=True, worldSpace=True, translation=True) for jnt in joints]
    tempTriangle = cmds.polyCreateFacet(p=positions, name=f'{ctrlOffsetGrp}_pv_temp_tri')[0]
    tempConstraint = cmds.normalConstraint(f'{tempTriangle}.vtx[1]', ctrlOffsetGrp)[0]

    cmds.delete(tempConstraint, tempTriangle)


def createFKIKSwitchController(legJoints: list[str], fkRootObj: str, ikRootObj: str, isRear: bool, scaleMulti=1):
    direction = legJoints[0][0]
    ctrlPrefix = f"{direction}_leg_{'rear' if isRear else 'front'}"

    # create controller
    fkLabel = curveGenerator.text(f'{ctrlPrefix}_fk_label', 'FK')
    ikLabel = curveGenerator.text(f'{ctrlPrefix}_ik_label', 'IK')
    utils.overrideDisplayTypeToReference(fkLabel)
    utils.overrideDisplayTypeToReference(ikLabel)
    
    labelWidth = utils.getWidthInWorld(fkLabel)
    labelHeight = utils.getHeightInWorld(fkLabel)

    switchCtrl = curveGenerator.twoDirArrow(f'{ctrlPrefix}_ctrl', labelWidth * 1.2, True)
    utils.setShapeColor(switchCtrl, COLOR_INDEX_SKYBLUE)

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

    # add attribute - FK_IK_Switch
    attrName = 'FK_IK_Switch'
    cmds.addAttr(switchCtrl, longName=attrName, attributeType='float', minValue=0, maxValue=1, keyable=True)
    cmds.connectAttr(f'{switchCtrl}.{attrName}', f'{ikRootObj}.visibility')
    cmds.connectAttr(f'{switchCtrl}.{attrName}', f'{ikLabel}.visibility')
    
    reverseNode = f'{ctrlPrefix}_fkik_reverse'
    cmds.shadingNode('reverse', asUtility=True, name=reverseNode)
    cmds.connectAttr(f'{switchCtrl}.{attrName}', f'{reverseNode}.inputX')
    cmds.connectAttr(f'{reverseNode}.outputX', f'{fkRootObj}.visibility')
    cmds.connectAttr(f'{reverseNode}.outputX', f'{fkLabel}.visibility')

    # add attribute - volume offset
    cmds.addAttr(switchCtrl, longName='Volume_Offset', attributeType='float', minValue=-0.5, maxValue=3.0, keyable=True, defaultValue=0.5)

    return switchCtrl

def createControllers(modelRelativeHorizontalAxes: str, isRear: bool, scaleMulti=1):
    legJoints = getLegJoints()
    fkRoot = createFKControllers(legJoints, modelRelativeHorizontalAxes, scaleMulti)
    ikRoot = createIKControllers(legJoints, isRear, scaleMulti)
    switchRoot = createFKIKSwitchController(legJoints, fkRoot, ikRoot, isRear, scaleMulti)

createControllers('z', False)