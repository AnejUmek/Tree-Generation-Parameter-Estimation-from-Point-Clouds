import bpy
from bl_ext.blender_org.modular_tree.python_classes.resources.node_groups import distribute_leaves
from pathlib import Path
import json
import time

from . import utils
from . import constants

def create_point_cloud():
    """
    mat_tree = bpy.data.materials.new("tree_material")
    mat_tree.use_nodes = True
    bsdf_tree = mat_tree.node_tree.nodes.get("Principled BSDF")
    bsdf_tree.inputs["Base Color"].default_value = (0.2, 0.10, 0.0, 1.0)
    
    mat_leaf = bpy.data.materials.new("leaf_material")
    mat_leaf.use_nodes = True
    bsdf_leaf = mat_leaf.node_tree.nodes.get("Principled BSDF")
    bsdf_leaf.inputs["Base Color"].default_value = (0.10, 0.5, 0.05, 1.0)
    """
    
    # CREATE POINT CLOUD USING GEOMETRY NODES
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=bpy.context.scene.cursor.location, scale=(1, 1, 1))
    
    point_cloud = bpy.data.objects["Cube"]
    point_cloud.name = "LIDAR point cloud"
    point_cloud.location.z += 50

    bpy.ops.node.new_geometry_nodes_modifier()
    node_tree = bpy.data.node_groups["Geometry Nodes"]
    
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)

    all_nodes = utils.create_node_tree_setup(node_tree, constants.nodes_to_add, constants.links_to_add)
    
    # CREATE TREE USING MODULAR TREE
    tree_node_tree = bpy.data.node_groups.new(name = "Mtree", type = "mt_MtreeNodeTree")

    all_tree_nodes = utils.create_node_tree_setup(tree_node_tree, constants.tree_nodes_to_add, constants.tree_links_to_add)
    
    existing_objects = set(bpy.data.objects)

    all_tree_nodes["treeMesher"].build_tree()

    new_objects = set(bpy.data.objects) - existing_objects

    tree = next(obj for obj in new_objects if obj.type == 'MESH')
    tree.location = bpy.context.scene.cursor.location.copy()
    
    all_nodes["objectInfo"].inputs["Object"].default_value = tree
    
    
    # CREATE LEAF AND ADD IT TO THE TREE
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=bpy.context.scene.cursor.location, scale=(1, 1, 1))

    leaf = bpy.data.objects["Plane"]
    leaf.name = "leaf"
    
    """
    if tree.data.materials:
        tree.data.materials[0] = mat_tree
    else:
        tree.data.materials.append(mat_tree)
        
    if leaf.data.materials:
        leaf.data.materials[0] = mat_leaf
    else:
        leaf.data.materials.append(mat_leaf)
    """
    #leaf.hide_viewport = True
    
    distribute_leaves(
        tree,
        leaf_object=leaf,
        density = 100,
        scale = 0.2,
        max_radius = 0.03)
    
    leaves_modifier = tree.modifiers["leaves"]
    # Scale Variation = 0
    leaves_modifier["Socket_4"] = 0.0
    # LOD 1 Distance = 50
    leaves_modifier["Socket_11"] = 50.0
    
    # SET TREE PARAMETER VALUES
    utils.assign_tree_node_values(all_tree_nodes, constants.tree_nodes_non_changing_parameters)
    tree_nodes_changing_parameters = utils.create_random_tree_changing_parameters()
    
    utils.assign_tree_node_values(all_tree_nodes, tree_nodes_changing_parameters)

    all_tree_nodes["treeMesher"].build_tree()
    
    tree_copy = tree.copy()
    tree_copy.data = tree.data.copy()
    bpy.context.collection.objects.link(tree_copy)
    tree_name = str(tree.name)
    
    bpy.context.view_layer.objects.active = tree_copy
    tree_copy.select_set(True)
    bpy.ops.object.modifier_apply(modifier="leaves")
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = point_cloud
    point_cloud.select_set(True)
    bpy.ops.object.modifier_apply(modifier="GeometryNodes")

    for ng in list(bpy.data.node_groups):
        bpy.data.node_groups.remove(ng)
    
    bpy.data.objects.remove(tree, do_unlink=True)
    bpy.data.objects.remove(leaf, do_unlink=True)
    
    tree_copy.name = tree_name
    
    # CREATE COLLECTION AND ADD OBJECTS TO IT
    coll_names = [c.name for c in bpy.data.collections]
    i = 1
    coll_new_name = f"Tree Collection {i}"
    while coll_new_name in coll_names:
        i += 1
        coll_new_name = f"Tree Collection {i}"
    
    coll_new = bpy.data.collections.new(coll_new_name)
    bpy.context.scene.collection.children.link(coll_new)

    all_objects = [point_cloud, tree_copy]
    for obj in all_objects:
        for coll in obj.users_collection:
            coll.objects.unlink(obj)
        coll_new.objects.link(obj)
    
    return tree_nodes_changing_parameters