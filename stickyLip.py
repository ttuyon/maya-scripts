import maya.cmds as cmds
import math

def createStickyLip():
    lf_main_attr = "lip_ctrl.lf_lip_seal"
    rt_main_attr = "lip_ctrl.rt_lip_seal"
    lip_val_list = [21, 15]
    lip_name_list = ['upperlip', 'lowerlip']

    name_counter = 0
    for each in lip_val_list:
        half_val = math.floor((each / 2)) + 1
        
        total_val = each + 1
        div_val = 10.0 / half_val
        counter = 0
        while(counter<half_val):
            lip_sr = cmds.shadingNode( 'setRange', asUtility=True, n=lip_name_list[name_counter] + '_' + str(counter+1).zfill(2) + '_l' + '_setRange')
            cmds.setAttr(lip_sr + '.oldMaxX', (div_val * (counter+1)))
            cmds.setAttr(lip_sr + '.oldMinX', (div_val * counter))
            cmds.setAttr(lip_sr + '.maxX', 0)
            cmds.setAttr(lip_sr + '.minX', 1)
            if counter == (half_val - 1):
                cmds.setAttr(lip_sr + '.minX', 0.5)
            cmds.connectAttr(lf_main_attr, lip_sr + '.valueX', f=True)
            
            lip_flip_sr = cmds.shadingNode( 'setRange', asUtility=True, n=lip_name_list[name_counter] + '_flip_' + str(counter+1).zfill(2) + '_l' + '_setRange')
            cmds.setAttr(lip_flip_sr + '.oldMaxX', 1)
            if counter == (half_val - 1):
                cmds.setAttr(lip_flip_sr + '.oldMaxX', 0.5)
            cmds.setAttr(lip_flip_sr + '.oldMinX', 0)
            cmds.setAttr(lip_flip_sr + '.maxX', 0)
            cmds.setAttr(lip_flip_sr + '.minX', 1)
            if counter == (half_val - 1):
                cmds.setAttr(lip_flip_sr + '.minX', 0.5)
            cmds.connectAttr(lip_sr + '.outValueX', lip_flip_sr + '.valueX', f=True)
                
            if counter == (half_val - 1):
                mid_pma = cmds.shadingNode( 'plusMinusAverage', asUtility=True, n=lip_name_list[name_counter] + '_' + str(counter+1).zfill(2) + '_ct' + '_plusMinusAverage')
                cmds.connectAttr(lip_sr + '.outValueX', mid_pma + '.input2D[0].input2Dx', f=True)
                cmds.connectAttr(lip_flip_sr + '.outValueX', mid_pma + '.input2D[0].input2Dy', f=True)
            else:
                cmds.connectAttr(lip_sr + '.outValueX', lip_name_list[name_counter] + '_wire_blsh.inputTarget[0].inputTargetGroup[0].targetWeights[' + str(counter) + ']', f=True)
                cmds.connectAttr(lip_flip_sr + '.outValueX', lip_name_list[name_counter] + '_wire_blsh.inputTarget[0].inputTargetGroup[1].targetWeights[' + str(counter) + ']', f=True)
            
            counter = counter + 1
            
        counter = half_val - 1
        rev_counter = half_val
        while(counter<total_val):
            lip_sr = cmds.shadingNode( 'setRange', asUtility=True, n=lip_name_list[name_counter] + '_' + str(counter+1).zfill(2) + '_r' + '_setRange')
            cmds.setAttr(lip_sr + '.oldMaxX', (div_val * rev_counter))
            cmds.setAttr(lip_sr + '.oldMinX', (div_val * (rev_counter-1)))
            cmds.setAttr(lip_sr + '.maxX', 0)
            cmds.setAttr(lip_sr + '.minX', 1)
            if counter == (half_val - 1):
                cmds.setAttr(lip_sr + '.minX', 0.5)
            cmds.connectAttr(rt_main_attr, lip_sr + '.valueX', f=True)
            
            lip_flip_sr = cmds.shadingNode( 'setRange', asUtility=True, n=lip_name_list[name_counter] + '_flip_' + str(counter+1).zfill(2) + '_r' + '_setRange')
            cmds.setAttr(lip_flip_sr + '.oldMaxX', 1)
            if counter == (half_val - 1):
                cmds.setAttr(lip_flip_sr + '.oldMaxX', 0.5)
            cmds.setAttr(lip_flip_sr + '.oldMinX', 0)
            cmds.setAttr(lip_flip_sr + '.maxX', 0)
            cmds.setAttr(lip_flip_sr + '.minX', 1)
            if counter == (half_val - 1):
                cmds.setAttr(lip_flip_sr + '.minX', 0.5)
            cmds.connectAttr(lip_sr + '.outValueX', lip_flip_sr + '.valueX', f=True)
            
            if counter == (half_val - 1):
                cmds.connectAttr(lip_sr + '.outValueX', mid_pma + '.input2D[1].input2Dx', f=True)
                cmds.connectAttr(lip_flip_sr + '.outValueX', mid_pma + '.input2D[1].input2Dy', f=True)
                cmds.connectAttr(mid_pma + '.output2Dx', lip_name_list[name_counter] + '_wire_blsh.inputTarget[0].inputTargetGroup[0].targetWeights[' + str(counter) + ']', f=True)
                cmds.connectAttr(mid_pma + '.output2Dy', lip_name_list[name_counter] + '_wire_blsh.inputTarget[0].inputTargetGroup[1].targetWeights[' + str(counter) + ']', f=True)
            else:
                cmds.connectAttr(lip_sr + '.outValueX', lip_name_list[name_counter] + '_wire_blsh.inputTarget[0].inputTargetGroup[0].targetWeights[' + str(counter) + ']', f=True)
                cmds.connectAttr(lip_flip_sr + '.outValueX', lip_name_list[name_counter] + '_wire_blsh.inputTarget[0].inputTargetGroup[1].targetWeights[' + str(counter) + ']', f=True)
            
            counter = counter + 1
            rev_counter = rev_counter - 1
        name_counter = name_counter + 1
        

