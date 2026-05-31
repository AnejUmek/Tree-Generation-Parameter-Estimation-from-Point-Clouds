from pathlib import Path
import numpy as np
import open3d as o3d

dataset_path = Path(__file__).parent.parent.joinpath("dataset")
point_clouds_path = dataset_path.joinpath("point_clouds")

voxels_path = dataset_path.joinpath("voxels")

if not voxels_path.exists():
    voxels_path.mkdir()

point_cloud_filenames = [path for path in list(Path.iterdir(point_clouds_path))]
point_cloud_filenames.sort()

size_x_z = 30
size_y = 60
num_voxels_x_z = 128
num_voxels_y = 256

half_size_x_z = size_x_z / 2

bins_x_z = np.linspace(-half_size_x_z, half_size_x_z, num_voxels_x_z)
bins_y = np.linspace(0, size_y, num_voxels_y)

for point_cloud_filename in point_cloud_filenames:
    number = int((point_cloud_filename.stem)[2:])
    voxel_filename = voxels_path.joinpath(f"vox{str(number).zfill(6)}.npz")

    pcd = o3d.io.read_point_cloud(point_cloud_filename)
    points = np.asarray(pcd.points)
    histogram, _ = np.histogramdd(points, bins=(bins_x_z, bins_y, bins_x_z))
    histogram = histogram.astype(np.uint8)
    # flipping y axis so the zero coordinate is at the bottom right corner
    histogram = histogram[:, ::-1, :]
    # np.save(voxel_filename, histogram)
    np.savez_compressed(voxel_filename, histogram)