import torch
from torch.utils.data import Dataset
from pathlib import Path
import json
import numpy as np

class PointCloudDataset(Dataset):
    def __init__(self, point_cloud_dir, parameters_dir, split, num_points = 1024):
        self.NUM_POINTS = num_points
        self.samples = []
        self.crown_shape_to_id = {
            "CYLINDRICAL": 0,
            "CONICAL": 1,
            "SPHERICAL": 2,
            "HEMISPHERICAL": 3,
            "TAPERED_CYLINDRICAL": 4,
            "INVERSE_CONICAL": 5,
            "TEND_FLAME": 6,
        }

        point_clouds_path = Path(point_cloud_dir)
        parameters_path = Path(parameters_dir)

        point_cloud_filenames = list(Path.iterdir(point_clouds_path))
        point_cloud_filenames.sort()

        parameters_filenames = list(Path.iterdir(parameters_path))
        parameters_filenames.sort()

        size = len(parameters_filenames)
        
        mean_path = Path(__file__).parent.joinpath("mean.npy")
        std_path = Path(__file__).parent.joinpath("std.npy")
        
        self.mean = np.load(mean_path).astype(np.float32)
        self.std = np.load(std_path).astype(np.float32)

        lower_limit = 0
        upper_limit = size
        if split == "train":                    # 80%
            upper_limit = round(size * 0.8)
        elif split == "val":                    # 10%
            lower_limit = round(size * 0.8)
            upper_limit = round(size * 0.9)
        elif split == "test":                   # 10%
            lower_limit = round(size * 0.9)
        else:
            raise Exception(f"Invalid split type: {split}")
        
        point_cloud_filenames = point_cloud_filenames[lower_limit:upper_limit]
        parameters_filenames = parameters_filenames[lower_limit:upper_limit]

        for point_cloud_filename, parameters_filename in zip(point_cloud_filenames, parameters_filenames):
            if point_cloud_filename.stem[3:] != parameters_filename.stem[6:]:
                raise Exception("Invalid point cloud - parameters pair")
            
            self.samples.append((point_cloud_filename, parameters_filename))
            
        
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        point_cloud_filename, parameters_filename = self.samples[idx]

        point_cloud = np.load(point_cloud_filename).astype(np.float32)
        with open(parameters_filename, "r") as f:
            params = json.load(f)
        
        num_points = point_cloud.shape[0]

        if num_points >= self.NUM_POINTS:
            idx = np.random.choice(num_points, self.NUM_POINTS, replace=False)
        else:
            idx = np.random.choice(num_points, self.NUM_POINTS, replace=True)

        point_cloud = point_cloud[idx]

        # center the points
        point_cloud = point_cloud - point_cloud.mean(axis=0)

        crown_shape = params["branches1"]["crown_shape"]
        regression = np.array([
            params["trunk"]["Length"],
            params["trunk"]["Start Radius"],
            params["branches1"]["Length"],
            params["branches1"]["Density"],
            params["branches1"]["Up Attraction"]
        ], dtype=np.float32)
        
        regression = (regression - self.mean) / self.std

        classification = self.crown_shape_to_id[crown_shape]

        point_cloud = torch.from_numpy(point_cloud).transpose(0, 1)
        label = {
            "regression" : torch.from_numpy(regression),
            "classification" : torch.tensor(classification, dtype=torch.long)
        }

        return point_cloud, label
