import bpy
from bl_ext.blender_org.modular_tree.python_classes.resources.node_groups import distribute_leaves
from pathlib import Path
import json

utils = bpy.data.texts["utils.py"].as_module()
constants = bpy.data.texts["constants.py"].as_module()

# REMOVE EVERYTHING FROM THE SCENE
if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
    bpy.ops.object.editmode_toggle()

for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

bpy.ops.object.select_all(action = "SELECT")
bpy.ops.object.delete()

print("OBJECTS")
print(list(bpy.data.objects))

bpy.ops.outliner.orphans_purge(do_recursive = True)

for name in [col.name for col in bpy.data.collections]:
    bpy.data.collections.remove(bpy.data.collections[name])

# CREATE POINT CLOUD USING GEOMETRY NODES
bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

point_cloud = bpy.data.objects["Cube"]
point_cloud.name = "LIDAR point cloud"
point_cloud.location.z = 50

bpy.ops.node.new_geometry_nodes_modifier()
node_tree = bpy.data.node_groups["Geometry Nodes"]

for node in node_tree.nodes:
    node_tree.nodes.remove(node)

all_nodes = utils.create_node_tree_setup(node_tree, constants.nodes_to_add, constants.links_to_add)

# CREATE TREE USING MODULAR TREE
tree_node_tree = bpy.data.node_groups.new(name = "Mtree", type = "mt_MtreeNodeTree")

all_tree_nodes = utils.create_node_tree_setup(tree_node_tree, constants.tree_nodes_to_add, constants.tree_links_to_add)

all_tree_nodes["treeMesher"].build_tree()

tree = bpy.data.objects["tree"]

all_nodes["objectInfo"].inputs["Object"].default_value = tree

# CREATE LEAF AND ADD IT TO THE TREE
bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

leaf = bpy.data.objects["Plane"]
leaf.name = "leaf"
leaf.hide_viewport = True

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

# SET TREE NON-CHANGING VALUES VALUES
utils.assign_tree_node_values(all_tree_nodes, constants.tree_nodes_non_changing_parameters)

# CREATE FOLDER IF THEY DON'T EXIST
dataset_folder = Path(__file__).parent.parent.parent.joinpath(constants.dataset_folder_name)
point_cloud_folder = Path.joinpath(dataset_folder, constants.point_clouds_folder_name)
mesh_folder = Path.joinpath(dataset_folder, constants.meshes_folder_name)
parameters_folder = Path.joinpath(dataset_folder, constants.parameters_folder_name)
#for folder in [dataset_folder, point_cloud_folder, mesh_folder, parameters_folder]:
for folder in [dataset_folder, point_cloud_folder, parameters_folder]:
    if not folder.exists():
        folder.mkdir()

point_cloud_filenames = [str(path) for path in list(Path.iterdir(point_cloud_folder))]

offset = 0
if len(point_cloud_filenames) >= 1:
    offset = max([int(filename[-10:-4]) for filename in point_cloud_filenames])

# CREATE DIFFERENT TREES AND SAVE THEM
number_of_trees = 1
for i in range(number_of_trees):
    point_cloud_filename = str(point_cloud_folder.joinpath(f"pc{str(i + 1 + offset).zfill(6)}.ply"))
    #mesh_filename = str(mesh_folder.joinpath(f"mesh{str(i + 1).zfill(6)}.ply"))
    parameters_filename = str(parameters_folder.joinpath(f"params{str(i + 1 + offset).zfill(6)}.json"))
    
    tree_nodes_changing_parameters = utils.create_random_tree_changing_parameters()
    utils.assign_tree_node_values(all_tree_nodes, tree_nodes_changing_parameters)
    
    all_tree_nodes["treeMesher"].build_tree()
    
    bpy.ops.object.select_all(action='DESELECT')
    point_cloud.select_set(True)
    bpy.context.view_layer.objects.active = point_cloud

    bpy.ops.wm.ply_export(
        filepath = point_cloud_filename,
        check_existing = True,
        forward_axis = "X",
        up_axis = "Y",
        apply_modifiers = True,
        export_selected_objects = True,
        export_uv = False,
        export_normals = False,
        export_colors = "NONE",
        export_attributes = False,
        export_triangulated_mesh = False,
        ascii_format = False)

    """
    bpy.ops.object.select_all(action='DESELECT')
    tree.select_set(True)
    bpy.context.view_layer.objects.active = tree

    bpy.ops.wm.ply_export(
        filepath = mesh_filename,
        check_existing = True,
        forward_axis = "X",
        up_axis = "Y",
        apply_modifiers = True,
        export_selected_objects = True,
        export_uv = False,
        export_normals = False,
        export_colors = "NONE",
        export_attributes = False,
        export_triangulated_mesh = True,
        ascii_format = False)
    """

    with open(parameters_filename, "w") as f:
        json.dump(tree_nodes_changing_parameters, f, indent = 4)
        