# 각 엣지 위치에 조인트 생성: upperlip_01...

JOINT_SIDE_NONE   = 0
JOINT_SIDE_LEFT   = 1
JOINT_SIDE_RIGHT  = 2

JOINT_LABEL_OTHER = 18

def createJoint():
    lips = ['upperlip', 'lowerlip']
    for lip in lips:
        curve = lip + '_linear_crv'
        jointGrp = cmds.group(empty=True, name=lip + '_joint_grp')
        cvCount = cmds.getAttr(f"{curve}.degree") + cmds.getAttr(f"{curve}.spans")
        for i in range(cvCount):
            cmds.select(clear=True)
            cvPos = cmds.xform(f"{curve}.cv[{i}]", q=True, ws=True, t=True)
            jnt = cmds.joint(name=f"{lip}_{(i + 1):02d}", position=cvPos, radius=.1)
            cmds.parent(jnt, jointGrp)

            if cvCount % 2 == 1 and i == cvCount // 2:
                side = JOINT_SIDE_NONE
                label = 'mid'
            elif i < cvCount // 2:
                side = JOINT_SIDE_LEFT
                label = f'side_{(i + 1):02d}'
            else:
                side = JOINT_SIDE_RIGHT
                label = f'side_{(cvCount - i):02d}'
            
            cmds.setAttr(f"{jnt}.type", JOINT_LABEL_OTHER)
            cmds.setAttr(f"{jnt}.side", side)
            cmds.setAttr(f"{jnt}.otherType", f"{lip}_{label}", type="string")

