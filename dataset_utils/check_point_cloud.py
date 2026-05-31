import open3d as o3d
from pathlib import Path
import numpy as np

dataset_path = Path(__file__).parent.parent.joinpath("dataset")
point_clouds_path = dataset_path.joinpath("point_clouds")

point_cloud_filenames = [str(path) for path in list(Path.iterdir(point_clouds_path))]
point_cloud_filenames.sort()

for point_cloud_filename in point_cloud_filenames:
    pcd = o3d.io.read_point_cloud(point_cloud_filename)
    points = np.asarray(pcd.points)

    num_points = points.shape[0]

    if num_points < 100:
        print(point_cloud_filename)