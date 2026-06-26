import maya.cmds as cmds
import maya.api.OpenMaya as om

#------------------------------------------------------------------
# UI
#------------------------------------------------------------------
def createUI():
    formLayout = cmds.formLayout()
    tabLayout = cmds.tabLayout(innerMarginHeight=5, innerMarginWidth=5)
    
    cmds.formLayout(formLayout, edit=True, attachForm=((tabLayout, 'top', 0), (tabLayout, 'left', 0), (tabLayout, 'bottom', 0), (tabLayout, 'right', 0)) )

    skinTab = createSkinTab()
    rigTab = createRigTab()
    miscTab = createMiscTab()

    cmds.tabLayout(tabLayout, edit=True, tabLabel=((skinTab, 'Skin'), (miscTab, 'Misc'), (rigTab, 'Rig')))

def openSuyeonToolkit():
    win = 'sy_Toolkit'

    if cmds.window(win, exists=True):
        cmds.deleteUI(win)

    cmds.window(win, title='Suyeon Toolkit', resizeToFitChildren=True)
    createUI()
    cmds.showWindow(win)

def createMiscTab():
    layout = cmds.columnLayout(adjustableColumn=True, margins=10, rowSpacing=10)

    cmds.text(label='Command Port Config', align='left', font='boldLabelFont')

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
                                    (closeBtn, 'left', 0, 0), (closeBtn, 'right', 5, 50), 
                                    (openBtn, 'left', 5, 50), (openBtn, 'right', 0, 100)])
    

    cmds.setParent('..')
    cmds.setParent('..')

    return layout

