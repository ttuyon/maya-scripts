import maya.cmds as cmds
import maya.mel as mel

def objectMode():
    hilite = cmds.ls(hilite=True)
    
    if not hilite:
        return
    
    obj = cmds.ls(dag=True, selection=True)

    cmds.selectMode(object=True)
    cmds.select(obj + hilite, replace=True)

    message = mel.eval('uiRes("m_toggleSelMode.kIvmSelectObject")')
    cmds.inViewMessage(message=message, fade=True, position='topCenter')

def componentMode():
    hilite = cmds.ls(hilite=True)

    if hilite:
        return
    
    cmds.selectMode(component=True)
    message = mel.eval('uiRes("m_toggleSelMode.kIvmSelectComponent")')
    cmds.inViewMessage(message=message, fade=True, position='topCenter')