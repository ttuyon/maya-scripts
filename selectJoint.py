import maya.cmds as cmds

parent = cmds.ls(selection=True)[0]

children = cmds.listRelatives(parent, allDescendents=True, fullPath=True)

joints = [obj for obj in children if cmds.objectType(obj) == 'joint']

if joints:
    cmds.select(joints, replace=True)
else:
    cmds.select(clear=True)