def createRigTab():
    layout = cmds.columnLayout(adjustableColumn=True, margins=10, rowSpacing=10)

    # 채널 창 숨김/표시
    cmds.text(label='Lock/Unlock Attributes', align='left', font='boldLabelFont')

    formLayout = cmds.formLayout(numberOfDivisions=100)

    checkboxGrp = cmds.checkBoxGrp(numberOfCheckBoxes=4, columnWidth4=[75, 60, 50, 60], labelArray4=['Transform', 'Rotate', 'Scale', 'Visibility'])

    lockAttrBtn = cmds.button(label="Lock", command=lambda *_: toggleAttributeLock(True, checkboxGrp))
    unlockAttrBtn = cmds.button(label="Unlock", command=lambda *_: toggleAttributeLock(False, checkboxGrp))

    cmds.formLayout(formLayout, edit=True, 
                    attachControl=[(lockAttrBtn, 'top', 10, checkboxGrp), 
                                   (unlockAttrBtn, 'top', 10, checkboxGrp)],
                    attachPosition=[(lockAttrBtn, 'left', 0, 0), (lockAttrBtn, 'right', 5, 50), 
                                    (unlockAttrBtn, 'left', 5, 50), (unlockAttrBtn, 'right', 0, 100)])
    
    cmds.setParent('..')

    cmds.separator(style='in')

    # 선택된 오브젝트의 Local Rotation Axis 가시성 설정
    formLayout = cmds.formLayout(numberOfDivisions=100)

    btnLabel = cmds.text(label="Local Rotation Axis", font="boldLabelFont", align="left", height=22)
    showLRABtn = cmds.button(label="Show", command=lambda *_: setLocalRotationAxisVisibility(True))
    hideLRABtn = cmds.button(label="Hide", command=lambda *_: setLocalRotationAxisVisibility(False))

    cmds.formLayout(formLayout, edit=True,
                    attachPosition=[(btnLabel, 'left', 0, 0), (btnLabel, 'right', 5, 40),
                                    (showLRABtn, 'left', 0, 40), (showLRABtn, 'right', 5, 70), 
                                    (hideLRABtn, 'left', 5, 70), (hideLRABtn, 'right', 0, 100)])

    cmds.setParent('..')

    cmds.separator(style='in')

    formLayout = cmds.formLayout(numberOfDivisions=100)

    # 특정 타입의 자식 노드만 선택
    # IDEA: 현재 선택된 오브젝트의 타입을 가져와서 그 노드를 선택하는 기능, 프리셋 드롭다운에 특정 노드 타입들 나열하여 선택 가능하도록
    selJntHierBtn = cmds.button(label="Sel Jnt Hierarchy", command=lambda *_: selectJointHierarchy())
    
    # 여러 개의 커브를 하나로 만들기
    combineCrvBtn = cmds.button(label="Combine Crvs", command=lambda *_: combineCurves())
    
    # 오프셋 부모 만들기
    createParentBtn = cmds.button(label="Create Parent", command=lambda *_: createParent())


    cmds.formLayout(formLayout, edit=True, 
                    # attachForm=[(matXFormEachBtn, 'top', 26), (matTranslateEachBtn, 'top', 26)],
                    attachPosition=[(createParentBtn, 'left', 0, 0), (createParentBtn, 'right', 1, 33.33), 
                                    (combineCrvBtn, 'left', 1, 33.33), (combineCrvBtn, 'right', 1, 66.67),
                                    (selJntHierBtn, 'left', 1, 66.67), (selJntHierBtn, 'right', 0, 100)])
                                    # (matXFormEachBtn, 'left', 0, 0), (matXFormEachBtn, 'right', 1, 50), 
                                    # (matTranslateEachBtn, 'left', 1, 50), (matTranslateEachBtn, 'right', 0, 100)])
    
    cmds.setParent('..')

    formLayout = cmds.formLayout(numberOfDivisions=100)
    
    # MatchTransform
    matXFormEachBtn = cmds.button(label="Match Xform Each", command=lambda *_: matchTransformEach())
    matTranslateEachBtn = cmds.button(label="Match Position Each", command=lambda *_: matchTransformEach(position=True, rotation=False, scale=False))

    cmds.formLayout(formLayout, edit=True, 
                    attachPosition=[(matXFormEachBtn, 'left', 0, 0), (matXFormEachBtn, 'right', 5, 50), 
                                    (matTranslateEachBtn, 'left', 5, 50), (matTranslateEachBtn, 'right', 0, 100)])
    

    cmds.setParent('..')

    cmds.separator(style='in')

    # 이름 바꾸기
    cmds.text(label='Rename Selected with Numbers', align='left', font='boldLabelFont')

    cmds.rowLayout(adjustableColumn=1, numberOfColumns=2, generalSpacing=5)
    formLayout = cmds.formLayout(numberOfDivisions=100)

    prefixField = cmds.textField(height=24, placeholderText='prefix')
    suffixField = cmds.textField(height=24, placeholderText='suffix')
    startNumField = cmds.intField(value=1, height=24)

    cmds.formLayout(formLayout, edit=True,
                    attachForm=[(prefixField, 'top', 0), (prefixField, 'left', 0), (suffixField, 'right', 0)],
                    attachControl=[(prefixField, 'right', 5, startNumField), 
                                   (suffixField, 'left', 5, startNumField)],
                    attachPosition=[(startNumField, 'left', 0, 50)])

    cmds.setParent('..')

    cmds.button(label="Rename", width=70, command=lambda *_: renameSelections(prefixField, suffixField, startNumField))

    cmds.setParent('..')

    cmds.setParent('..')

    return layout

