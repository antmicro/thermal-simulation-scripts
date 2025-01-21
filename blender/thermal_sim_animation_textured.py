import os
import bpy
import time
import math
from mathutils import Euler

# Inputs
x3d_path = r"/home/ant/Workspace/FEM_tests/rpi_blend"
output_path = r"/home/ant/Workspace/FEM_tests/blend_out"
use_paraview_camera = True

if not os.path.isdir(output_path):
    os.makedirs(output_path)

# List x3d files
files = os.listdir(x3d_path)
x3d_files = [file for file in files if file.endswith("x3d")]
x3d_files.sort(key=lambda x: "{0:0>8}".format(x).lower())

x3d_files = x3d_files[76:230]
for file in x3d_files:
    print(f"Loading file {file}")

    bpy.ops.import_scene.x3d(filepath=f"{x3d_path}/{file}")

    lights = [object for object in bpy.data.objects if "light" in object.name.lower()]
    for light in lights:

        if (light.name != "Light_array") and (light.name != "Light_Force"):
            bpy.data.objects.remove(light)

    cameras = [
        object for object in bpy.data.objects if "viewpoint" in object.name.lower()
    ]
    for camera in cameras:
        bpy.data.objects.remove(camera)

    shape = bpy.data.objects["Shape_IndexedFaceSet"]
    shape.name = "Frame"
    shape = bpy.data.objects["Frame"]

    shape.data.materials.clear()
    shape.data.materials.append(bpy.data.materials["FixedShading"])
    shape.rotation_euler = Euler((2.593, 1.559, 0.857), "XYZ")

    # Render
    filename = file.replace("x3d", "png")
    bpy.ops.render.render()

    # Save render image
    filepath = f"{output_path}/{filename}"
    bpy.data.images["Render Result"].save_render(filepath=filepath)

    time.sleep(1)
    bpy.data.objects.remove(shape)
    time.sleep(1)

print("DONE")