# 조인트를 드라이브할 로케이터 생성
def createLocator():
    lips = ['upperlip', 'lowerlip']

    for lip in lips:
        curve = lip + '_wire_crv'
        cvCount = cmds.getAttr(f"{curve}.degree") + cmds.getAttr(f"{curve}.spans")
        
        nearestNode = cmds.createNode("nearestPointOnCurve", name="temp_nearest")
        cmds.connectAttr(f"{curve}.worldSpace[0]", f"{nearestNode}.inputCurve")

        # 그룹 미리 생성
        locGrp = cmds.group(empty=True, name=f"{lip}_loc_grp")
        locBaseGrp = cmds.group(empty=True, name=f"{lip}_loc_base_grp")
        
        for i in range(cvCount):
            cvPos = cmds.xform(f"{curve}.cv[{i}]", q=True, ws=True, t=True)
            
            cmds.setAttr(f"{nearestNode}.inPosition", *cvPos)
            param = cmds.getAttr(f"{nearestNode}.parameter")
            
            # 로케이터 생성 후 그룹에 삽입
            locTransform = cmds.spaceLocator(name=f"{lip}_{(i + 1):02d}_loc")[0]
            # cmds.xform(locTransform, ws=True, t=cvPos)
            cmds.parent(locTransform, locGrp)

            locBaseTransform = cmds.spaceLocator(name=f"{lip}_{(i + 1):02d}_base_loc")[0]
            cmds.parent(locBaseTransform, locBaseGrp)
            
            # pointOnCurveInfo 생성
            pocNode = cmds.createNode("pointOnCurveInfo", name=f"{lip}_{(i + 1):02d}_pointOnCurveInfo")
            cmds.connectAttr(f"{curve}.worldSpace[0]", f"{pocNode}.inputCurve")
            cmds.setAttr(f"{pocNode}.parameter", param)
            cmds.connectAttr(f"{pocNode}.position", f"{locTransform}.translate")
            cmds.connectAttr(f"{pocNode}.position", f"{locBaseTransform}.translate")
            cmds.disconnectAttr(f"{pocNode}.position", f"{locBaseTransform}.translate")
        
        cmds.delete(nearestNode)

def connectCtrlCrvLocatorsToJoints():
    lips = ['upperlip', 'lowerlip']

    for lip in lips:
        count = cmds.getAttr(f"{lip}_linear_crv.degree") + cmds.getAttr(f"{lip}_linear_crv.spans")
        for i in range(1, count + 1):
            index = f"{i:02d}"

            locName = f"{lip}_{index}_loc"
            baseLocName = f"{lip}_{index}_base_loc"
            jointName = f"{lip}_{index}"

            for node in [locName, baseLocName, jointName]:
                if not cmds.objExists(node):
                    cmds.warning(f"[connectLocatorsToJoints] 노드를 찾을 수 없습니다: {node}")
                    continue

            multNode = cmds.createNode("multMatrix", name=f"{lip}_{index}_offset_multMatrix")

            cmds.connectAttr(f"{locName}.worldMatrix[0]", f"{multNode}.matrixIn[0]")
            cmds.connectAttr(f"{baseLocName}.worldInverseMatrix[0]", f"{multNode}.matrixIn[1]")
            cmds.connectAttr(f"{multNode}.matrixSum", f"{jointName}.offsetParentMatrix")

            print(f"[OK] {locName} & {baseLocName} → {jointName}.offsetParentMatrix")

