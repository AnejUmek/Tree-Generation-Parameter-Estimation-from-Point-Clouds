import open3d as o3d
from pathlib import Path
import json

dataset_path = Path(__file__).parent.parent.joinpath("dataset_test")
meshes_path = dataset_path.joinpath("meshes")
point_clouds_path = dataset_path.joinpath("point_clouds")
parameters_path = dataset_path.joinpath("parameters")

for path in [dataset_path, meshes_path, parameters_path, point_clouds_path]:
    if not path.exists():
        raise Exception(f"Invalid dataset, missing {path}")
    
mesh_filenames = [str(path) for path in list(Path.iterdir(meshes_path))]
mesh_filenames.sort()
point_cloud_filenames = [str(path) for path in list(Path.iterdir(point_clouds_path))]
point_cloud_filenames.sort()
parameters_filenames = [str(path) for path in list(Path.iterdir(parameters_path))]
parameters_filenames.sort()

for mesh_filename, point_cloud_filename, parameters_filename in zip(mesh_filenames, point_cloud_filenames, parameters_filenames):
    with open(parameters_filename, "r") as f:
        params = json.load(f)
    
    print(json.dumps(params, indent=4))
    
    mesh = o3d.io.read_triangle_mesh(mesh_filename)
    mesh.compute_vertex_normals()

    pcd = o3d.io.read_point_cloud(point_cloud_filename)
    pcd.paint_uniform_color([0, 1, 0])


    if pcd.has_normals():
        pcd.normals = o3d.utility.Vector3dVector([])

    o3d.visualization.draw_geometries([mesh, pcd])

    