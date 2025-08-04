import maya.cmds as cmds

locked = True
keyable = False

searchList = ["*_grp", "*_ikHandle", "*_offset", "*_rot", "*Constraint1", "*Constraint", "*_aim", "*_clstrtop", "*_rev", "*_loc", "*_cluster", "*_cluster*", "*_driver"]

for search in searchList:
    selList = cmds.ls(search, transforms=True, showType=True)

    for i in range(0, len(selList), 2):
        sel, nodeType = selList[i], selList[i+1]

        if nodeType == 'joint':
            continue

        cmds.setAttr((sel + ".tx"), k=keyable, l=locked)
        cmds.setAttr((sel + ".ty"), k=keyable, l=locked)
        cmds.setAttr((sel + ".tz"), k=keyable, l=locked)

        cmds.setAttr((sel + ".rx"), k=keyable, l=locked)
        cmds.setAttr((sel + ".ry"), k=keyable, l=locked)
        cmds.setAttr((sel + ".rz"), k=keyable, l=locked)

        cmds.setAttr((sel + ".sx"), k=keyable, l=locked)
        cmds.setAttr((sel + ".sy"), k=keyable, l=locked)
        cmds.setAttr((sel + ".sz"), k=keyable, l=locked)

        cmds.setAttr((sel + ".v"), k=keyable, l=locked)
