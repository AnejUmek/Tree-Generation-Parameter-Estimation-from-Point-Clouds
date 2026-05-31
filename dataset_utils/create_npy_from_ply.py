from pathlib import Path
import numpy as np
import open3d as o3d

dataset_path = Path(__file__).parent.parent.joinpath("dataset")
point_clouds_path = dataset_path.joinpath("point_clouds")

point_clouds_data_path = dataset_path.joinpath("point_clouds_data")

if not point_clouds_data_path.exists():
    point_clouds_data_path.mkdir()

point_cloud_filenames = [path for path in list(Path.iterdir(point_clouds_path))]
point_cloud_filenames.sort()

for point_cloud_filename in point_cloud_filenames:
    number = int((point_cloud_filename.stem)[2:])
    point_cloud_data_filename = point_clouds_data_path.joinpath(f"pcd{str(number).zfill(6)}.npy")

    pcd = o3d.io.read_point_cloud(point_cloud_filename)
    points = np.asarray(pcd.points, dtype=np.float32)

    np.save(point_cloud_data_filename, points)