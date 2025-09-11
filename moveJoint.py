# Move Bind Joint

import maya.cmds as cmds

def moveBindJoint():
    selectedList = cmds.ls(selection=True)
    
    if not selectedList:
        cmds.error("오브젝트를 선택해주세요.")
        return
    
    listSize = len(selectedList)
    halfSize = listSize // 2
    
    for i in range(halfSize):
        cmds.select(selectedList[i + halfSize], replace=True)
        
        try:
            cmds.MoveSkinJointsTool()
        except:
            print("MoveSkinJointsTool을 실행할 수 없습니다.")
        
        cmds.select([selectedList[i], selectedList[i + halfSize]])
        jointOrientCopy()

def jointOrientCopy():
    selectedJoints = cmds.ls(selection=True, type='joint', long=True)
    
    if len(selectedJoints) != 2:
        cmds.error("조인트 두 개를 선택해주세요.")
        return
    
    originalRotate = cmds.xform(selectedJoints[0], query=True, worldSpace=True, rotation=True)
    originalPosition = cmds.xform(selectedJoints[0], query=True, worldSpace=True, rotatePivot=True)
    
    childJoints = cmds.listRelatives(selectedJoints[1], fullPath=True, type='joint')
    
    childPositions = []
    childRotates = []
    
    if childJoints:
        for child in childJoints:
            childPos = cmds.xform(child, query=True, worldSpace=True, rotatePivot=True)
            childRot = cmds.xform(child, query=True, worldSpace=True, rotation=True)
            childPositions.append(childPos)
            childRotates.append(childRot)
    
    cmds.setAttr(f"{selectedJoints[1]}.jointOrient", 0, 0, 0)
    
    cmds.xform(selectedJoints[1], worldSpace=True, translation=originalPosition)
    cmds.xform(selectedJoints[1], worldSpace=True, rotation=originalRotate)
    
    currentRotate = cmds.getAttr(f"{selectedJoints[1]}.rotate")[0]
    cmds.setAttr(f"{selectedJoints[1]}.rotate", 0, 0, 0)
    cmds.setAttr(f"{selectedJoints[1]}.jointOrient", *currentRotate)
    
    if childJoints:
        for i, child in enumerate(childJoints):
            cmds.xform(child, worldSpace=True, translation=childPositions[i])
            cmds.xform(child, worldSpace=True, rotation=childRotates[i])

moveBindJoint()