import maya.cmds as cmds
import maya.api.OpenMaya as om

#------------------------------------------------------------------
# UI
#------------------------------------------------------------------

GROUP_SPACING = 1

def openSuyeonToolkit():
    win = 'sy_Toolkit'

    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, title='Suyeon Toolkit', resizeToFitChildren=True)

    cmds.columnLayout(adjustableColumn=True, margins=10, rowSpacing=10)

    ################# open/close port

    # 구분선
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(60, 100), columnAttach=[(1, 'both', 0), (2, 'both', 0)])
    cmds.text(label='Port Config', align='left', font='boldLabelFont')
    cmds.separator(style='in')
    cmds.setParent('..')

    # 폼
    formLayout = cmds.formLayout(numberOfDivisions=100, margins=10)

    portLabel = cmds.text(label='Port', align='left', height=20)
    portField = cmds.intField('portInput', value=7001, height=20)

    langLabel = cmds.text(label='Language', align='left', height=20)
    langMenu = cmds.optionMenu('language', height=20)
    cmds.menuItem(label='MEL')
    cmds.menuItem(label='Python')

    openBtn = cmds.button(label="Open", command=lambda *_: openPort(portField, langMenu))
    closeBtn = cmds.button(label="Close", command=lambda *_: closePort(portField))

    cmds.formLayout(formLayout, edit=True,
                    attachForm=[(portLabel, 'top', 0), 
                                (portLabel, 'left', 0)],
                    attachControl=[(portField, 'left', 10, portLabel), 
                                   (langMenu, 'left', 10, langLabel),
                                   (openBtn, 'top', 10, portLabel),
                                   (closeBtn, 'top', 10, portLabel)],
                    attachPosition=[(portField, 'right', 10, 50),
                                    (langLabel, 'left', 0, 50),
                                    (langMenu, 'right', 0, 100),
                                    (closeBtn, 'left', 0, 0), (closeBtn, 'right', 2, 50), 
                                    (openBtn, 'left', 2, 50), (openBtn, 'right', 0, 100)])
    

    cmds.setParent('..')

    cmds.separator(style='none', height=GROUP_SPACING)

    # ################# attribute lock/unlock
    
    # 구분선
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(120, 100), columnAttach=[(1, 'both', 0), (2, 'both', 0)])
    cmds.text(label='Lock/Unlock Attributes', align='left', font='boldLabelFont')
    cmds.separator(style='in')
    cmds.setParent('..')

    # 폼
    formLayout = cmds.formLayout(numberOfDivisions=100)

    checkboxGrp = cmds.checkBoxGrp(numberOfCheckBoxes=4, columnWidth4=[75, 60, 50, 60], labelArray4=['Transform', 'Rotate', 'Scale', 'Visibility'])

    lockAttrBtn = cmds.button(label="Lock", command=lambda *_: toggleAttributeLock(True, checkboxGrp))
    unlockAttrBtn = cmds.button(label="Unlock", command=lambda *_: toggleAttributeLock(False, checkboxGrp))

    cmds.formLayout(formLayout, edit=True, 
                    attachControl=[(lockAttrBtn, 'top', 10, checkboxGrp), 
                                   (unlockAttrBtn, 'top', 10, checkboxGrp)],
                    attachPosition=[(lockAttrBtn, 'left', 0, 0), (lockAttrBtn, 'right', 2, 50), 
                                    (unlockAttrBtn, 'left', 2, 50), (unlockAttrBtn, 'right', 0, 100)])
    cmds.setParent('..')

    cmds.separator(style='none', height=GROUP_SPACING)

    # ################# paint skin weights - reset rotation, remove keyframe
    
    # 구분선
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(100, 100), columnAttach=[(1, 'both', 0), (2, 'both', 0)])
    cmds.text(label='Paint Skin Weights', align='left', font='boldLabelFont')
    cmds.separator(style='in')
    cmds.setParent('..')

    # 버튼 - 회전값 초기화
    cmds.button(label="Reset Rotation", command=lambda *_: resetRotationValue())

    # 버튼 - 키프레임 제거
    formLayout = cmds.formLayout(numberOfDivisions=100)

    btnLabel = cmds.text(label="Remove keyframe", align="left", height=22)
    removeCurrKeyframeBtn = cmds.button(label="Current", command=lambda *_: removeKeyframes(False))
    removeKeyframesBtn = cmds.button(label="All", command=lambda *_: removeKeyframes(True))

    cmds.formLayout(formLayout, edit=True,
                    attachPosition=[(btnLabel, 'left', 0, 0), (btnLabel, 'right', 2, 33),
                                    (removeKeyframesBtn, 'left', 0, 33), (removeKeyframesBtn, 'right', 2, 66), 
                                    (removeCurrKeyframeBtn, 'left', 2, 66), (removeCurrKeyframeBtn, 'right', 0, 100)])

    cmds.setParent('..')

    cmds.separator(style='none', height=GROUP_SPACING)

    # ################# joint influence lock/unlock
    
    # 구분선
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(150, 100), columnAttach=[(1, 'both', 0), (2, 'both', 0)])
    cmds.text(label='Lock/Unlock Joints Influence', align='left', font='boldLabelFont')
    cmds.separator(style='in')
    cmds.setParent('..')

    # 버튼
    formLayout = cmds.formLayout(numberOfDivisions=100)
    
    lockBtn = cmds.button(label="Lock", command=lambda *_: toggleJointsInfluenceLock(True))
    unlockBtn = cmds.button(label="Unlock", command=lambda *_: toggleJointsInfluenceLock(False))

    cmds.formLayout(formLayout, edit=True,
                    attachPosition=[(lockBtn, 'left', 0, 0), (lockBtn, 'right', 2, 50), 
                                    (unlockBtn, 'left', 2, 50), (unlockBtn, 'right', 0, 100)])

    cmds.setParent('..')

    cmds.showWindow(win)

