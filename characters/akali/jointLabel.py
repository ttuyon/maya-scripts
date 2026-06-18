"""
MetaHuman Joint Label Script for Maya 2025
==========================================
- type : 전부 18 (Other) 고정
- side : 본 이름 끝의 _l / _r / 없음 으로 자동 판별
- otherType : _l / _r 을 제거한 나머지 이름
"""

import maya.cmds as cmds

# side 인덱스
SIDE_NONE   = 0
SIDE_LEFT   = 1
SIDE_RIGHT  = 2

LABEL_OTHER = 18


def parse_joint_name(short_name):
    """
    본 이름에서 side 와 otherType 을 추출한다.

    '_l' 로 끝나면 → Left,  otherType = 접미사 제거한 이름
    '_r' 로 끝나면 → Right, otherType = 접미사 제거한 이름
    그 외           → None,  otherType = 이름 그대로

    Returns
    -------
    (side: int, other_type: str)
    """
    lower = short_name.lower()

    if lower.endswith("_l"):
        return SIDE_LEFT,  short_name[:-2]   # 뒤 2글자(_l) 제거
    elif lower.endswith("_r"):
        return SIDE_RIGHT, short_name[:-2]   # 뒤 2글자(_r) 제거
    else:
        return SIDE_NONE,  short_name


def label_joint(joint):
    """
    조인트 하나에 라벨을 설정한다.
    type = 18(Other) 고정 / side·otherType 은 이름에서 자동 추출.
    """
    if not cmds.objExists(joint):
        return False
    if cmds.nodeType(joint) != "joint":
        return False

    short_name = joint.split("|")[-1].split(":")[-1]   # namespace 제거
    side, other_type = parse_joint_name(short_name)

    cmds.setAttr(f"{joint}.side", side)
    cmds.setAttr(f"{joint}.type", LABEL_OTHER)
    cmds.setAttr(f"{joint}.otherType", other_type, type="string")

    return True


def run(verbose=True):
    """씬 내 모든 조인트에 라벨을 적용한다."""
    all_joints = cmds.ls(type="joint") or []

    if not all_joints:
        cmds.warning("씬에 조인트가 없습니다.")
        return

    ok, fail = [], []

    for jnt in all_joints:
        (ok if label_joint(jnt) else fail).append(jnt)

    if verbose:
        print("=" * 50)
        print(f"[MetaHuman Label] ✅ {len(ok)}개 완료 / ⚠️ {len(fail)}개 실패")
        print("=" * 50)

    return ok, fail


def run_selected(verbose=True):
    """선택된 조인트에만 라벨을 적용한다."""
    joints = cmds.ls(selection=True, type="joint") or []

    if not joints:
        cmds.warning("조인트를 먼저 선택하세요.")
        return

    ok, fail = [], []

    for jnt in joints:
        (ok if label_joint(jnt) else fail).append(jnt)

    if verbose:
        print(f"[선택 라벨] ✅ {len(ok)}개 완료 / ⚠️ {len(fail)}개 실패")

    return ok, fail


run_selected()