def createSkinTab():
    layout = cmds.columnLayout(adjustableColumn=True, margins=10, rowSpacing=10)

    # 트랜스폼 값 초기화
    cmds.text(label='Reset Transform', font='boldLabelFont', align='left')

    formLayout = cmds.formLayout(numberOfDivisions=100)

    resetTranslateBtn = cmds.button(label='Translate', command=lambda *_: resetTransformValue('translate'))
    resetRotateBtn = cmds.button(label='Rotate', command=lambda *_: resetTransformValue('rotate'))
    resetScaleBtn = cmds.button(label='Scale', command=lambda *_: resetTransformValue('scale'))
    resetAllBtn = cmds.button(label='All', command=lambda *_: resetTransformValue())

    cmds.formLayout(formLayout, edit=True, 
                    attachPosition=[(resetAllBtn, 'left', 0, 0), (resetAllBtn, 'right', 0, 25),
                                    (resetScaleBtn, 'left', 0, 25), (resetScaleBtn, 'right', 0, 50),
                                    (resetTranslateBtn, 'left', 0, 50), (resetTranslateBtn, 'right', 0, 75),
                                    (resetRotateBtn, 'left', 0, 75), (resetRotateBtn, 'right', 0, 100)])
    
    cmds.setParent('..')

    cmds.separator(style='in')

    # 키프레임 제거
    formLayout = cmds.formLayout(numberOfDivisions=100)

    btnLabel = cmds.text(label="Remove Keyframe", font="boldLabelFont", align="left", height=22)
    removeCurrKeyframeBtn = cmds.button(label="Current", command=lambda *_: removeKeyframes(False))
    removeKeyframesBtn = cmds.button(label="All", command=lambda *_: removeKeyframes(True))

    cmds.formLayout(formLayout, edit=True,
                    attachPosition=[(btnLabel, 'left', 0, 0), (btnLabel, 'right', 5, 40),
                                    (removeKeyframesBtn, 'left', 0, 40), (removeKeyframesBtn, 'right', 5, 70), 
                                    (removeCurrKeyframeBtn, 'left', 5, 70), (removeCurrKeyframeBtn, 'right', 0, 100)])

    cmds.setParent('..')

    cmds.separator(style='in')

    # 뷰포트 내 조인트 visibility 토글, x-ray 모드 토글
    formLayout = cmds.formLayout(numberOfDivisions=100)

    xRayBtn = cmds.button(label="Toggle X-Ray", command=lambda *_: toggleXRayMode())
    jntVisibilityBtn = cmds.button(label="Toggle Joints Visibility", command=lambda *_: toggleJointsVisibility())

    cmds.formLayout(formLayout, edit=True, 
                    attachPosition=[(xRayBtn, 'left', 0, 0), (xRayBtn, 'right', 5, 50), 
                                    (jntVisibilityBtn, 'left', 5, 50), (jntVisibilityBtn, 'right', 0, 100)])
    
    cmds.setParent('..')

    cmds.separator(style='in')

    # 더미 컨트롤러 생성
    cmds.text(label='Create Dummy Ctrl', font='boldLabelFont', align='left')

    cmds.rowLayout(adjustableColumn=5, numberOfColumns=5, generalSpacing=5)
    cmds.text(label='Forward Axis')
    
    fwdAxisRadioCollection = cmds.radioCollection()
    cmds.radioButton(label='X', select=True)
    cmds.radioButton(label='Y')
    cmds.radioButton(label='Z')

    cmds.button(label="Create", command=lambda *_: createDummyController(fwdAxisRadioCollection))

    cmds.setParent('..')


    cmds.setParent('..')

    return layout

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

    selections = cmds.ls(selection=True, transforms=True)

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

def resetTransformValue(type = None):
    transformChannels = {
        'translate': [('tx', 0), ('ty', 0), ('tz', 0)],
        'rotate': [('rx', 0), ('ry', 0), ('rz', 0)],
        'scale': [('sx', 1), ('sy', 1), ('sz', 1)],
    }
    
    targetTypes = [type] if type else ['translate', 'rotate', 'scale']
    
    for sel in cmds.ls(selection=True):
        for transformType in targetTypes:
            for attr, defaultVal in transformChannels[transformType]:
                try:
                    cmds.setAttr(f'{sel}.{attr}', defaultVal)
                except RuntimeError:
                    pass

def removeKeyframes(all):
    currentTime = cmds.currentTime(query=True)
    time = (None, None) if all else (currentTime, currentTime)

    for sel in cmds.ls(selection=True):
        cmds.cutKey(sel, clear=True, time=time)

def toggleJointsVisibility():
    panel = cmds.getPanel(withFocus=True)
    
    if 'modelPanel' in panel:
        isVisible = cmds.modelEditor(panel, query=True, joints=True)
        cmds.modelEditor(panel, edit=True, joints=not isVisible)

def toggleXRayMode():
    panel = cmds.getPanel(withFocus=True)
    
    if 'modelPanel' in panel:
        isXRayMode = cmds.modelEditor(panel, query=True, xray=True)
        cmds.modelEditor(panel, edit=True, xray=not isXRayMode)

