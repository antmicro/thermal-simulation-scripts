from paraview.simple import *

output_path = "x3d/"  # X3D output files

paraview.simple._DisableFirstRenderCameraReset()
scene = GetAnimationScene()

scene_count = int(scene.EndTime) + 1

for scene_id in scene_count:
    print(f"Exporting {scene_id} of {scene_count}")
    scene.AnimationTime = scene_id

    source = GetActiveSource()
    view = GetActiveViewOrCreate("RenderView")

    display = GetDisplayProperties(source, view=view)
    ExportView(f"{output_path}{i:04d}.x3d", view=view)

print("DONE")
