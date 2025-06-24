import bpy
from pathlib import Path
import json
import math
from preprocessing.common import get_config
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


def copy_nodes(source_nodes: bpy, target_nodes: bpy) -> dict:
    """Copy nodes from source material to target material.

    Target material must be writable
    """
    node_map = {}
    for node in source_nodes:
        # Create new node
        new_node = target_nodes.new(type=node.bl_idname)
        new_node.location = node.location
        new_node.label = node.label
        new_node.name = f"{node.name}_thermal"
        # Copy node attributes
        for attr in dir(node):
            if attr.startswith("_"):
                continue
            try:
                setattr(new_node, attr, getattr(node, attr))
            except AttributeError:
                pass  # Cover internal Blender read-only attr
        # Copy node inputs
        for i, input_socket in enumerate(node.inputs):
            if i < len(new_node.inputs):  # Ensure corresponding socket exists
                try:
                    new_socket = new_node.inputs[i]
                    if hasattr(input_socket, "default_value") and hasattr(
                        new_socket, "default_value"
                    ):
                        new_socket.default_value = input_socket.default_value
                except AttributeError:
                    pass  # Cover internal Blender read-only attr
        # Cover color ramp node case
        if node.bl_idname == "ShaderNodeValToRGB":
            src_ramp = node.color_ramp
            dst_ramp = new_node.color_ramp
            dst_ramp.interpolation = src_ramp.interpolation
            # Copy color and position
            for i, src_elem in enumerate(src_ramp.elements):
                dst_elem = dst_ramp.elements[i]
                dst_elem.position = src_elem.position
                dst_elem.color = src_elem.color
        node_map[node] = new_node
    return node_map


def copy_links(source_links: bpy, target_links: bpy, node_map: dict) -> None:
    """Copy links from source material to target material.

    Target material must be writable
    """
    for link in source_links:
        from_node = link.from_node
        to_node = link.to_node
        if from_node in node_map and to_node in node_map:
            new_from_node = node_map[from_node]
            new_to_node = node_map[to_node]
            try:
                from_socket = new_from_node.outputs[link.from_socket.identifier]
                to_socket = new_to_node.inputs[link.to_socket.identifier]
                if from_socket and to_socket:
                    target_links.new(from_socket, to_socket)
            except Exception as e:
                log.error(f"Failed to link {from_node.name} -> {to_node.name}: {e}")


def relink_material_output(nodes: bpy, links: bpy):
    """Link the node that was linked to "Material Output" to custom "Thermal Material Output" node.

    Remove obsolete "Material Output" node
    src/postprocessing/material.blend has to have custom labeled nodes as specified below
    """
    for node in nodes:
        if node.type == "OUTPUT_MATERIAL" and node.label != "Thermal Material Output":
            from_socket = node.inputs["Surface"].links[0].from_socket
            not_thermal_output_node = node
        if node.label == "Thermal Mix Shader":
            input_socket = node.inputs[1]
    links.new(from_socket, input_socket)
    nodes.remove(not_thermal_output_node)


def merge_materials(
    lib: str, lib_thermal: str, config: str, merged_material_path: str
) -> None:
    """Merge library assets material with thermal_material and save in output blend."""
    # Import materials
    lib_material_name = get_config(config)["material"]
    lib_material = import_material(lib, lib_material_name)
    thermal_material_name = "thermal_threshold"
    thermal_material = import_material(lib_thermal, thermal_material_name)
    thermal_material.use_nodes = True
    thermal_material_nodes = thermal_material.node_tree.nodes
    thermal_material_links = thermal_material.node_tree.links
    # Create new material & copy lib_material content
    merged_material = lib_material.copy()
    merged_material.use_nodes = True
    merged_material.name = "MergedMaterial"
    # Copy thermal material nodes & links
    merged_material_nodes = merged_material.node_tree.nodes
    merged_material_links = merged_material.node_tree.links
    node_map = copy_nodes(thermal_material_nodes, merged_material_nodes)
    copy_links(thermal_material_links, merged_material_links, node_map)
    relink_material_output(merged_material_nodes, merged_material_links)
    # Create dummy object
    for o in bpy.data.objects:
        bpy.data.objects.remove(o)
    mesh = bpy.data.meshes.new("DummyMesh")
    obj = bpy.data.objects.new("DummyObject", mesh)
    bpy.context.scene.collection.objects.link(obj)
    merged_material.use_fake_user = True
    # Assign output material to dummy object
    obj.data.materials.append(merged_material)
    # Save new blend with dummy object & merged material
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(
        filepath=Path(merged_material_path).resolve().as_posix()
    )


def process_blend(blend_in: str, blend_out: str, material: str, config: str) -> None:
    """Import .blend.

    Assign thermal mask material to the object
    Set location and orientation of the object
    Create custom camera with parameters from config.json
    """

    # Load .blend
    bpy.ops.wm.open_mainfile(filepath=Path(blend_in).resolve().as_posix())
    # Get material
    material_name = "MergedMaterial"
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
