import maya.cmds as cmds

allShapes = [
    'eyeBlinkLeft', 'eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft', 'eyeSquintLeft', 'eyeWideLeft', 'eyeBlinkRight', 'eyeLookDownRight', 'eyeLookInRight', 'eyeLookOutRight', 'eyeLookUpRight', 'eyeSquintRight', 'eyeWideRight', 
    'jawForward', 'jawLeft', 'jawRight', 'jawOpen', 
    'mouthClose', 'mouthFunnel', 'mouthPucker', 'mouthLeft', 'mouthRight', 'mouthSmileLeft', 'mouthSmileRight', 'mouthFrownLeft', 'mouthFrownRight', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthStretchLeft', 'mouthStretchRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower', 'mouthShrugUpper', 'mouthPressLeft', 'mouthPressRight', 'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthUpperUpLeft', 'mouthUpperUpRight',
    'browDownLeft', 'browDownRight', 'browInnerUp', 'browOuterUpLeft', 'browOuterUpRight', 
    'cheekPuff', 'cheekSquintLeft', 'cheekSquintRight', 
    'noseSneerLeft', 'noseSneerRight', 
    'tongueOut'
]

meshs = [
    [
        'Face_Main_Mesh', 
        [
            'eyeBlinkLeft', 'eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft', 'eyeSquintLeft', 'eyeWideLeft', 'eyeBlinkRight', 'eyeLookDownRight', 'eyeLookInRight', 'eyeLookOutRight', 'eyeLookUpRight', 'eyeSquintRight', 'eyeWideRight', 
            'jawForward', 'jawLeft', 'jawRight', 'jawOpen', 
            'mouthClose', 'mouthFunnel', 'mouthPucker', 'mouthLeft', 'mouthRight', 'mouthSmileLeft', 'mouthSmileRight', 'mouthFrownLeft', 'mouthFrownRight', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthStretchLeft', 'mouthStretchRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower', 'mouthShrugUpper', 'mouthPressLeft', 'mouthPressRight', 'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthUpperUpLeft', 'mouthUpperUpRight',
            'browDownLeft', 'browDownRight', 'browInnerUp', 'browOuterUpLeft', 'browOuterUpRight', 
            'cheekPuff', 'cheekSquintLeft', 'cheekSquintRight', 
            'noseSneerLeft', 'noseSneerRight', 
            'tongueOut'
        ]
    ],
    [
        'Eyelash_Main_Mesh',
        [
            'eyeBlinkLeft', 'eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft', 'eyeSquintLeft', 'eyeWideLeft', 'eyeBlinkRight', 'eyeLookDownRight', 'eyeLookInRight', 'eyeLookOutRight', 'eyeLookUpRight', 'eyeSquintRight', 'eyeWideRight', 
            'cheekSquintLeft', 'cheekSquintRight'
        ]
    ],
    [
        'Eyebrow_Main_Mesh',
        [
            'eyeSquintLeft', 'eyeSquintRight',
            'browDownLeft', 'browDownRight', 'browInnerUp', 'browOuterUpLeft', 'browOuterUpRight', 
            'cheekSquintLeft', 'cheekSquintRight'
        ]
    ],
    [
        'Teeth2_Mesh',
        [
            'jawForward', 'jawLeft', 'jawRight', 'jawOpen'
        ]
    ],
    [   
        'Tongue_Mesh',
        [ 
            'jawForward', 'jawLeft', 'jawRight', 'jawOpen',
            'tongueOut'
        ]
    ],
    [
        'Corneas_Mesh',
        ['eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft', 'eyeLookDownRight', 'eyeLookInRight', 'eyeLookOutRight', 'eyeLookUpRight']
    ],
    [
        'Eyes_Mesh',
        ['eyeLookDownLeft', 'eyeLookInLeft', 'eyeLookOutLeft', 'eyeLookUpLeft', 'eyeLookDownRight', 'eyeLookInRight', 'eyeLookOutRight', 'eyeLookUpRight']
    ]
]
grps = ['Face_Mesh', 'Eyelash_Mesh', 'Eyebrow_Mesh', 'Teeth2_Mesh', 'Tongue_Mesh', 'Corneas_Mesh', 'Eyes_Mesh']

topGrp = cmds.group(empty=True, name='akali_facial_arkit52')

for i in range(len(meshs)):
    grp = grps[i] + '_ARKit'
    cmds.group(empty=True, name=grp)
    cmds.parent(grp, topGrp)

    mesh = meshs[i][0]
    mesh_shapes = meshs[i][1]

    isFirst = True
    for shape in mesh_shapes:
        cmds.setAttr(f"ctrlARKit_M.{shape}", 10)
        name = f"{mesh}_{shape}"
        cmds.duplicate(mesh, name=name)
        cmds.parent(name, grp)
        cmds.move(15 * allShapes.index(shape), 0, 0, name)
        cmds.setAttr(f"ctrlARKit_M.{shape}", 0)

    cmds.move(15, 0, 0, grp)