def setLocalRotationAxisVisibility(visible):
    for sel in cmds.ls(selection=True):
        try:
            cmds.setAttr(f'{sel}.displayLocalAxis', visible)
        except:
            continue

def selectJointHierarchy():
    parents = cmds.ls(selection=True)
    hierarchy = []

    for parent in parents:
        children = cmds.listRelatives(parent, allDescendents=True, fullPath=True)

        if children is not None:
            hierarchy += children

    joints = [obj for obj in hierarchy if cmds.objectType(obj) == 'joint']

    if joints:
        cmds.select(joints, replace=True)
    else:
        cmds.select(clear=True)

def combineCurves():
    shapeTransforms = cmds.ls(selection=True)
    shapes = []
    
    for transform in shapeTransforms:
        shapes += cmds.listRelatives(transform, shapes=True)
    
    if len(shapes) == 0:
        return
    
    cmds.makeIdentity(shapes, apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)
    cmds.delete(shapes, constructionHistory=True)

    result = cmds.createNode('transform', name='curve')

    cmds.parent(shapes, result, relative=True, shape=True)

    cmds.delete(shapeTransforms)

def renameSelections(prefixField, suffixField, startNumField):
    prefix = cmds.textField(prefixField, query=True, text=True)
    suffix = cmds.textField(suffixField, query=True, text=True)
    startNum = cmds.intField(startNumField, query=True, value=True)

    for num, sel in enumerate(cmds.ls(selection=True, uuid=True)):
        cmds.rename(cmds.ls(sel), f'{prefix}{startNum + num}{suffix}')
        
def createDummyController(fwdAxisRadioCollection):
    selectedBtn = cmds.radioCollection(fwdAxisRadioCollection, query=True, select=True)
    fwdAxis = cmds.radioButton(selectedBtn, query=True, label=True)
    
    if fwdAxis == 'X':
        normal = (1, 0, 0)
    elif fwdAxis == 'Y':
        normal = (0, 1, 0)
    else:
        normal = (0, 0, 1)
    
    for drivenObj in cmds.ls(selection=True):
        ctrl = f'{drivenObj}_DummyCtrl'
        group = f'{drivenObj}DummyCtrl_Grp'

        if cmds.objExists(ctrl):
            cmds.setAttr(f'{ctrl}.translate', 0, 0, 0)
            cmds.setAttr(f'{ctrl}.rotate', 0, 0, 0)
        else:
            ctrl = cmds.circle(name=ctrl, normal=normal, constructionHistory=False)[0]
            cmds.setAttr(f"{ctrl}.overrideEnabled", True)
            cmds.setAttr(f"{ctrl}.overrideColor", 13)    

        if not cmds.objExists(group):
            group = cmds.group(ctrl, name=group)

        cmds.matchTransform(group, drivenObj, rotation=True, position=True)
        cmds.parentConstraint(ctrl, drivenObj, maintainOffset=True)

    cmds.select(clear=True)

def createParent():
    sel = cmds.ls(selection=True)
    parents = []

    for obj in sel:
        parentName = obj + "_parent"
        parentGrp = cmds.group(empty=True, name=parentName)
        cmds.matchTransform(parentGrp, obj)

        currentParent = cmds.listRelatives(obj, parent=True)
        
        if currentParent:
            cmds.parent(parentGrp, currentParent[0])

        cmds.parent(obj, parentGrp)
        parents.append(parentGrp)

    cmds.select(parents, replace=True)

def matchTransformEach(position=True, rotation=True, scale=True):
    sel = cmds.ls(selection=True)
    
    if not sel:
        return
    
    count = len(sel)
    
    if count % 2 != 0:
        cmds.warning(f"Please select an even number of objects.")
        return
    
    half = count // 2
    sources = sel[:half]
    targets = sel[half:]
    
    for i in range(half):
        cmds.matchTransform(sources[i], targets[i], position=position, rotation=rotation, scale=scale)

openSuyeonToolkit()