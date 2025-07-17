#-----------------------------------------
# Suyeon Auto Limb Tool v1
#-----------------------------------------

import maya.cmds as cmds

def autoLimbTool(isRearLeg: bool):
    limbJoints = 4
    
    if isRearLeg:
        limbType = 'rear'
        print('Working on the REAR leg')
    else:
        limbType = 'front'
        print('Working on the FRONT leg')

    selectionCheck = cmds.ls(selection=True, type='joint')

    if not selectionCheck:
        cmds.error('Please select the root joint.')
    else:
        jointRoot = cmds.ls(selection=True, type='joint')[0]

    whichSide = jointRoot[0:2]
    
    if not 'l_' in whichSide:
        if not 'r_' in whichSide:
            cmds.error('Please use a joint with a usable prefix of either l_ or r_')

    limbName = whichSide + 'leg_' + limbType
    
    mainControl = limbName + '_ctrl'
    pawControlName = limbName + '_ik_ctrl'
    kneeControlName = limbName + '_tibia_ctrl'
    hockControlName = limbName + '_hock_ctrl'
    rootControl = limbName + '_root_ctrl'

    #-------------------------------------
    # Build the list of joints we are working with, using the root as a start point
    #-------------------------------------

    jointHierarchy = cmds.listRelatives(jointRoot, allDescendents=True, type='joint')
    jointHierarchy.append(jointRoot)
    jointHierarchy.reverse()

    cmds.select(clear=True)

    #-------------------------------------
    # Duplicate the main joint chain and rename each joint
    #-------------------------------------
    newJointList=["_ik", "_fk", "_stretch"]

    if isRearLeg:
        newJointList.append('_driver')

    for newJoint in newJointList:
        for i in range(limbJoints):
            newJointName = jointHierarchy[i] + newJoint
            cmds.joint(name=newJointName)
            cmds.matchTransform(newJointName, jointHierarchy[i])
            cmds.makeIdentity(newJointName, apply=True, rotate=True)

        cmds.select(clear=True)

    #-------------------------------------
    # Constrain the main joints to the ik and fk joints so we can blend between them
    #-------------------------------------
    for i in range(limbJoints):
        cmds.parentConstraint(jointHierarchy[i] +  "_fk", jointHierarchy[i] +  "_ik", jointHierarchy[i], weight=1, maintainOffset=False)
    
    #-------------------------------------
    # setup fk
    #-------------------------------------
    for i in range(limbJoints):
        cmds.parentConstraint(jointHierarchy[i] +  "_fk_ctrl", jointHierarchy[i] +  "_fk", weight=1, maintainOffset=False)

    #-------------------------------------
    # setup ik
    #-------------------------------------
    if isRearLeg:
        cmds.ikHandle(name=limbName + '_driver_ikHandle', solver='ikRPsolver', startJoint=jointHierarchy[0] + "_driver", endEffector=jointHierarchy[3] + "_driver")

    cmds.ikHandle(name=limbName + '_knee_ikHandle', solver='ikRPsolver', startJoint=jointHierarchy[0] + "_ik", endEffector=jointHierarchy[2] + "_ik")
    cmds.ikHandle(name=limbName + '_hock_ikHandle', solver='ikSCsolver', startJoint=jointHierarchy[2] + "_ik", endEffector=jointHierarchy[3] + "_ik")

    cmds.group(limbName + '_knee_ikHandle', name=limbName + '_knee_ctrl')
    cmds.group(limbName + '_knee_ctrl', name=limbName + '_knee_ctrl_offset')

    cmds.matchTransform(limbName + '_knee_ctrl', limbName + '_knee_ctrl_offset', jointHierarchy[3], pivots=True)

    cmds.parent(limbName + '_hock_ikHandle', pawControlName)

    if isRearLeg:
        cmds.parent(limbName + '_knee_ctrl_offset', jointHierarchy[2] + "_driver")
        cmds.parent(limbName + '_hock_ikHandle', jointHierarchy[3] + "_driver")
        cmds.parent(limbName + '_driver_ikHandle', pawControlName)
    else:
        cmds.parent(limbName + '_knee_ctrl_offset', 'root_ctrl')
        cmds.pointConstraint(pawControlName, limbName + '_knee_ctrl_offset', weight=1)

    cmds.orientConstraint(pawControlName, jointHierarchy[3] + '_ik', weight=1, maintainOffset=True)

    # pv
    if isRearLeg:
        cmds.poleVectorConstraint(kneeControlName, limbName + '_driver_ikHandle', weight=1)
    else:
        cmds.poleVectorConstraint(kneeControlName, limbName + '_knee_ikHandle', weight=1)

    #-------------------------------------
    # add hock control
    #-------------------------------------
    cmds.shadingNode('multiplyDivide', asUtility=True, name=limbName + '_hock_multi')

    cmds.connectAttr(hockControlName + '.translate', limbName + '_hock_multi.input1', force=True)
    cmds.connectAttr(limbName + '_hock_multi.outputZ', limbName + '_knee_ctrl.rotateX', force=True)
    cmds.connectAttr(limbName + '_hock_multi.outputX', limbName + '_knee_ctrl.rotateZ', force=True)

    multiValue = 4 if isRearLeg else 5

    cmds.setAttr(limbName + '_hock_multi.input2Z', multiValue)
    cmds.setAttr(limbName + '_hock_multi.input2X', -multiValue)

    #-------------------------------------
    # ik fk blending
    #-------------------------------------
    for i in range(limbJoints):
        getConstraint = cmds.listConnections(jointHierarchy[i], type='parentConstraint')[0]
        getWeights = cmds.parentConstraint(getConstraint, query=True, weightAliasList=True)

        cmds.connectAttr(mainControl + '.FK_IK_Switch', getConstraint + '.' + getWeights[1], force=True)
        cmds.connectAttr(limbName + '_fkik_reverse.outputX', getConstraint + '.' + getWeights[0], force=True)

    #-------------------------------------
    # organize the hierarchy
    #-------------------------------------
    cmds.group(empty=True, name=limbName + "_grp")
    cmds.matchTransform(limbName + "_grp", jointRoot)
    cmds.makeIdentity(limbName + "_grp", apply=True, translate=True, rotate=True)
    cmds.parent(jointRoot + '_ik', jointRoot + '_fk', jointRoot + '_stretch', limbName + '_grp')

    if isRearLeg:
        cmds.parent(jointRoot + '_driver', limbName + '_grp')
    
    cmds.parentConstraint(rootControl, limbName + '_grp', weight=1, maintainOffset=True)

    cmds.parent(limbName + '_grp', 'rig_systems')
    cmds.select(clear=True)

    #-------------------------------------
    # make stertch
    #-------------------------------------
    stretchEndPosLoc = cmds.spaceLocator(name=limbName + '_stertchEndPos_loc')[0]
    cmds.matchTransform(stretchEndPosLoc, jointHierarchy[3])
    cmds.parent(stretchEndPosLoc, pawControlName)
    
    # 다리 관절들 사이 길이들 합
    limbLengthPMANode = cmds.shadingNode('plusMinusAverage', asUtility=True, name=limbName + '_length')
    for i in range(limbJoints - 1):
        distanceNode = cmds.shadingNode('distanceBetween', asUtility=True, name=jointHierarchy[i] + '_distnode')
        cmds.connectAttr(jointHierarchy[i] + '_stretch.worldMatrix', distanceNode + '.inMatrix1', force=True)
        cmds.connectAttr(jointHierarchy[i+1] + '_stretch.worldMatrix', distanceNode + '.inMatrix2', force=True)
        cmds.connectAttr(jointHierarchy[i] + '_stretch.rotatePivotTranslate', distanceNode + '.point1', force=True)
        cmds.connectAttr(jointHierarchy[i+1] + '_stretch.rotatePivotTranslate', distanceNode + '.point2', force=True)
        cmds.connectAttr(distanceNode + '.distance', limbLengthPMANode + f'.input1D[{i}]', force=True)

    # 첫 번째 관절과 발목 사이의 거리
    distanceNode = cmds.shadingNode('distanceBetween', asUtility=True, name=limbName + '_stretch_distnode')
    cmds.connectAttr(jointHierarchy[0] + '_stretch.worldMatrix', distanceNode + '.inMatrix1', force=True)
    cmds.connectAttr(stretchEndPosLoc + '.worldMatrix', distanceNode + '.inMatrix2', force=True)
    cmds.connectAttr(jointHierarchy[0] + '_stretch.rotatePivotTranslate', distanceNode + '.point1', force=True)
    cmds.connectAttr(stretchEndPosLoc + '.rotatePivotTranslate', distanceNode + '.point2', force=True)

    scaleFactorCalcNode = cmds.shadingNode('multiplyDivide', asUtility=True, name=limbName + '_scaleFactor')
    stretchConditionNode = cmds.shadingNode('condition', asUtility=True, name=limbName + '_stretchCondition')

    cmds.setAttr(scaleFactorCalcNode + '.operation', 2) # divide

    # 스트레치 여부 확인
    cmds.setAttr(stretchConditionNode + '.operation', 2) # greater than
    cmds.setAttr(stretchConditionNode + '.secondTerm', 1)
    cmds.connectAttr(distanceNode + '.distance', scaleFactorCalcNode + '.input1X', force=True)
    cmds.connectAttr(limbLengthPMANode + '.output1D', scaleFactorCalcNode + '.input2X', force=True)

    cmds.connectAttr(scaleFactorCalcNode + '.outputX', stretchConditionNode + '.firstTerm', force=True)
    cmds.connectAttr(scaleFactorCalcNode + '.outputX', stretchConditionNode + '.colorIfTrueR', force=True)

    for i in range(limbJoints):
        cmds.connectAttr(stretchConditionNode + '.outColorR', jointHierarchy[i] + '_ik.scaleX', force=True)

        if isRearLeg:
            cmds.connectAttr(stretchConditionNode + '.outColorR', jointHierarchy[i] + '_driver.scaleX', force=True)

    # Stretchness 어트리뷰트 반영
    stretchnessBlendingNode = cmds.shadingNode('blendColors', asUtility=True, name=limbName + '_blendStretchness')
    cmds.setAttr(stretchnessBlendingNode + '.color2', 1, 0, 0, type='double3')
    cmds.connectAttr(scaleFactorCalcNode + '.outputX', stretchnessBlendingNode + '.color1R', force=True)
    cmds.connectAttr(stretchnessBlendingNode + '.outputR', stretchConditionNode + '.colorIfTrueR', force=True)
    cmds.connectAttr(pawControlName + '.Stretchiness', stretchnessBlendingNode + '.blender', force=True)

    # Stretch_Type 어트리뷰트 반영 - 키프레임 활용
    cmds.setAttr(pawControlName + '.Stretch_Type', 0)
    cmds.setAttr(stretchConditionNode + '.operation', 1) # not equal
    cmds.setDrivenKeyframe(stretchConditionNode + '.operation', currentDriver=pawControlName + '.Stretch_Type')

    cmds.setAttr(pawControlName + '.Stretch_Type', 1)
    cmds.setAttr(stretchConditionNode + '.operation', 3) # greater than
    cmds.setDrivenKeyframe(stretchConditionNode + '.operation', currentDriver=pawControlName + '.Stretch_Type')

    cmds.setAttr(pawControlName + '.Stretch_Type', 2)
    cmds.setAttr(stretchConditionNode + '.operation', 5) # less or equal
    cmds.setDrivenKeyframe(stretchConditionNode + '.operation', currentDriver=pawControlName + '.Stretch_Type')

    cmds.setAttr(pawControlName + '.Stretch_Type', 0)

    #-------------------------------------
    cmds.select(clear=True)

    #-------------------------------------
    # volume preservation
    #-------------------------------------
    volumeCalcNode = cmds.shadingNode('multiplyDivide', asUtility=True, name=limbName + '_volume')
    cmds.setAttr(volumeCalcNode + '.operation', 3)
    cmds.connectAttr(stretchnessBlendingNode + '.outputR', volumeCalcNode + '.input1X', force=True)
    cmds.connectAttr(volumeCalcNode + '.outputX', stretchConditionNode + '.colorIfTrueG', force=True)

    # TODO: 추후 리본 시스템에 맞게 변경 필요
    cmds.connectAttr(stretchConditionNode + '.outColorG', jointHierarchy[1] + '.scaleY', force=True)
    cmds.connectAttr(stretchConditionNode + '.outColorG', jointHierarchy[1] + '.scaleZ', force=True)
    cmds.connectAttr(stretchConditionNode + '.outColorG', jointHierarchy[2] + '.scaleY', force=True)
    cmds.connectAttr(stretchConditionNode + '.outColorG', jointHierarchy[2] + '.scaleZ', force=True)

    cmds.connectAttr(mainControl + '.Volume_Offset', volumeCalcNode + '.input2X', force=True)

    #-------------------------------------
    # make roll joints & systems
    #-------------------------------------
    if whichSide == 'l_':
        flipSide = 1
    else:
        flipSide = -1

    # femur 롤 조인트 생성
    rollJointList = [jointHierarchy[0], jointHierarchy[3], jointHierarchy[0], jointHierarchy[0]]
    for i in range(len(rollJointList)): 
        rollJointName = rollJointList[i]

        if i == 3:
            rollJointName += '_follow_tip'
        elif i == 2:
            rollJointName += '_follow'
        else:
            rollJointName += '_roll'

        cmds.joint(name=rollJointName, radius=2)
        cmds.matchTransform(rollJointName, rollJointList[i])
        cmds.makeIdentity(rollJointName, apply=True, rotate=True)
        # cmds.toggle(rollJointName, localAxis=True)

        if i < 2:
            cmds.parent(rollJointName, rollJointList[i])
        
        if i != 2:
            cmds.select(clear=True)

    # femur 롤 시스템 생성
    tempConstraint = cmds.pointConstraint(jointHierarchy[0], jointHierarchy[1], rollJointList[2] + '_follow_tip', weight=1, maintainOffset=False)[0]
    cmds.delete(tempConstraint)
    cmds.move(0, 0, -5 * flipSide, rollJointList[2] + '_follow', relative=True, objectSpace=True, worldSpaceDistance=True)

    rollAimLocator = cmds.spaceLocator(name=rollJointList[0] + '_roll_aim')[0]
    cmds.matchTransform(rollAimLocator, rollJointList[2] + '_follow')
    cmds.parent(rollAimLocator, rollJointList[2] + '_follow')
    cmds.move(0, 0, -5 * flipSide, rollAimLocator, relative=True, objectSpace=True, worldSpaceDistance=True)

    cmds.aimConstraint(jointHierarchy[1], rollJointList[0] + '_roll', weight=True, aimVector=(1, 0, 0), upVector=(0, 0, -1), worldUpType='object', worldUpObject=rollAimLocator, maintainOffset=True)

    followIkHandle = cmds.ikHandle(name=limbName + '_follow_ikHandle', solver="ikRPsolver", startJoint=rollJointList[2] + '_follow', endEffector=rollJointList[2] + '_follow_tip')[0]
    print(followIkHandle)
    cmds.parent(followIkHandle, jointHierarchy[1])
    cmds.matchTransform(followIkHandle, jointHierarchy[1])

    cmds.setAttr(followIkHandle + '.poleVectorX', 0)
    cmds.setAttr(followIkHandle + '.poleVectorY', 0)
    cmds.setAttr(followIkHandle + '.poleVectorZ', 0)

    # metacarpus 롤 시스템 생성
    rollAimLocator = cmds.spaceLocator(name=rollJointList[1] + '_roll_aim')[0]
    cmds.matchTransform(rollAimLocator, rollJointList[1] + '_roll')
    cmds.parent(rollAimLocator, jointHierarchy[3])
    cmds.move(5 * flipSide, 0, 0, rollAimLocator, relative=True, objectSpace=True, worldSpaceDistance=True)

    cmds.aimConstraint(jointHierarchy[2], rollJointList[1] + '_roll', weight=True, aimVector=(0, 1, 0), upVector=(1, 0, 0), worldUpType='object', worldUpObject=rollAimLocator, maintainOffset=True)

    # hierarchy
    cmds.parent(rollJointList[0] + '_follow', limbName + '_grp')

    cmds.select(clear=True)

autoLimbTool(False)

