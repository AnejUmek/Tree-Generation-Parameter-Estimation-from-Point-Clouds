from point_cloud_dataset import PointCloudDataset

dataset = PointCloudDataset(
    "/home/anej/FRI/mag/2_letnik/2_semester/nrg/seminar/tree_parameter_estimation_from_point_cloud/dataset/point_clouds_data",
    "/home/anej/FRI/mag/2_letnik/2_semester/nrg/seminar/tree_parameter_estimation_from_point_cloud/dataset/parameters",
    split = "train",
    )

print(dataset.mean)
print(dataset.std)

print(len(dataset))

point_cloud, label = dataset.__getitem__(0)