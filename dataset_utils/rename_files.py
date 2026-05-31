from pathlib import Path

dataset_path = Path(__file__).parent.parent.joinpath("dataset")
point_clouds_path = dataset_path.joinpath("point_clouds")
parameters_path = dataset_path.joinpath("parameters")

point_cloud_filenames = [path for path in list(Path.iterdir(point_clouds_path))]
point_cloud_filenames.sort()
parameters_filenames = [path for path in list(Path.iterdir(parameters_path))]
parameters_filenames.sort()


for i, (point_cloud_filename, parameters_filename) in enumerate(zip(point_cloud_filenames, parameters_filenames)):
    point_cloud_new_filename = point_cloud_filename.parent.joinpath(f"pc{str(i + 1).zfill(6)}.ply")
    parameters_new_filename = parameters_filename.parent.joinpath(f"params{str(i + 1).zfill(6)}.json")
    
    point_cloud_filename.rename(point_cloud_new_filename)
    parameters_filename.rename(parameters_new_filename)