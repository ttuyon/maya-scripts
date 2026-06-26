import maya.cmds as cmds

def matchCvPositions():
    # 선택된 오브젝트 가져오기
    selection = cmds.ls(orderedSelection=True, long=True)
    
    if len(selection) < 2:
        cmds.warning("최소 두 개 이상의 커브를 선택해주세요.")
        return
    
    if len(selection) % 2 != 0:
        cmds.warning("선택한 커브의 수가 홀수입니다. 짝수 개를 선택해주세요. 현재 선택: {}개".format(len(selection)))
        return
    
    halfCount = len(selection) // 2
    
    # 앞 절반 = 이동될 커브들, 뒤 절반 = 기준 커브들
    sourceCurves = selection[:halfCount]
    targetCurves = selection[halfCount:]
    
    for sourceCurve, targetCurve in zip(sourceCurves, targetCurves):
        # CV 개수 확인
        sourceCvCount = cmds.getAttr(sourceCurve + ".spans") + cmds.getAttr(sourceCurve + ".degree")
        targetCvCount = cmds.getAttr(targetCurve + ".spans") + cmds.getAttr(targetCurve + ".degree")
        
        if sourceCvCount != targetCvCount:
            cmds.warning(
                "'{}' 와 '{}' 의 CV 개수가 다릅니다. Source: {}, Target: {} — 이 쌍은 건너뜁니다.".format(
                    sourceCurve, targetCurve, sourceCvCount, targetCvCount
                )
            )
            continue
        
        # 각 CV 위치를 타겟 기준으로 이동
        for i in range(sourceCvCount):
            targetPos = cmds.xform(
                "{}.cv[{}]".format(targetCurve, i),
                query=True,
                worldSpace=True,
                translation=True
            )
            cmds.xform(
                "{}.cv[{}]".format(sourceCurve, i),
                worldSpace=True,
                translation=targetPos
            )
        
        print("CV 매칭 완료: '{}' → '{}'".format(sourceCurve, targetCurve))

matchCvPositions()