import bpy
import numpy as np
import torch
from pathlib import Path
from bl_ext.blender_org.modular_tree.python_classes.resources.node_groups import distribute_leaves

from . import pointnet2
from . import utils
from . import constants

class_names = [
    "CYLINDRICAL",
    "CONICAL",
    "SPHERICAL",
    "HEMISPHERICAL",
    "TAPERED_CYLINDRICAL",
    "INVERSE_CONICAL",
    "TEND_FLAME",
]

def inference():
    obj = bpy.context.active_object
    if obj:
        if obj.type == "MESH":
            if len(obj.data.vertices) > 0 and len(obj.data.edges) == 0 and len(obj.data.polygons) == 0:
                num_points = len(obj.data.vertices)
                
                # extract points
                point_cloud = np.array([obj.matrix_world @ v.co for v in obj.data.vertices], dtype=np.float32)
                
                point_cloud = point_cloud.reshape((num_points, 3))
                point_cloud[:, :] = point_cloud[:, [1, 2, 0]]
                
                # sample 2048 points
                """
                if num_points >= 2048:
                    idx = np.random.choice(num_points, 2048, replace=False)
                else:
                    idx = np.random.choice(num_points, 2048, replace=True)

                point_cloud = point_cloud[idx]
                """
                # center the points
                point_cloud = point_cloud - point_cloud.mean(axis=0)
                
                # transpose point cloud
                point_cloud = torch.from_numpy(point_cloud).transpose(0, 1)
                
                # add batch dimension
                point_cloud = torch.unsqueeze(point_cloud, dim=0)
                
                mean_path = Path(__file__).parent.joinpath("mean.npy")
                std_path = Path(__file__).parent.joinpath("std.npy")

                mean = np.load(mean_path).astype(np.float32)
                std = np.load(std_path).astype(np.float32)

                output = calculate_parameters(point_cloud)
                
                pred_class = output["classification"].argmax(dim=1).item()
                pred_values = output["regression"].squeeze().numpy() * std + mean
                
                parameters = {
                    "trunk" : {
                        "Seed": 0,
                        "Length": pred_values[0],
                        "Start Radius": pred_values[1],
                    },
                    "branches1" : {
                        "Seed": 0,
                        "Length": pred_values[2],
                        "Density": pred_values[3],
                        "Up Attraction": pred_values[4],
                        "crown_shape": class_names[pred_class],
                    },
                }
                return parameters
                
            else:
                print("Not a point cloud")
        else:
            print("Invalid object type")
    else:
        print("No object selected")

def calculate_parameters(point_cloud):
    device = torch.device("cpu")
    
    model = pointnet2.PointNet2()
    
    checkpoint_path = Path(__file__).parent.joinpath("model.pth")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])

    model.to(device)
    
    model.eval()
    
    with torch.no_grad():
        output = model(point_cloud)
    
    return output

def create_tree_from_parameters(parameters):
    
    point_cloud = bpy.context.active_object
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
    
    tree_node_tree = bpy.data.node_groups.new(name = "Mtree", type = "mt_MtreeNodeTree")
    all_tree_nodes = utils.create_node_tree_setup(tree_node_tree, constants.tree_nodes_to_add, constants.tree_links_to_add)
    existing_objects = set(bpy.data.objects)
    all_tree_nodes["treeMesher"].build_tree()
    new_objects = set(bpy.data.objects) - existing_objects
    tree = next(obj for obj in new_objects if obj.type == 'MESH')
    tree.location = point_cloud.location.copy()
    tree.location.z -= 50
    
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
        
    # leaf.hide_viewport = True
    
    
    
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
    utils.assign_tree_node_values(all_tree_nodes, parameters)
    all_tree_nodes["treeMesher"].build_tree()
    
    
    tree_copy = tree.copy()
    tree_copy.data = tree.data.copy()
    bpy.context.collection.objects.link(tree_copy)
    tree_copy.name = f"estimated tree ({point_cloud.name})"
    
    bpy.context.view_layer.objects.active = tree_copy
    tree_copy.select_set(True)
    bpy.ops.object.modifier_apply(modifier="leaves")
    
    for ng in list(bpy.data.node_groups):
        bpy.data.node_groups.remove(ng)
    
    bpy.data.objects.remove(tree, do_unlink=True)
    bpy.data.objects.remove(leaf, do_unlink=True)
    
    
    
    
    for coll in tree_copy.users_collection:
        coll.objects.unlink(tree_copy)
    
    for coll in point_cloud.users_collection:
        coll.objects.link(tree_copy)
    