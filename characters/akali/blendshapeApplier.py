import maya.cmds as cmds

mainMeshs = ['Face_Mesh', 'Eyelash_Mesh', 'Eyebrow_Mesh', 'Teeth2_Mesh', 'Tongue_Mesh', 'Corneas_Mesh', 'Eyes_Mesh']

for mainMesh in mainMeshs:
    blsh = mainMesh.split('_')[0].lower() + '_arkit52'
    cmds.blendShape(mainMesh, name=blsh, frontOfChain=True)

    targets = cmds.listRelatives(f'akali_facial_arkit52:{mainMesh}_ARKit')

    for i in range(len(targets)):
        target = targets[i]
        targetName = target.rsplit('_', 1)[-1]

        cmds.blendShape(
            blsh,
            edit=True,
            topologyCheck=True,
            target=(mainMesh, i, target, 1),
            weight=(0, 0)
        )

        cmds.aliasAttr(targetName, f'{blsh}.w[{i}]')