def createCtrlCrvJnt():
    """
    두 커브의 5개 지점에 조인트 생성
    0.0 / 0.25 / 0.5 / 0.75 / 1.0 (parameter 기준)
    양 끝 지점(0.0, 1.0)은 두 커브가 공유 → 조인트 하나만 생성

    Args:
        curveNameA (str): 첫 번째 커브 이름
        curveNameB (str): 두 번째 커브 이름
    """
    lips = ['upperlip', 'lowerlip']
    curves = [f'{lip}_control_crv' for lip in lips]

    for curveName in curves:
        if not cmds.objExists(curveName):
            cmds.warning(f"[createJointsOnCurve] 커브를 찾을 수 없습니다: {curveName}")
            return

    paramJointPairs = [
        (0.0,  "side_l"),
        (0.25, "side_l"),
        (0.5,  "mid"),
        (0.75, "side_r"),
        (1.0,  "side_r"),
    ]

    cbJoints = [[], []]
    cbJointsGrp = cmds.group(empty=True, name='lip_ctrl_cb_joint_grp')

    for param, label in paramJointPairs:
        isShared = param in (0.0, 1.0)  # 양 끝은 공유 지점

        # 공유 지점 → curveNameA 기준으로 조인트 하나만 생성
        targets = [(curves[0], "lip")] if isShared else [
            (curves[0], lips[0]),
            (curves[1], lips[1]),
        ]

        for curveName, prefix in targets:
            pociNode = cmds.createNode("pointOnCurveInfo", name=f"{curveName}_{label}_poci")

            cmds.connectAttr(f"{curveName}.worldSpace[0]", f"{pociNode}.inputCurve")
            cmds.setAttr(f"{pociNode}.turnOnPercentage", 1)
            cmds.setAttr(f"{pociNode}.parameter", param)

            pos = cmds.getAttr(f"{pociNode}.position")[0]

            cmds.select(clear=True)
            cbJnt = cmds.joint(name=f"{prefix}_{label}", position=pos, radius=.3)
            cmds.parent(cbJnt, cbJointsGrp)

            cmds.delete(pociNode)

            print(f"[OK] {cbJnt} → position {pos}")

            if isShared:
                cbJoints[0].append(cbJnt)
                cbJoints[1].append(cbJnt)
            elif curveName == curves[0]:
                cbJoints[0].append(cbJnt)
            else:
                cbJoints[1].append(cbJnt)

    for i in range(2):
        cmds.skinCluster(
            cbJoints[i] + [curves[i]],
            name=f"{curves[i]}_skinCluster",
            toSelectedBones=True,
            bindMethod=0,   # Closest Distance
            skinMethod=0,   # Classic Linear
            normalizeWeights=1,
            multi=False,
            maximumInfluences=5,
            obeyMaxInfluences=True,
            removeUnusedInfluence=False
        )
        print(f"[OK] {curves[i]} 스킨 바인드 완료 → {cbJoints[i]}")

def createMasterCtrlCrv():
    lips = ['upperlip', 'lowerlip']

    cbJointNames = [
        ['lip_side_l', 'upperlip_side_l', 'upperlip_mid', 'upperlip_side_r', 'lip_side_r'],
        ['lip_side_l', 'lowerlip_side_l', 'lowerlip_mid', 'lowerlip_side_r', 'lip_side_r'],
    ]

    # 양 끝 조인트 한 세트만 먼저 생성
    sharedPositions = {}
    for jntName, side in [('lip_side_l', 'l'), ('lip_side_r', 'r')]:
        if not cmds.objExists(jntName):
            cmds.warning(f"[createMasterCtrlCrv] 조인트를 찾을 수 없습니다: {jntName}")
            return
        sharedPositions[side] = cmds.xform(jntName, query=True, worldSpace=True, translation=True)

    endJoints = []
    for side in ['l', 'r']:
        cmds.select(clear=True)
        endJnt = cmds.joint(
            name=f"lip_corner_{side}",
            position=sharedPositions[side],
            radius=0.3
        )
        endJoints.append(endJnt)

    cmds.group(endJoints, name='lip_corner_ctrl_cb_joint_grp')

    # 커브 생성 & 바인드
    drivenCurves = []
    for i, lip in enumerate(lips):
        positions = []
        for jntName in cbJointNames[i]:
            if not cmds.objExists(jntName):
                cmds.warning(f"[createMasterCtrlCrv] 조인트를 찾을 수 없습니다: {jntName}")
                return
            pos = cmds.xform(jntName, query=True, worldSpace=True, translation=True)
            positions.append(pos)

        pointArgs = [tuple(p) for p in positions]
        drivenCrv = cmds.curve(
            ep=pointArgs,
            degree=3,
            name=f"{lip}_control_master_crv"
        )
        # 추후 작업을 편하게 해주기 위해 파라미터를 span값과 동일하게 맞춰줌
        cmds.rebuildCurve(
            drivenCrv,
            constructionHistory=False,
            replaceOriginal=True,
            rebuildType=0,
            endKnots=True,
            keepRange=2,
            keepControlPoints=True,
            keepEndPoints=True,
            keepTangents=False,
            spans=cmds.getAttr(f"{drivenCrv}.spans"),
            degree=3,
            tolerance=0
        )
        drivenCurves.append(drivenCrv)
        print(f"[OK] {drivenCrv} 생성 완료")

        # 같은 endJoints로 두 커브 모두 바인드
        cmds.skinCluster(
            endJoints + [drivenCrv],
            name=f"{drivenCrv}_skinCluster",
            toSelectedBones=True,
            bindMethod=0,
            skinMethod=0,
            normalizeWeights=1,
            maximumInfluences=2,
            obeyMaxInfluences=True,
            removeUnusedInfluence=False
        )
        print(f"[OK] {drivenCrv} 스킨 바인드 완료 → {endJoints}")

