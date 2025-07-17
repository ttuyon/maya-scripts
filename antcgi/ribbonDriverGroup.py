#-----------------------------------------
# antcgi 리본 툴 사용 시 Driver Group 옵션이 제대로 작동하지 않아 이를 대체하기 위한 스크립트
#-----------------------------------------

import sys
import maya.mel as mel

modulePath = mel.eval('getenv "MAYA_MY_SCRIPT_PATH"')
if modulePath not in sys.path:
    sys.path.append(modulePath)

import maya.cmds as cmds

offsetGrps = cmds.ls(selection=True)
joint = 'jaw_base' ########### NEED TO UPDATE

parent = cmds.listRelatives(offsetGrps[0], parent=True)[0]

for offsetGrp in offsetGrps:
    driverGrp = cmds.group(empty=True, name=offsetGrp.replace('_offset', '_driver'), parent=parent)
    cmds.matchTransform(driverGrp, joint, position=True, rotation=True)
    cmds.parent(offsetGrp, driverGrp)