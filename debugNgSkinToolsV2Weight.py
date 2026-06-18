from ngSkinTools2.api import Layers, NamedPaintTarget
import maya.cmds as cmds

def calculateFinalWeight(mesh, vertexIndex):
    skinCluster = cmds.ls(cmds.listHistory(mesh), type='skinCluster')[0]
    layersObj = Layers(skinCluster)
    influences = layersObj.list_influences()
    infIndexToName = {i: inf.path.split("|")[-1] for i, inf in enumerate(influences)}
    allLayers = layersObj.list()

    def getMask(layer):
        maskWeights = layer.get_weights(NamedPaintTarget.MASK)
        return maskWeights[vertexIndex] if maskWeights else 1.0

    def getInfluenceWeights(layer):
        result = {}
        for i, name in infIndexToName.items():
            try:
                wList = layer.get_weights(i)
                if wList and len(wList) > vertexIndex:
                    w = wList[vertexIndex]
                    if w > 0.0001:
                        result[name] = w
            except:
                pass
        return result

    def sumChildren(children, indent=0):
        """
        자식 레이어들을 단순 합산 (remaining 없음)
        각 자식의 기여 = 자신의 웨이트 × 자신의 mask × opacity
        """
        pad = "  " * indent
        total = {}

        for layer in children:
            if not layer.enabled:
                print(f"{pad}[ {layer.name} ] SKIP (disabled)")
                continue

            mask = getMask(layer)
            opacity = layer.opacity

            if layer.children:
                print(f"{pad}[ {layer.name} ] mask={mask:.4f} → 자식 합산:")
                childSum = sumChildren(layer.children, indent + 1)
            else:
                childSum = getInfluenceWeights(layer)

            for joint, w in childSum.items():
                contribution = w * mask * opacity
                total[joint] = total.get(joint, 0) + contribution
                print(f"{pad}  {joint}: {w:.4f} × mask{mask:.4f} = {contribution:.6f}")

        return total

    def mergeRootLayers(rootLayers, indent=0):
        """
        최상위 레이어들은 remaining 방식으로 합산
        """
        pad = "  " * indent
        remaining = 1.0
        final = {}

        for layer in rootLayers:
            if not layer.enabled:
                print(f"{pad}[ {layer.name} ] SKIP (disabled)")
                continue

            mask = getMask(layer)
            opacity = layer.opacity

            if layer.children:
                print(f"\n{pad}[ {layer.name} ] mask={mask:.4f} → 자식 합산:")
                layerWeights = sumChildren(layer.children, indent + 1)
            else:
                layerWeights = getInfluenceWeights(layer)

            layerSum = sum(layerWeights.values())
            effective = layerSum * mask * opacity

            print(f"\n{pad}[ {layer.name} ] 남은공간={remaining:.4f} | "
                  f"합={layerSum:.4f} × mask{mask:.4f} × opacity{opacity:.4f} = {effective:.4f}")

            for joint, w in layerWeights.items():
                contribution = w * mask * opacity * remaining
                final[joint] = final.get(joint, 0) + contribution
                print(f"{pad}  {joint}: {w:.4f} → 실제기여 {contribution:.6f}")

            remaining -= effective * remaining
            print(f"{pad}  처리 후 남은공간: {remaining:.4f}")

        return final

    rootLayers = list(reversed([l for l in allLayers if l.parent is None]))

    print(f"\n=== 버텍스 {vertexIndex} 계산 ===")
    print(f"루트 순서: {[l.name for l in rootLayers]}\n")

    final = mergeRootLayers(rootLayers)

    print("\n=== 시뮬레이션 최종 웨이트 ===")
    total = 0
    for joint, w in sorted(final.items(), key=lambda x: -x[1]):
        if w > 0.0001:
            print(f"  {joint}: {w:.6f}")
            total += w
    print(f"  합계: {total:.6f}")

    print("\n=== Maya 실제값 ===")
    infs = cmds.skinCluster(skinCluster, q=True, influence=True)
    weights = cmds.skinPercent(skinCluster, f"{mesh}.vtx[{vertexIndex}]", q=True, value=True)
    for inf, w in zip(infs, weights):
        if w > 0.0001:
            print(f"  {inf}: {w:.6f}")