def createController():
    """
    입꼬리 조인트: ctrl_grp - ctrl (parentConstraint)
    입 디테일 조인트: ctrl_off1_grp - ctrl_off2_grp - ctrl
    """
    cornerJoints = [
        'lip_corner_l',
        'lip_corner_r',
    ]

    detailJoints = [
        'lip_side_l',
        'upperlip_side_l', 'upperlip_mid', 'upperlip_side_r',
        'lowerlip_side_l', 'lowerlip_mid', 'lowerlip_side_r',
        'lip_side_r',
    ]

    ctrlsGrp = cmds.group(empty=True, name='lip_ctrls_grp')

    # ── 입꼬리 컨트롤러 ────────────────────────────────
    for jntName in cornerJoints:
        if not cmds.objExists(jntName):
            cmds.warning(f"[createLipCtrls] 조인트를 찾을 수 없습니다: {jntName}")
            continue

        ctrlName = f"{jntName}_ctrl"
        grpName  = f"{jntName}_ctrl_grp"

        ctrl = cmds.circle(name=ctrlName, normal=(0, 0, 1), radius=0.5, constructionHistory=False)[0]
        grp  = cmds.group(ctrl, name=grpName)

        cmds.matchTransform(grp, jntName)
        cmds.parentConstraint(ctrl, jntName, maintainOffset=True)
        cmds.parent(grp, ctrlsGrp)

        print(f"[OK] {grpName} → {ctrlName} → parentConstraint → {jntName}")

    # ── 입 디테일 컨트롤러 ────────────────────────────
    for jntName in detailJoints:
        if not cmds.objExists(jntName):
            cmds.warning(f"[createLipCtrls] 조인트를 찾을 수 없습니다: {jntName}")
            continue

        ctrlName = f"{jntName}_ctrl"
        off1Name = f"{jntName}_ctrl_off1_grp"
        off2Name = f"{jntName}_ctrl_off2_grp"

        ctrl = cmds.circle(name=ctrlName, normal=(0, 0, 1), radius=0.3, constructionHistory=False)[0]
        off2 = cmds.group(ctrl, name=off2Name)
        off1 = cmds.group(off2, name=off1Name)

        cmds.matchTransform(off1, jntName)
        cmds.parent(off1, ctrlsGrp)

        print(f"[OK] {off1Name} → {off2Name} → {ctrlName}")

