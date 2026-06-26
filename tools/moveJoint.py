# Move Bind Joint

import maya.cmds as cmds

def moveBindJoint():
    cmds.currentTime(0)

    selectedList = cmds.ls(selection=True)
    
    if not selectedList:
        cmds.error("Please select an object.")
        return
    
    listSize = len(selectedList)
    halfSize = listSize // 2

    #################### 키프레임 존재 확인
    keyframeSel = []

    for i in range(halfSize):
        keyframes = cmds.keyframe(selectedList[i + halfSize], query=True)
        if keyframes is not None and len(keyframes) > 0:
            keyframeSel.append(selectedList[i + halfSize])

    if len(keyframeSel) > 0:
        cmds.confirmDialog(title='Move Joint', 
                           message=f"Keyframes exist on the following joints.\n\n{', '.join(keyframeSel)}", 
                           button='OK', 
                           icon='warning')
        return
        # result = cmds.confirmDialog(title='Move Joint', message='Delete keyframes?', button=['OK', 'Cancel'], defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel')

        # if result == 'OK':
        #     for keyframeObj in keyframeSel:
        #         cmds.cutKey(keyframeObj, clear=True, time=(None, None))
        # else:
        #     return
    ####################
    
    for i in range(halfSize):
        cmds.select(selectedList[i + halfSize], replace=True)
        
        try:
            cmds.MoveSkinJointsTool()
        except:
            print("Cannot execute MoveSkinJointsTool.")
        
        cmds.select([selectedList[i], selectedList[i + halfSize]])
        jointOrientCopy()

def jointOrientCopy():
    selectedJoints = cmds.ls(selection=True, type='joint', long=True)
    
    if len(selectedJoints) != 2:
        cmds.error("Please select two joints.")
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