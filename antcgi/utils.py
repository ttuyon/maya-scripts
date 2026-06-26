import maya.cmds as cmds

def getJointDisplayRadius(jointName):
   radius = cmds.getAttr(f"{jointName}.radius")
   globalScale = cmds.jointDisplayScale(query=True)
   return radius * globalScale

def setShapeColor(object: str, color: int):
    for shape in cmds.listRelatives(object, shapes=True):
        cmds.setAttr(f"{shape}.overrideEnabled", True)
        cmds.setAttr(f"{shape}.overrideColor", color)

def overrideDisplayTypeToReference(object: str):
    cmds.setAttr(f"{object}.overrideEnabled", True)
    cmds.setAttr(f"{object}.overrideDisplayType", 2)

def getWidthInWorld(object: str):
    bbox = cmds.exactWorldBoundingBox(object)
    width = bbox[3] - bbox[0]
    return width

def getHeightInWorld(object: str):
    bbox = cmds.exactWorldBoundingBox(object)
    height = bbox[4] - bbox[1]
    return height

def addSeparatorAttribute(object: str, attrName: str):
    cmds.addAttr(object, longName=attrName, attributeType='enum', enumName='----------')
    cmds.setAttr(f'{object}.{attrName}', edit=True, channelBox=True, lock=True)