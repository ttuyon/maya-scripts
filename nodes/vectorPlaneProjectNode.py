import maya.api.OpenMaya as om

def maya_useNewAPI():
    pass

class VectorPlaneProjectNode(om.MPxNode):
    id = om.MTypeId(0x00000001)

    planeOrigin: om.MObject
    planeVector1: om.MObject
    planeVector2: om.MObject

    input: om.MObject
    output: om.MObject
    
    @staticmethod
    def creator():
        return VectorPlaneProjectNode()
    
    @staticmethod
    def initialize():
        nAttr: om.MFnNumericAttribute = om.MFnNumericAttribute()

        VectorPlaneProjectNode.planeOrigin = nAttr.createPoint('planeOrigin', 'pOri')
        nAttr.keyable = True
        nAttr.channelBox = True
        nAttr.storable = True
        nAttr.readable = True
        nAttr.writable = True

        VectorPlaneProjectNode.planeVector1 = nAttr.createPoint('planeVector1', 'pVec1')
        nAttr.keyable = True
        nAttr.channelBox = True
        nAttr.storable = True
        nAttr.readable = True
        nAttr.writable = True

        VectorPlaneProjectNode.planeVector2 = nAttr.createPoint('planeVector2', 'pVec2')
        nAttr.keyable = True
        nAttr.channelBox = True
        nAttr.storable = True
        nAttr.readable = True
        nAttr.writable = True

        VectorPlaneProjectNode.input = nAttr.createPoint('input', 'in')
        nAttr.keyable = True
        nAttr.channelBox = True
        nAttr.storable = True
        nAttr.readable = True
        nAttr.writable = True

        VectorPlaneProjectNode.output = nAttr.createPoint('output', 'out')
        nAttr.keyable = False
        nAttr.storable = False
        nAttr.readable = True
        nAttr.writable = False

        om.MPxNode.addAttribute(VectorPlaneProjectNode.planeOrigin)
        om.MPxNode.addAttribute(VectorPlaneProjectNode.planeVector1)
        om.MPxNode.addAttribute(VectorPlaneProjectNode.planeVector2)
        om.MPxNode.addAttribute(VectorPlaneProjectNode.input)

        om.MPxNode.addAttribute(VectorPlaneProjectNode.output)

        om.MPxNode.attributeAffects(VectorPlaneProjectNode.planeOrigin, VectorPlaneProjectNode.output)
        om.MPxNode.attributeAffects(VectorPlaneProjectNode.planeVector1, VectorPlaneProjectNode.output)
        om.MPxNode.attributeAffects(VectorPlaneProjectNode.planeVector2, VectorPlaneProjectNode.output)
        om.MPxNode.attributeAffects(VectorPlaneProjectNode.input, VectorPlaneProjectNode.output)

    def __init__(self):
        om.MPxNode.__init__(self)
 
    def compute(self, plug: om.MPlug, data: om.MDataBlock):
        if plug == VectorPlaneProjectNode.output:
            pass
        elif plug.isChild and plug.parent() == VectorPlaneProjectNode.output:
            pass
        else:
            return None
        
        pOriHandle: om.MDataHandle = data.inputValue(VectorPlaneProjectNode.planeOrigin)
        pOri: om.MFloatVector = pOriHandle.asFloatVector()
        
        pVec1Handle: om.MDataHandle = data.inputValue(VectorPlaneProjectNode.planeVector1)
        pVec1: om.MFloatVector = pVec1Handle.asFloatVector()

        pVec2Handle: om.MDataHandle = data.inputValue(VectorPlaneProjectNode.planeVector2)
        pVec2: om.MFloatVector = pVec2Handle.asFloatVector()

        inputHandle: om.MDataHandle = data.inputValue(VectorPlaneProjectNode.input)
        input: om.MFloatVector = inputHandle.asFloatVector()

        pVec1 -= pOri
        pVec2 -= pOri
        input -= pOri

        planeNormal: om.MFloatVector = (pVec1 ^ pVec2).normal()
        result: om.MFloatVector = input - (input * planeNormal) * planeNormal + pOri

        outputHandle: om.MDataHandle = data.outputValue(VectorPlaneProjectNode.output)
        outputHandle.setMFloatVector(result)
        data.setClean(plug)
 
        return self
 
def initializePlugin(obj):
    plugin: om.MFnPlugin = om.MFnPlugin(obj, 'Suyeon', '1.0', 'Any')

    try:
        plugin.registerNode('vectorPlaneProject', VectorPlaneProjectNode.id, VectorPlaneProjectNode.creator, VectorPlaneProjectNode.initialize)
    except:
        raise RuntimeError('Failed to register node')
 
def uninitializePlugin(obj):
    plugin: om.MFnPlugin = om.MFnPlugin(obj)

    try:
        plugin.deregisterNode(VectorPlaneProjectNode.id)
    except:
        raise RuntimeError('Failed to register node')