import torch
import argparse

from pathlib import Path
from tqdm import tqdm
import numpy as np
import json

from dataset.point_cloud_dataset import PointCloudDataset
from model.pointnet2 import PointNet2, PointNet2Loss

from sklearn.metrics import confusion_matrix

def parse_args():
    parser = argparse.ArgumentParser('training')
    parser.add_argument('--use_cpu', action='store_true', default=False, help='use cpu mode')
    parser.add_argument('--dataset_path', type=str, required=True, help="Path to the dataset")
    parser.add_argument('--batch_size', type=int, default=8, help='batch size in training')
    parser.add_argument('--checkpoint', required=True, help='Load pretrained model weights')
    parser.add_argument('--num_points', type=int, default=1024, help='Point Number')
    return parser.parse_args()

def test(args):
    if args.use_cpu:
        device = torch.device("cpu")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    dataset_path = Path(args.dataset_path)
    point_cloud_path = dataset_path.joinpath("point_clouds_data")
    parameters_path = dataset_path.joinpath("parameters")
    
    test_dataset = PointCloudDataset(point_cloud_path, parameters_path, split = "test", num_points=args.num_points)
    testloader = torch.utils.data.DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=4, drop_last=False)

    model = PointNet2()

    checkpoint_path = Path(args.checkpoint)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])

    model.to(device)

    criterion = PointNet2Loss(regression_weight=0.25, classification_weight=1.0)

    model.eval()
    test_losses = {
        "total" : 0.0,
        "regression" : 0.0,
        "classification" : 0.0,
    }
    class_names = [
        "CYLINDRICAL",
        "CONICAL",
        "SPHERICAL",
        "HEMISPHERICAL",
        "TAPERED_CYLINDRICAL",
        "INVERSE_CONICAL",
        "TEND_FLAME",
    ]

    regression_names = [
        "Trunk length",
        "Trunk radius",
        "Branch length",
        "Branch density",
        "Branch up attraction",
    ]

    mean_path = Path(__file__).parent.joinpath("dataset", "mean.npy")
    std_path = Path(__file__).parent.joinpath("dataset", "std.npy")

    mean = np.load(mean_path).astype(np.float32)
    std = np.load(std_path).astype(np.float32)

    correct = 0
    total = 0

    all_prediction_classes = []
    all_target_classes = []

    regression_prediction = np.zeros((len(test_dataset), 5))
    regression_targets = np.zeros(((len(test_dataset), 5)))

    i = 0
    with torch.no_grad():
        for point_clouds, labels in tqdm(testloader, total=len(testloader)):
            point_clouds = point_clouds.to(device)
            
            batch_size = point_clouds.shape[0]

            labels["regression"] = labels["regression"].to(device)
            labels["classification"] = labels["classification"].to(device)

            outputs = model(point_clouds)
            
            loss = criterion(outputs, labels)
            for key in test_losses.keys():
                test_losses[key] += loss[key].item()

            pred_class = outputs["classification"].argmax(dim=1)
            all_prediction_classes.extend(pred_class.cpu().numpy())
            all_target_classes.extend(labels["classification"].cpu().numpy())

            correct += (pred_class == labels["classification"]).sum().item()
            total += point_clouds.shape[0]

            pred_values = outputs["regression"]
            
            regression_prediction[i:i + batch_size, :] = pred_values.cpu().numpy() * std + mean
            regression_targets[i: i + batch_size, :] = labels["regression"].cpu().numpy() * std + mean
            i += batch_size

    for key in test_losses.keys():
        test_losses[key] /= len(testloader)

    test_accuracy = correct / total
    cm = confusion_matrix(all_target_classes, all_prediction_classes, labels=list(range(len(class_names))))

    mae = np.abs(regression_prediction - regression_targets).mean(axis = 0)

    results_path = Path(__file__).parent.joinpath("results")
    if not results_path.exists():
        results_path.mkdir()

    results_file_path = results_path.joinpath(f"results_{checkpoint_path.parent.name}.json")
    
    results = {
        "checkpoint" : str(checkpoint_path),
        "losses" : {
            "total" : test_losses['total'],
            "regression": test_losses['regression'],
            "classification": test_losses['classification'],
        },
        "accuracy" : test_accuracy,
        "mae" : {parameter_name : mae_value for parameter_name, mae_value in zip(regression_names, mae)},
        "confusion matrix" : cm.tolist(),
    } 
    with open(results_file_path, "w") as f:
        json.dump(results, f, indent = 4)

if __name__ == "__main__":
    args = parse_args()
    test(args)