import sys
import maya.mel as mel

modulePath = mel.eval('getenv "MAYA_MY_SCRIPT_PATH"')
if modulePath not in sys.path:
    sys.path.append(modulePath)

import maya.cmds as cmds
import utils

ctrl = 'l_leg_front_ik_ctrl'
dir = 'l_front'

cmds.connectAttr(f'{ctrl}.Heel_Twist', f'{dir}_heel_rev.rotateY')
cmds.connectAttr(f'{ctrl}.Toe_Twist', f'{dir}_tip_rev.rotateY')

spreadMultiInner = cmds.shadingNode('multiplyDivide', asUtility=True, name=f'{dir}_inner_toes_multi')
factor = 0.5 * 1 if dir.startswith('l_') else -1
cmds.setAttr(f'{spreadMultiInner}.input2X', factor)
cmds.setAttr(f'{spreadMultiInner}.input2Y', -1 * factor)
spreadMultiOuter = cmds.shadingNode('multiplyDivide', asUtility=True, name=f'{dir}_outer_toes_multi')
factor = 1 * 1 if dir.startswith('l_') else -1
cmds.setAttr(f'{spreadMultiOuter}.input2X', factor)
cmds.setAttr(f'{spreadMultiOuter}.input2Y', -1 * factor)

cmds.connectAttr(f'{ctrl}.Paw_Spread', f'{spreadMultiInner}.input1X')
cmds.connectAttr(f'{ctrl}.Paw_Spread', f'{spreadMultiInner}.input1Y')
cmds.connectAttr(f'{ctrl}.Paw_Spread', f'{spreadMultiOuter}.input1X')
cmds.connectAttr(f'{ctrl}.Paw_Spread', f'{spreadMultiOuter}.input1Y')

for finger in ['index', 'middle', 'ring', 'pinky']:
    toeTapAttr = f'{ctrl}.Toe_Tap'
    toeCurlAttr = f'{ctrl}.Toe_Curl'

    if dir.startswith('r_'):
        multiNode = f'{dir}_toe_tap_curl_multi'

        if not cmds.objExists(multiNode):
            cmds.shadingNode('multiplyDivide', asUtility=True, name=multiNode)
            cmds.setAttr(f'{multiNode}.input2X', -1)
            cmds.setAttr(f'{multiNode}.input2Y', -1)
            cmds.connectAttr(toeTapAttr, f'{multiNode}.input1X')
            cmds.connectAttr(toeCurlAttr, f'{multiNode}.input1Y')
        
        toeTapAttr = f'{multiNode}.outputX'
        toeCurlAttr = f'{multiNode}.outputY'

    cmds.connectAttr(toeTapAttr, f'{dir}_{finger}_end_ikHandle.translateY')
    cmds.connectAttr(toeCurlAttr, f'{dir}_{finger}_tip_ikHandle.translateY')

    if finger == 'middle' or finger == 'ring':
        spreadMulti = spreadMultiInner
    else:
        spreadMulti = spreadMultiOuter

    if finger == 'index' or finger == 'middle':
        output = 'outputX'
    else:
        output = 'outputY'

    cmds.connectAttr(f'{spreadMulti}.{output}', f'{dir}_{finger}_end_ikHandle.translateZ')
    cmds.connectAttr(f'{spreadMulti}.{output}', f'{dir}_{finger}_tip_ikHandle.translateZ')

    



