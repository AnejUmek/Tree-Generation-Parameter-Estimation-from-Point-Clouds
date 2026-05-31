# Tree Generation Parameter Estimation from Point Clouds

### Abstract
3D scans of the environment have become more and more common in the recent years with drones, UAVs and autonomous cars becoming more accessible. But the generated point clouds are not interpretable so they are usually transformed into some other type of data. One particular area of reconstruction is the reconstruction of vegetation or trees. 
In this paper I tackle the reconstruction of trees from an arial scan. I create a synthtic dataset of trees using Blender and simulate an aerial LiDAR scan to create their point clouds. After the creation of the dataset, PointNet++ is used to predict the most important parameters of the trees which can be used for their reconstruction. I also create a simple Blender add-on to test the capabilities of the model. On test set the model achieves great results with 98.0\% accuracy on the classification parameter, while the qualitative results show that the reconstruction of the trees from the point cloud creates similar looking trees to the original.

### Dataset
The dataset is availabe in the [here](https://drive.google.com/drive/folders/1JOrb_KYhFZtL_l2wNDouisAKmAfrwr-Q?usp=sharing), named _dataset_. You can download, extract and add it to the root folder of this project.