#------------------------------------------------------------------
# Button Actions
#------------------------------------------------------------------

def openPort(portField, languageMenu):
    port = cmds.intField(portField, query=True, value=True)
    language = cmds.optionMenu(languageMenu, query=True, value=True)

    if not port or not language:
        cmds.error("Please input a valid value")
        return

    try:
        cmds.commandPort(name=f"localhost:{port}", sourceType=language.lower(), echoOutput=True)
        om.MGlobal.displayInfo(f"Port {port} opened with {language} support")

    except Exception as e:
        cmds.error(f"Error opening port: {e}")

def closePort(portField):
    port = cmds.intField(portField, query=True, value=True)

    if not port:
        cmds.error("Please input a valid value")
        return

    try:
        cmds.commandPort(name=f"localhost:{port}", close=True)
        om.MGlobal.displayInfo(f"Port {port} closed")

    except Exception as e:
        cmds.error(f"Error closing port: {e}")

def toggleAttributeLock(lock, checkboxGrp):
    checkValues = cmds.checkBoxGrp(checkboxGrp, query=True, valueArray4=True)

    locked = lock
    keyable = not lock

    selections = cmds.ls(selection=True,transforms=True, allPaths=True)

    for sel in selections:
        if checkValues[0]:
            cmds.setAttr((sel + ".tx"), k=keyable, l=locked)
            cmds.setAttr((sel + ".ty"), k=keyable, l=locked)
            cmds.setAttr((sel + ".tz"), k=keyable, l=locked)

        if checkValues[1]:
            cmds.setAttr((sel + ".rx"), k=keyable, l=locked)
            cmds.setAttr((sel + ".ry"), k=keyable, l=locked)
            cmds.setAttr((sel + ".rz"), k=keyable, l=locked)
            
        if checkValues[2]:
            cmds.setAttr((sel + ".sx"), k=keyable, l=locked)
            cmds.setAttr((sel + ".sy"), k=keyable, l=locked)
            cmds.setAttr((sel + ".sz"), k=keyable, l=locked)
            
        if checkValues[3]:                                    
            cmds.setAttr((sel + ".v"), k=keyable, l=locked)
    

def toggleJointsInfluenceLock(lock):
    for joint in cmds.ls(type='joint'):
        if cmds.attributeQuery('liw', node=joint, exists=True):
            cmds.setAttr(joint + ".liw", lock)

    om.MGlobal.displayInfo(f"All joint influences have been {'locked' if lock else 'unlocked'}.")

def resetRotationValue():
    for sel in cmds.ls(selection=True):
        cmds.setAttr(f"{sel}.rx", 0)
        cmds.setAttr(f"{sel}.ry", 0)
        cmds.setAttr(f"{sel}.rz", 0)

def removeKeyframes(all):
    currentTime = cmds.currentTime(query=True)
    time = (None, None) if all else (currentTime, currentTime)

    for sel in cmds.ls(selection=True):
        cmds.cutKey(sel, clear=True, time=time)


openSuyeonToolkit()