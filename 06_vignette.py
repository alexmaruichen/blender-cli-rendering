# blender --background --python 06_vignette.py -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.getcwd())

import utils


def set_principled_node_as_rough_blue(principled_node):
    utils.set_principled_node(
        principled_node=principled_node,
        base_color=(0.1, 0.2, 0.6, 1.0),
        metallic=0.5,
        specular=0.5,
        roughness=0.9,
    )


def set_principled_node_as_ceramic(principled_node):
    utils.set_principled_node(
        principled_node=principled_node,
        base_color=(0.8, 0.8, 0.8, 1.0),
        subsurface=0.1,
        subsurface_color=(0.9, 0.9, 0.9, 1.0),
        subsurface_radius=(1.0, 1.0, 1.0),
        metallic=0.2,
        specular=0.5,
        roughness=0.0,
    )


def set_principled_node_as_gold(principled_node):
    utils.set_principled_node(
        principled_node=principled_node,
        base_color=(1.00, 0.75, 0.35, 1.0),
        metallic=1.0,
        specular=0.5,
        roughness=0.0,
    )


def set_principled_node_as_glass(principled_node):
    utils.set_principled_node(principled_node=principled_node,
                              base_color=(0.92, 0.92, 0.95, 1.0),
                              metallic=0.0,
                              specular=0.5,
                              roughness=0.0,
                              clearcoat=0.5,
                              clearcoat_roughness=0.030,
                              ior=1.45,
                              transmission=1.0)


def set_scene_objects():
    bpy.ops.mesh.primitive_monkey_add(location=(-3.0, 0.0, 1.0))
    current_object = bpy.context.object
    current_object.name = "Suzanne_Left"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 3)
    mat = bpy.data.materials.new("Material_Left")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    utils.clean_nodes(nodes)
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    set_principled_node_as_glass(principled_node)
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 1.0))
    current_object = bpy.context.object
    current_object.name = "Suzanne_Center"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 3)
    mat = bpy.data.materials.new("Material_Center")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    utils.clean_nodes(nodes)
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    set_principled_node_as_gold(principled_node)
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_monkey_add(location=(+3.0, 0.0, 1.0))
    current_object = bpy.context.object
    current_object.name = "Suzanne_Right"
    utils.set_smooth_shading(current_object)
    utils.add_subdivision_surface_modifier(current_object, 3)
    mat = bpy.data.materials.new("Material_Right")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    utils.clean_nodes(nodes)
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    set_principled_node_as_rough_blue(principled_node)
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    current_object.data.materials.append(mat)

    bpy.ops.mesh.primitive_plane_add(radius=10.0)
    current_object = bpy.context.object
    current_object.name = "Floor"
    mat = bpy.data.materials.new("Material_Plane")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    utils.clean_nodes(nodes)
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    set_principled_node_as_ceramic(principled_node)
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    current_object.data.materials.append(mat)

    bpy.ops.object.empty_add(location=(0.0, -0.75, 1.0))
    focus_target = bpy.context.object
    return focus_target


def set_camera_params(camera, dof_target):
    camera.data.sensor_fit = 'HORIZONTAL'
    camera.data.sensor_width = 36.0
    camera.data.sensor_height = 24.0
    camera.data.lens = 50
    camera.data.dof_object = dof_target
    camera.data.cycles.aperture_type = 'RADIUS'
    camera.data.cycles.aperture_size = 0.180
    camera.data.cycles.aperture_blades = 6


