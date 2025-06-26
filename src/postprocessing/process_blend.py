import bpy
from pathlib import Path
import json
import math
import logging

log = logging.getLogger(__name__)


def preview_camera(gltf_path: Path, blend_path: Path) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=Path(gltf_path).resolve().as_posix())

    # Fix orientation for all imported objects
    for obj in bpy.data.objects:
        obj.name = "Shape_IndexedFaceSet"
        if obj.type != "MESH":
            continue
        # Align rotation from freecad to paraview mode
        obj.rotation_mode = "XYZ"
        obj.scale = (1000.0, 1000.0, 1000.0)  # Scale
        obj.rotation_euler[0] += math.radians(90)
        center_object(obj)

    # Add camera
    cam_data = bpy.data.cameras.new(name="camera_custom")
    cam_obj = bpy.data.objects.new("camera_custom", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_data.clip_start = 0.1
    cam_data.clip_end = 15000
    cam_data.dof.use_dof = False
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=Path(blend_path).resolve().as_posix())


def get_camera_parameters(config_path: str) -> tuple:
    """Get custom camera properties from config."""
    with open(Path(config_path).resolve().as_posix(), "r") as file:
        config_data: dict = json.load(file)
    location = config_data["camera_custom"]["location"]
    rotation = config_data["camera_custom"]["rotation"]
    focal_length = config_data["camera_custom"]["focal_length"]
    sensor_width = config_data["camera_custom"]["sensor_width"]
    return location, rotation, focal_length, sensor_width


def center_object(obj: bpy):
    """Set object origin to geometry.

    Set location to start of coordinate system
    Align object longest dimension to X axis
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="BOUNDS")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.rotation_mode = "XYZ"
    obj.location = (0, 0, 0)
    if obj.dimensions.x < obj.dimensions.y:
        obj.rotation_euler.rotate_axis("Z", math.radians(-90))
    if obj.dimensions.x < obj.dimensions.z:
        obj.rotation_euler.rotate_axis("Y", math.radians(-90))


def save_camera_properties(blend: str, config: str) -> None:
    """Save camera_custom parameters from blend to config."""
    with open(Path(config).resolve().as_posix(), "r") as file:
        config_data = json.load(file)
    bpy.ops.wm.open_mainfile(filepath=Path(blend).resolve().as_posix())
    bpy.context.preferences.filepaths.save_version = 0
    for obj in bpy.data.objects:
        if obj.name != "camera_custom":
            continue
        location = []
        rotation = []
        location.append(obj.location[0])
        location.append(obj.location[1])
        location.append(obj.location[2])
        rotation.append(obj.rotation_euler[0])
        rotation.append(obj.rotation_euler[1])
        rotation.append(obj.rotation_euler[2])
        sensor_width = bpy.data.cameras["camera_custom"].sensor_width
        focal_length = bpy.data.cameras["camera_custom"].lens
    config_data["camera_custom"]["location"] = location
    config_data["camera_custom"]["rotation"] = rotation
    config_data["camera_custom"]["focal_length"] = focal_length
    config_data["camera_custom"]["sensor_width"] = sensor_width
    with open(Path(config).resolve().as_posix(), "w") as file:
        json.dump(config_data, file, indent=4)


def import_material(blend: str, material_name: str) -> bpy:
    """Import material with given name from blend."""
    with bpy.data.libraries.load(Path(blend).resolve().as_posix(), link=False) as (
        data_from,
        data_to,
    ):
        if material_name in data_from.materials:
            data_to.materials.append(material_name)
        else:
            log.error(f"Material {material_name} not found in {blend}")
            log.info(f"Available materials: {data_from.materials}")
    return bpy.data.materials.get(material_name)


def process_blend(blend_in: str, blend_out: str, material: str, config: str) -> None:
    """Import .blend.

    Assign thermal mask material to the object
    Set location and orientation of the object
    Create custom camera with parameters from config.json
    """

    # Load .blend
    bpy.ops.wm.open_mainfile(filepath=Path(blend_in).resolve().as_posix())
    # Get material
    material_name = "thermal_threshold"
    material = import_material(material, material_name)
    # Color shape
    shape = bpy.data.objects["mesh0"]
    center_object(shape)
    shape.data.materials.clear()
    shape.data.materials.append(material)
    # Get custom camera parameters if provided in config
    location, rotation, focal_length, sensor_width = get_camera_parameters(config)
    # Add custom camera
    cam_data = bpy.data.cameras.new(name="camera_custom")
    cam_obj = bpy.data.objects.new("camera_custom", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (location[0], location[1], location[2])
    cam_obj.rotation_mode = "XYZ"
    cam_obj.rotation_euler = (
        rotation[0],
        rotation[1],
        rotation[2],
    )
    cam_data.lens = focal_length
    cam_data.sensor_width = sensor_width
    cam_data.clip_start = 0.1
    cam_data.clip_end = 15000
    cam_data.dof.use_dof = False
    # Save blend file
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=Path(blend_out).resolve().as_posix())


def gltf_to_blend(gltf_path: str, blend_path: str) -> None:
    """Convert .gltf to .blend."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=Path(gltf_path).resolve().as_posix())
    # Clear objects except mesh
    for obj in bpy.data.objects:
        if obj.name != "mesh0":
            bpy.data.objects.remove(obj)
            continue
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=Path(blend_path).resolve().as_posix())
