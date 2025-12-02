import maya.cmds as cmds

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