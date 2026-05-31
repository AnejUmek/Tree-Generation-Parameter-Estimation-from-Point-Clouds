import open3d as o3d
from pathlib import Path
import json
import random

dataset_path = Path(__file__).parent.parent.joinpath("dataset")
point_clouds_path = dataset_path.joinpath("point_clouds")
parameters_path = dataset_path.joinpath("parameters")

for path in [dataset_path, parameters_path, point_clouds_path]:
    if not path.exists():
        raise Exception(f"Invalid dataset, missing {path}")
    
point_cloud_filenames = [str(path) for path in list(Path.iterdir(point_clouds_path))]
point_cloud_filenames.sort()
parameters_filenames = [str(path) for path in list(Path.iterdir(parameters_path))]
parameters_filenames.sort()

max_num = len(point_cloud_filenames)

for i in random.sample(range(max_num), 10):
    point_cloud_filename = point_cloud_filenames[i]
    parameters_filename = parameters_filenames[i]

    print(point_cloud_filename.split("/")[-1])
    print(parameters_filename.split("/")[-1])

    with open(parameters_filename, "r") as f:
        params = json.load(f)
    
    print(json.dumps(params, indent=4))
    
    pcd = o3d.io.read_point_cloud(point_cloud_filename)
    pcd.paint_uniform_color([0, 1, 0])

    if pcd.has_normals():
        pcd.normals = o3d.utility.Vector3dVector([])

    o3d.visualization.draw_geometries([pcd])

    