def connectDetailCtrlSystem():
    lips = ['upperlip', 'lowerlip']

    for lip in lips:
        masterCrv = f"{lip}_control_master_crv"
        boundCrv  = f"{lip}_bound_crv"

        spanCount = cmds.getAttr(masterCrv + ".spans")

        locGrp = cmds.group(empty=True, name=f"{lip}_control_master_loc_grp")
        baseGrp = cmds.group(empty=True, name=f"{lip}_control_master_base_loc_grp")

        # -------------------------------
        # 1. master curve locator 생성
        # -------------------------------
        for i in range(spanCount + 1):
            loc = cmds.spaceLocator(n=f"{lip}_{(i + 1):02d}_master_loc")[0]
            base = cmds.spaceLocator(n=f"{lip}_{(i + 1):02d}_master_base_loc")[0]

            cmds.parent(loc, locGrp)
            cmds.parent(base, baseGrp)

            poc = cmds.createNode("pointOnCurveInfo",
                n=f"{masterCrv}_{(i + 1):02d}_pointOnCurveInfo")

            cmds.connectAttr(masterCrv + ".worldSpace[0]", poc + ".inputCurve")
            cmds.setAttr(poc + ".parameter", i)

            cmds.connectAttr(poc + ".position", loc + ".translate")
            cmds.connectAttr(poc + ".position", base + ".translate")
            cmds.disconnectAttr(poc + ".position", base + ".translate")

        # ----------------------------------
        # 2 / 3 detail controller 연결
        # ----------------------------------
        
        detailMap = {
            'upperlip': [
                ('side_l', 0.0),
                ('side_l', 0.25),
                ('mid',    0.5),
                ('side_r', 0.75),
                ('side_r', 1.0),
            ],
            'lowerlip': [
                ('side_l', 0.0),
                ('side_l', 0.25),
                ('mid',    0.5),
                ('side_r', 0.75),
                ('side_r', 1.0),
            ]
        }
        
        for i, (label, param) in enumerate(detailMap[lip]):

            if param in (0.0, 1.0):
                if lip == 'lowerlip':
                    continue
                prefix = "lip"
            else:
                prefix = lip

            ctrl = f"{prefix}_{label}_ctrl"
            off1 = f"{prefix}_{label}_ctrl_off1_grp"
            off2 = f"{prefix}_{label}_ctrl_off2_grp"
            joint = f"{prefix}_{label}"

            loc = f"{lip}_{(i + 1):02d}_master_loc"
            base = f"{lip}_{(i + 1):02d}_master_base_loc"

            # -------------------------
            # 변화량 matrix
            # -------------------------
            masterDeltaMult = cmds.createNode("multMatrix",
                n=f"{prefix}_{label}_masterDelta_mult")

            cmds.connectAttr(loc + ".worldMatrix[0]", masterDeltaMult + ".matrixIn[0]")
            cmds.connectAttr(base + ".worldInverseMatrix[0]", masterDeltaMult + ".matrixIn[1]")

            # translate만 추출
            decompose = cmds.createNode("decomposeMatrix",
                n=f"{prefix}_{label}_masterDelta_decomposeMatrix")


            cmds.connectAttr(masterDeltaMult + ".matrixSum", decompose + ".inputMatrix")

            # off2_grp translate 연결
            cmds.connectAttr(decompose + ".outputTranslate",
                             off2 + ".translate")

            # -------------------------
            # bound curve → off1_grp
            # -------------------------
            boundPoc = cmds.createNode("pointOnCurveInfo",
                n=f"{prefix}_{label}_bound_pointOnCurveInfo")

            cmds.connectAttr(boundCrv + ".worldSpace[0]",
                             boundPoc + ".inputCurve")

            cmds.setAttr(boundPoc + ".turnOnPercentage", 1)
            cmds.setAttr(boundPoc + ".parameter", param)

            cmds.connectAttr(boundPoc + ".position",
                             off1 + ".translate")

            # -------------------------
            # controller + delta → joint
            # -------------------------
            ctrlDeltaMult = cmds.createNode("multMatrix",
                n=f"{prefix}_{label}_ctrl_multMatrix")

            cmds.connectAttr(ctrl + ".matrix",
                             ctrlDeltaMult + ".matrixIn[0]")

            cmds.connectAttr(masterDeltaMult + ".matrixSum",
                             ctrlDeltaMult + ".matrixIn[1]")

            finalPick = cmds.createNode("pickMatrix",
                n=f"{prefix}_{label}_finalDelta_pickMatrix")

            cmds.setAttr(finalPick + ".useRotate", 0)
            cmds.setAttr(finalPick + ".useScale", 0)
            cmds.setAttr(finalPick + ".useShear", 0)

            cmds.connectAttr(ctrlDeltaMult + ".matrixSum",
                             finalPick + ".inputMatrix")

            cmds.connectAttr(finalPick + ".outputMatrix",
                             joint + ".offsetParentMatrix")


connectDetailCtrlSystem()