def define_vignette_node():
    group = bpy.data.node_groups.new(type="CompositorNodeTree",
                                     name="Vignette")

    input_node = group.nodes.new("NodeGroupInput")
    group.inputs.new("NodeSocketColor", "Image")
    group.inputs.new("NodeSocketFloat", "Amount")
    group.inputs["Amount"].default_value = 0.5
    group.inputs["Amount"].min_value = 0.0
    group.inputs["Amount"].max_value = 1.0

    lens_distortion_node = group.nodes.new(type="CompositorNodeLensdist")
    lens_distortion_node.inputs["Distort"].default_value = 1.000

    separate_rgba_node = group.nodes.new(type="CompositorNodeSepRGBA")

    blur_node = group.nodes.new(type="CompositorNodeBlur")
    blur_node.filter_type = 'GAUSS'
    blur_node.size_x = 300
    blur_node.size_y = 300
    blur_node.use_extended_bounds = True

    mix_node = group.nodes.new(type="CompositorNodeMixRGB")
    mix_node.blend_type = 'MULTIPLY'

    output_node = group.nodes.new("NodeGroupOutput")
    group.outputs.new("NodeSocketColor", "Image")

    group.links.new(input_node.outputs["Amount"], mix_node.inputs["Fac"])
    group.links.new(input_node.outputs["Image"], mix_node.inputs[1])
    group.links.new(input_node.outputs["Image"],
                    lens_distortion_node.inputs["Image"])
    group.links.new(lens_distortion_node.outputs["Image"],
                    separate_rgba_node.inputs["Image"])
    group.links.new(separate_rgba_node.outputs["A"], blur_node.inputs["Image"])
    group.links.new(blur_node.outputs["Image"], mix_node.inputs[2])
    group.links.new(mix_node.outputs["Image"], output_node.inputs["Image"])

    utils.arrange_nodes(group)


def add_vignette_node(node_tree):
    define_vignette_node()

    vignette_node = node_tree.nodes.new(type='CompositorNodeGroup')
    vignette_node.name = "Vignette"
    vignette_node.node_tree = bpy.data.node_groups['Vignette']

    return vignette_node


def build_scene_composition(scene):
    scene.use_nodes = True
    utils.clean_nodes(scene.node_tree.nodes)

    render_layer_node = scene.node_tree.nodes.new(type="CompositorNodeRLayers")

    vignette_node = add_vignette_node(scene.node_tree)

    lens_distortion_node = scene.node_tree.nodes.new(
        type="CompositorNodeLensdist")
    lens_distortion_node.inputs["Distort"].default_value = -0.050
    lens_distortion_node.inputs["Dispersion"].default_value = 0.050

    color_correction_node = scene.node_tree.nodes.new(
        type="CompositorNodeColorCorrection")
    color_correction_node.master_saturation = 1.10
    color_correction_node.master_gain = 1.10

    glare_node = scene.node_tree.nodes.new(type="CompositorNodeGlare")
    glare_node.glare_type = 'FOG_GLOW'
    glare_node.quality = 'HIGH'

    composite_node = scene.node_tree.nodes.new(type="CompositorNodeComposite")

    scene.node_tree.links.new(render_layer_node.outputs['Image'],
                              vignette_node.inputs['Image'])
    scene.node_tree.links.new(vignette_node.outputs['Image'],
                              lens_distortion_node.inputs['Image'])
    scene.node_tree.links.new(lens_distortion_node.outputs['Image'],
                              color_correction_node.inputs['Image'])
    scene.node_tree.links.new(color_correction_node.outputs['Image'],
                              glare_node.inputs['Image'])
    scene.node_tree.links.new(glare_node.outputs['Image'],
                              composite_node.inputs['Image'])

    utils.arrange_nodes(scene.node_tree)


# Args
output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])
num_samples = int(sys.argv[sys.argv.index('--') + 3])

# Parameters
hdri_path = "./assets/HDRIs/green_point_park_2k.hdr"

# Scene Building
scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset
utils.clean_objects()

## Suzannes
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(view_align=False, location=[0.0, -15.0, 2.0])
camera = bpy.context.object

utils.add_track_to_constraint(camera, focus_target)
set_camera_params(camera, focus_target)

## Lights
utils.build_environmental_light(world, hdri_path)

## Composition
build_scene_composition(scene)

# Render Setting
utils.set_cycles_renderer(scene,
                          resolution_percentage,
                          output_file_path,
                          camera,
                          num_samples,
                          use_denoising=True)

# Render
bpy.ops.render.render(animation=False, write_still=True)
