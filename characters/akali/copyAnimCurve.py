import maya.cmds as cmds

def copyAnimCurveUAToRight(sourceAttr, verbose=True):
    # ── 1. 선택 오브젝트 확인 ──────────────────────────────────────────
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("컨트롤러를 먼저 선택하세요.")
        return

    sourceCtrl = selection[0]

    # ── 2. 오른손 컨트롤러명 미리 결정 ───────────────────────────────
    rightCtrl = sourceCtrl.replace("_l_", "_r_")

    if rightCtrl == sourceCtrl:
        cmds.warning(f"'{sourceCtrl}' - '_l_' 패턴이 없어 오른손 컨트롤러를 특정할 수 없습니다.")
        return

    if not cmds.objExists(rightCtrl):
        cmds.warning(f"오른손 컨트롤러 '{rightCtrl}'이 씬에 없습니다.")
        return

    # ── 3. 지정된 어트리뷰트에 연결된 animCurveUA 노드 수집 ──────────
    if not cmds.attributeQuery(sourceAttr, node=sourceCtrl, exists=True):
        cmds.warning(f"'{sourceCtrl}.{sourceAttr}' 어트리뷰트가 존재하지 않습니다.")
        return

    outConnections = cmds.listConnections(
        f"{sourceCtrl}.{sourceAttr}",
        source=False,
        destination=True,
        type="animCurveUA",
        plugs=False
    )

    if not outConnections:
        cmds.warning(f"'{sourceCtrl}.{sourceAttr}'에 연결된 animCurveUA 노드가 없습니다.")
        return

    animCurveNodes = list(set(outConnections))

    if verbose:
        print(f"\n[copyAnimCurveUAToRight] '{sourceCtrl}.{sourceAttr}'에서 {len(animCurveNodes)}개의 animCurveUA 발견")

    results = {"success": [], "skipped": [], "error": []}

    for curveNode in animCurveNodes:

        # ── 4. 노드 이름 파싱 ─────────────────────────────────────────
        lastUnderscoreIdx = curveNode.rfind("_")
        if lastUnderscoreIdx == -1:
            cmds.warning(f"  [SKIP] '{curveNode}' - 언더스코어가 없어 파싱 불가")
            results["skipped"].append(curveNode)
            continue

        targetObj  = curveNode[:lastUnderscoreIdx]
        targetAttr = curveNode[lastUnderscoreIdx + 1:]

        # ── 5. _l_ → _r_ 치환 ────────────────────────────────────────
        rightTargetObj = targetObj.replace("_l_", "_r_")
        rightCurveName = curveNode.replace("_l_", "_r_")

        if rightTargetObj == targetObj:
            cmds.warning(f"  [SKIP] '{curveNode}' - '_l_' 패턴 없음")
            results["skipped"].append(curveNode)
            continue

        # ── 6. 오른손 대상 오브젝트 존재 여부 확인 ───────────────────
        if not cmds.objExists(rightTargetObj):
            cmds.warning(f"  [SKIP] '{curveNode}' - 오른손 대상 '{rightTargetObj}'이 씬에 없음")
            results["skipped"].append(curveNode)
            continue

        # ── 7. 중복 노드 체크 → 경고 후 스킵 ─────────────────────────
        if cmds.objExists(rightCurveName):
            cmds.warning(f"  [WARNING] '{rightCurveName}'이 이미 존재합니다. 스킵합니다.")
            results["skipped"].append(curveNode)
            continue

        # ── 8. animCurveUA 노드 복제 ──────────────────────────────────
        try:
            duplicated = cmds.duplicate(curveNode, name=rightCurveName)[0]
        except Exception as e:
            cmds.warning(f"  [ERROR] '{curveNode}' duplicate 실패: {e}")
            results["error"].append(curveNode)
            continue

        # ── 9. 오른손 컨트롤러 → 복제 노드 input 연결 ────────────────
        if cmds.attributeQuery(sourceAttr, node=rightCtrl, exists=True):
            cmds.connectAttr(f"{rightCtrl}.{sourceAttr}", f"{duplicated}.input", force=True)
        else:
            cmds.warning(f"  [WARNING] '{rightCtrl}.{sourceAttr}' 어트리뷰트 없음, input 연결 스킵")

        # ── 10. 복제 노드 output → 오른손 대상 어트리뷰트 연결 ────────
        try:
            rightTargetPlug = f"{rightTargetObj}.{targetAttr}"

            if not cmds.attributeQuery(targetAttr, node=rightTargetObj, exists=True):
                cmds.warning(f"  [WARNING] '{rightTargetPlug}' 어트리뷰트 없음, output 연결 스킵")
                results["skipped"].append(curveNode)
                continue

            cmds.connectAttr(f"{duplicated}.output", rightTargetPlug, force=True)

            if verbose:
                print(f"  [OK] {curveNode}  →  복제: {duplicated}  →  {rightTargetPlug}")

            results["success"].append(duplicated)

        except Exception as e:
            cmds.warning(f"  [ERROR] '{duplicated}' output 연결 실패: {e}")
            results["error"].append(curveNode)

    # ── 11. 결과 요약 ─────────────────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"[copyAnimCurveUAToRight] 완료 요약")
    print(f"  ✔ 성공  : {len(results['success'])}개")
    print(f"  ⚠ 스킵  : {len(results['skipped'])}개")
    print(f"  ✖ 오류  : {len(results['error'])}개")
    print(f"{'='*55}\n")

    return results


# ── 실행 ──────────────────────────────────────────────────────────────────
copyAnimCurveUAToRight(sourceAttr="pose_fist")